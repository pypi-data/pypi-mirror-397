from __future__ import annotations

import os
import asyncio
import threading
from omegaconf import OmegaConf
from service_forge.workflow.node import node_register
from service_forge.workflow.workflow_factory import create_workflows
from service_forge.api.http_api import start_fastapi_server
from service_forge.api.kafka_api import start_kafka_server
from service_forge.db.database import DatabaseManager
from loguru import logger
from typing import Callable, AsyncIterator, Awaitable, Any, TYPE_CHECKING
from service_forge.api.http_api_doc import generate_service_http_api_doc
from service_forge.api.routers.service.service_router import set_service
from service_forge.sft.config.sf_metadata import SfMetadata

if TYPE_CHECKING:
    from service_forge.workflow.workflow_group import WorkflowGroup

class Service:
    def __init__(
        self,
        metadata: SfMetadata,
        config_path: str,
        workflow_config_paths: list[str],
        _handle_stream_output: Callable[[str, AsyncIterator[str]], Awaitable[None]] = None,
        _handle_query_user: Callable[[str, str], Awaitable[str]] = None,
        enable_http: bool = True,
        http_host: str = "0.0.0.0",
        http_port: int = 8000,
        enable_kafka: bool = True,
        kafka_host: str = "localhost",
        kafka_port: int = 9092,
        service_env: dict[str, Any] = None,
        database_manager: DatabaseManager = None,
    ) -> None:
        self.metadata = metadata
        self.config_path = config_path
        self.workflow_config_paths = workflow_config_paths
        self._handle_stream_output = _handle_stream_output
        self._handle_query_user = _handle_query_user
        self.enable_http = enable_http
        self.http_host = http_host
        self.http_port = http_port
        self.enable_kafka = enable_kafka
        self.kafka_host = kafka_host
        self.kafka_port = kafka_port
        self.service_env = {} if service_env is None else service_env
        self.database_manager = database_manager
        self.workflow_groups: list[WorkflowGroup] = []
        self.workflow_tasks: dict[str, asyncio.Task] = {}  # workflow_name -> task mapping
        self.workflow_config_map: dict[str, str] = {}  # workflow_name -> config_path mapping
        self.fastapi_thread: threading.Thread | None = None
        self.fastapi_loop: asyncio.AbstractEventLoop | None = None

    @property
    def name(self) -> str:
        return self.metadata.name
    
    @property
    def version(self) -> str:
        return self.metadata.version
    
    @property
    def description(self) -> str:
        return self.metadata.description

    async def start(self):
        set_service(self)
        
        if self.enable_http:
            fastapi_task = asyncio.create_task(start_fastapi_server(self.http_host, self.http_port))
            doc_task = asyncio.create_task(generate_service_http_api_doc(self))
        else:
            fastapi_task = None
            doc_task = None
        if self.enable_kafka:
            kafka_task = asyncio.create_task(start_kafka_server(f"{self.kafka_host}:{self.kafka_port}"))
        else:
            kafka_task = None

        workflow_tasks: list[asyncio.Task] = []

        for workflow_config_path in self.workflow_config_paths:
            workflow_group = create_workflows(
                self.parse_workflow_path(workflow_config_path),
                service_env=self.service_env,
                _handle_stream_output=self._handle_stream_output, 
                _handle_query_user=self._handle_query_user,
                database_manager=self.database_manager,
            )
            self.workflow_groups.append(workflow_group)
            main_workflow = workflow_group.get_main_workflow()
            task = asyncio.create_task(workflow_group.run())
            workflow_tasks.append(task)
            self.workflow_tasks[main_workflow.name] = task
            self.workflow_config_map[main_workflow.name] = workflow_config_path

        try:
            core_tasks = []
            if fastapi_task:
                core_tasks.append(fastapi_task)
            if doc_task:
                core_tasks.append(doc_task)
            if kafka_task:
                core_tasks.append(kafka_task)
            
            all_tasks = core_tasks + workflow_tasks
            results = await asyncio.gather(*all_tasks, return_exceptions=True)
            
            # Check core tasks
            for i, result in enumerate(results[:len(core_tasks)]):
                if isinstance(result, Exception):
                    logger.error(f"Error in service {self.name} core task {i}: {result}")
                    raise result
            
            # Check workflow tasks
            for i, result in enumerate(results[len(core_tasks):], start=len(core_tasks)):
                if isinstance(result, Exception) and not isinstance(result, asyncio.CancelledError):
                    # Workflow task exception should not stop the service
                    logger.error(f"Error in service {self.name} workflow task {i}: {result}")

        except Exception as e:
            logger.error(f"Error in service {self.name}: {e}")
            if fastapi_task:
                fastapi_task.cancel()
            if kafka_task:
                kafka_task.cancel()
            for workflow_task in workflow_tasks:
                workflow_task.cancel()
            raise

    def parse_workflow_path(self, workflow_config_path: str) -> str:
        if os.path.isabs(workflow_config_path):
            return workflow_config_path
        else:
            return os.path.join(os.path.dirname(self.config_path), workflow_config_path)
    
    def get_workflow_group_by_name(self, workflow_name: str) -> WorkflowGroup | None:
        for workflow_group in self.workflow_groups:
            if workflow_group.get_workflow(workflow_name) is not None:
                return workflow_group
        return None
    
    def trigger_workflow(self, workflow_name: str, trigger_name: str, **kwargs) -> uuid.UUID:
        workflow_group = self.get_workflow_group_by_name(workflow_name)
        if workflow_group is None:
            logger.error(f"Workflow {workflow_name} not found")
            return False
        
        workflow = workflow_group.get_main_workflow()
        if workflow is None:
            logger.error(f"Workflow {workflow_name} not found")
            return False

        return workflow.trigger(trigger_name, **kwargs)

    async def start_workflow(self, workflow_name: str) -> bool:
        if workflow_name in self.workflow_tasks:
            task = self.workflow_tasks[workflow_name]
            if not task.done():
                logger.warning(f"Workflow {workflow_name} is already running")
                return False
            del self.workflow_tasks[workflow_name]
        
        workflow_group = self.get_workflow_group_by_name(workflow_name)
        if workflow_group is None:
            logger.error(f"Workflow {workflow_name} not found")
            return False
        
        task = asyncio.create_task(workflow_group.run(workflow_name))
        self.workflow_tasks[workflow_name] = task
        logger.info(f"Started workflow {workflow_name}")
        return True
    
    async def stop_workflow(self, workflow_name: str) -> bool:
        if workflow_name not in self.workflow_tasks:
            logger.warning(f"Workflow {workflow_name} is not running")
            return False
        
        task = self.workflow_tasks[workflow_name]
        if task.done():
            logger.warning(f"Workflow {workflow_name} is already stopped")
            del self.workflow_tasks[workflow_name]
            return False
        
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        del self.workflow_tasks[workflow_name]
        logger.info(f"Stopped workflow {workflow_name}")
        return True
    
    async def load_workflow_from_config(self, config_path: str = None, config: dict = None, workflow_name: str = None) -> bool:
        try:
            if config is None:
                if config_path is None:
                    raise ValueError("Either config_path or config must be provided")
                if os.path.isabs(config_path):
                    full_path = config_path
                else:
                    full_path = self.parse_workflow_path(config_path)
                workflow_group = create_workflows(
                    config_path=full_path,
                    service_env=self.service_env,
                    _handle_stream_output=self._handle_stream_output,
                    _handle_query_user=self._handle_query_user,
                    database_manager=self.database_manager,
                )
                config_identifier = config_path
            else:
                workflow_group = create_workflows(
                    config=config,
                    service_env=self.service_env,
                    _handle_stream_output=self._handle_stream_output,
                    _handle_query_user=self._handle_query_user,
                    database_manager=self.database_manager,
                )
                config_identifier = config_path if config_path else "config_dict"
            
            self.workflow_groups.append(workflow_group)
            main_workflow = workflow_group.get_main_workflow()
            actual_name = workflow_name if workflow_name else main_workflow.name
            
            if workflow_name and workflow_name != main_workflow.name:
                actual_name = main_workflow.name
            
            if actual_name in self.workflow_tasks:
                await self.stop_workflow(actual_name)
            
            task = asyncio.create_task(workflow_group.run(actual_name))
            self.workflow_tasks[actual_name] = task
            self.workflow_config_map[actual_name] = config_identifier
            
            logger.info(f"Loaded and started workflow {actual_name} from {config_identifier}")
            return True
        except Exception as e:
            logger.error(f"Failed to load workflow from {config_path or 'config_dict'}: {e}")
            return False
    
    def get_service_status(self) -> dict[str, Any]:
        workflow_statuses = []
        for workflow_group in self.workflow_groups:
            for workflow in workflow_group.workflows:
                workflow_name = workflow.name
                is_running = workflow_name in self.workflow_tasks and not self.workflow_tasks[workflow_name].done()
                config_path = self.workflow_config_map.get(workflow_name, "unknown")
                workflow_statuses.append({
                    "name": workflow_name,
                    "description": workflow.description,
                    "status": "running" if is_running else "stopped",
                    "config_path": config_path,
                })
        
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "workflows": workflow_statuses,
        }
    
    @staticmethod
    def from_config(metadata, service_env: dict[str, Any] = None) -> Service:
        config = OmegaConf.to_object(OmegaConf.load(metadata.service_config))
        database_manager = DatabaseManager.from_config(config=config)
        return Service(
            metadata=metadata,
            config_path=metadata.service_config,
            workflow_config_paths=config.get('workflows', []),
            _handle_stream_output=None,
            _handle_query_user=None,
            enable_http=config.get('enable_http', True),
            http_host=config.get('http_host', '0.0.0.0'),
            http_port=config.get('http_port', 8000),
            enable_kafka=config.get('enable_kafka', True),
            kafka_host=config.get('kafka_host', 'localhost'),
            kafka_port=config.get('kafka_port', 9092),
            service_env=service_env,
            database_manager=database_manager,
        )

def create_service(config_path: str, name: str, version: str, service_env: dict[str, Any] = None) -> Service:
    return Service.from_config(config_path, name, version, service_env)
