import logging
from datetime import timedelta

from google.genai import types  # noqa: F401
from hatchet_sdk import Context, SleepCondition

from mtmai.clients.rest.models.agent_runner_input import AgentRunnerInput
from mtmai.clients.rest.models.agent_runner_output import AgentRunnerOutput
from mtmai.hatchet_client import hatchet

logger = logging.getLogger(__name__)

agent_runner_workflow = hatchet.workflow(
    name="agent_update", input_validator=AgentRunnerInput
)


@agent_runner_workflow.task()
async def start(input: AgentRunnerInput, ctx: Context) -> AgentRunnerOutput:
    logger.info("开始执行 AgentRunnerWorkflow")
    return AgentRunnerOutput(
        content="hello1 result",
    )


@agent_runner_workflow.task(
    parents=[start],
    wait_for=[
        SleepCondition(
            timedelta(seconds=1),
        )
    ],
)
async def wait_for_sleep(input, ctx: Context) -> dict:
    logger.info("到达 wait_for_sleep")
    return {"步骤2": input}
