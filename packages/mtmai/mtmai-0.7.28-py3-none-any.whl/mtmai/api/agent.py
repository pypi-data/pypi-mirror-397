import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.utils.context_utils import Aclosing

from mtmai.adk.session_service import MtAdkSessionService
from mtmai.cli.adk_web_server import RunAgentRequest
from mtmai.clients.rest.models.agent_runner_input import AgentRunnerInput

# from mtmai.deps import AdkSessionDep
from mtmai.flows import flow_agent_runner
from mtmai.hatchet_client import hatchet

router = APIRouter()

# 开关: 是否已工作流的方式运行(以后考虑)
run_with_wf = False
logger = logging.getLogger("mtmai_api." + __name__)


@router.post("/agent_run", include_in_schema=True)
async def agentrun(
    req: RunAgentRequest,
) -> StreamingResponse:
    logger.info("agent_run in python")
    adk_session_api_base_url = "http://localhost:3700"
    adkSession = MtAdkSessionService(
        base_url=adk_session_api_base_url, access_token=None
    )
    if run_with_wf:
        ref = flow_agent_runner.agent_runner_workflow.run_no_wait(
            input=AgentRunnerInput()
        )

        return StreamingResponse(
            hatchet.runs.subscribe_to_stream(ref.workflow_run_id),
            media_type="text/plain",
        )
    # print(adkSession)
    # SSE endpoint
    session = await adkSession.get_session(
        app_name=req.app_name, user_id=req.user_id, session_id=req.session_id
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    # from mtmai.agents.langchat import root_agent
    from mtmai.agents.simple_chat.agent import root_agent

    # root_agent = langchat_agent
    # # Convert the events to properly formatted SSE
    async def event_generator():
        try:
            stream_mode = StreamingMode.SSE if req.streaming else StreamingMode.NONE
            runner = Runner(
                app_name=req.app_name,
                agent=root_agent,
                # artifact_service=self.artifact_service,
                session_service=adkSession,
                # memory_service=self.memory_service,
                # credential_service=self.credential_service,
            )
            async with Aclosing(
                runner.run_async(
                    user_id=req.user_id,
                    session_id=req.session_id,
                    new_message=req.new_message,
                    state_delta=req.state_delta,
                    run_config=RunConfig(streaming_mode=stream_mode),
                )
            ) as agen:
                async for event in agen:
                    # Format as SSE data
                    sse_event = event.model_dump_json(exclude_none=True, by_alias=True)
                    logger.debug(
                        "Generated event in agent run streaming: %s", sse_event
                    )
                    yield f"data: {sse_event}\n\n"
        except Exception as e:
            logger.exception("Error in event_generator: %s", e)
            # You might want to yield an error event here
            yield f'data: {{"error": "{str(e)}"}}\n\n'

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
