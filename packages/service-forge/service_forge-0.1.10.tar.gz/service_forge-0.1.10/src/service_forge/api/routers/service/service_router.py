from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from loguru import logger
from typing import Optional, TYPE_CHECKING
import tempfile
import os
from pydantic import BaseModel
from omegaconf import OmegaConf

if TYPE_CHECKING:
    from service_forge.service import Service

# TODO: refactor this, do not use global variable
_current_service: Optional['Service'] = None

def set_service(service: 'Service') -> None:
    global _current_service
    _current_service = service

def get_service() -> Optional['Service']:
    return _current_service

service_router = APIRouter(prefix="/sdk/service", tags=["service"])

class WorkflowStatusResponse(BaseModel):
    name: str
    version: str
    description: str
    workflows: list[dict]

class WorkflowActionResponse(BaseModel):
    success: bool
    message: str

@service_router.get("/status", response_model=WorkflowStatusResponse)
async def get_service_status():
    service = get_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        status = service.get_service_status()
        return status
    except Exception as e:
        logger.error(f"Error getting service status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@service_router.post("/workflow/{workflow_name}/start", response_model=WorkflowActionResponse)
async def start_workflow(workflow_name: str):
    service = get_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        success = await service.start_workflow(workflow_name)
        if success:
            return WorkflowActionResponse(success=True, message=f"Workflow {workflow_name} started successfully")
        else:
            return WorkflowActionResponse(success=False, message=f"Failed to start workflow {workflow_name}")
    except Exception as e:
        logger.error(f"Error starting workflow {workflow_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@service_router.post("/workflow/{workflow_name}/stop", response_model=WorkflowActionResponse)
async def stop_workflow(workflow_name: str):
    service = get_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        success = await service.stop_workflow(workflow_name)
        if success:
            return WorkflowActionResponse(success=True, message=f"Workflow {workflow_name} stopped successfully")
        else:
            return WorkflowActionResponse(success=False, message=f"Failed to stop workflow {workflow_name}")
    except Exception as e:
        logger.error(f"Error stopping workflow {workflow_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@service_router.post("/workflow/upload", response_model=WorkflowActionResponse)
async def upload_workflow_config(
    file: Optional[UploadFile] = File(None),
    config_content: Optional[str] = Form(None),
    workflow_name: Optional[str] = Form(None)
):
    service = get_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    if file is None and config_content is None:
        raise HTTPException(status_code=400, detail="Either file or config_content must be provided")
    
    if file is not None and config_content is not None:
        raise HTTPException(status_code=400, detail="Cannot provide both file and config_content")
    
    temp_file_path = None
    try:
        if file is not None:
            if not file.filename or not file.filename.endswith(('.yaml', '.yml')):
                raise HTTPException(status_code=400, detail="Only YAML files are supported")
            
            suffix = '.yaml' if file.filename.endswith('.yaml') else '.yml'
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=suffix) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            success = await service.load_workflow_from_config(config_path=temp_file_path, workflow_name=workflow_name)
        else:
            try:
                config = OmegaConf.to_object(OmegaConf.create(config_content))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid YAML format: {str(e)}")
            
            success = await service.load_workflow_from_config(config=config, workflow_name=workflow_name)
        
        if success:
            return WorkflowActionResponse(
                success=True,
                message=f"Workflow configuration uploaded and loaded successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to load workflow configuration")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading workflow config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_file_path}: {e}")

