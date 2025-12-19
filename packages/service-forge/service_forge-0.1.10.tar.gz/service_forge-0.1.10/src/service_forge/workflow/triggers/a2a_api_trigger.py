from __future__ import annotations
from loguru import logger
from service_forge.workflow.trigger import Trigger
from typing import AsyncIterator, Any
from service_forge.workflow.port import Port
from google.protobuf.message import Message
from google.protobuf.json_format import MessageToJson
from fastapi import FastAPI
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.utils.constants import DEFAULT_RPC_URL, EXTENDED_AGENT_CARD_PATH, AGENT_CARD_WELL_KNOWN_PATH

# --8<-- [start:HelloWorldAgent]
class HelloWorldAgent:
    """Hello World Agent."""

    async def invoke(self) -> str:
        return 'Hello World'


# --8<-- [end:HelloWorldAgent]


# --8<-- [start:HelloWorldAgentExecutor_init]
class HelloWorldAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self):
        self.agent = HelloWorldAgent()

    # --8<-- [end:HelloWorldAgentExecutor_init]
    # --8<-- [start:HelloWorldAgentExecutor_execute]
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        result = await self.agent.invoke()
        await event_queue.enqueue_event(new_agent_text_message(result))

    # --8<-- [end:HelloWorldAgentExecutor_execute]

    # --8<-- [start:HelloWorldAgentExecutor_cancel]
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')

    # --8<-- [end:HelloWorldAgentExecutor_cancel]



class A2AAPITrigger(Trigger):
    DEFAULT_INPUT_PORTS = [
        Port("app", FastAPI),
    ]

    DEFAULT_OUTPUT_PORTS = [
        Port("trigger", bool),
        Port("data", Any),
    ]

    def __init__(self, name: str):
        super().__init__(name)
        self.events = {}
        self.is_setup_handler = False
        self.agent_card: AgentCard | None = None

    @staticmethod
    def serialize_result(result: Any):
        if isinstance(result, Message):
            return MessageToJson(
                result,
                preserving_proto_field_name=True
            )
        return result

    def _setup_handler(self, app: FastAPI) -> None:
        skill = AgentSkill(
            id='hello_world',
            name='Returns hello world',
            description='just returns hello world',
            tags=['hello world'],
            examples=['hi', 'hello world'],
        )

        agent_card = AgentCard(
            name='Hello World Agent',
            description='Just a hello world agent',
            url='http://localhost:37200/a2a/',
            version='1.0.0',
            default_input_modes=['text'],
            default_output_modes=['text'],
            capabilities=AgentCapabilities(streaming=True),
            skills=[skill],
            supports_authenticated_extended_card=False,
        )
        
        # Store agent_card for documentation generation
        self.agent_card = agent_card

        request_handler = DefaultRequestHandler(
            agent_executor=HelloWorldAgentExecutor(),
            task_store=InMemoryTaskStore(),
        )

        try:
            server = A2AStarletteApplication(
                agent_card=agent_card,
                http_handler=request_handler,
            )
            
            server.add_routes_to_app(
                app,
                agent_card_url="/a2a" + AGENT_CARD_WELL_KNOWN_PATH,
                rpc_url="/a2a" + DEFAULT_RPC_URL,
                extended_agent_card_url="/a2a" + EXTENDED_AGENT_CARD_PATH,
            )
        except Exception as e:
            logger.error(f"Error adding A2A routes: {e}")
            raise

    async def _run(self, app: FastAPI) -> AsyncIterator[bool]:
        print("RUN")
        if not self.is_setup_handler:
            self._setup_handler(app)
            self.is_setup_handler = True

        while True:
            try:
                trigger = await self.trigger_queue.get()
                self.prepare_output_edges(self.get_output_port_by_name('data'), trigger['data'])
                yield self.trigger(trigger['id'])
            except Exception as e:
                logger.error(f"Error in A2AAPITrigger._run: {e}")
                continue

