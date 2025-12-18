from typing import Optional
from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from mtmai.clients.mtgate_api.api.sandboxes import sandbox_list
from mtmai.clients.mtgate_api.models.sandbox_list_response_200 import (
    SandboxListResponse200,
)
from mtmai.clients.mtgateclient import create_mtgate_client
import logging
from google.adk.agents.callback_context import CallbackContext

logger = logging.getLogger(__name__)


async def list_sandbox_configs(query: str, tool_context: ToolContext):
    async with await create_mtgate_client() as mtgateclient:
        detailed_response = await sandbox_list.asyncio_detailed(
            client=mtgateclient._client,
            limit=100,
            offset=0,
        )

        if detailed_response.status_code != 200:
            logger.error(f"API调用失败，状态码: {detailed_response.status_code}")
            if detailed_response.content:
                logger.error(f"响应内容: {detailed_response.content}")
        if isinstance(detailed_response.parsed, SandboxListResponse200):
            return detailed_response.parsed.to_dict()
        return "查询失败"


# --- 1. Define the Callback Function ---
def check_if_agent_should_run(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """
    Logs entry and checks 'skip_llm_agent' in session state.
    If True, returns Content to skip the agent's execution.
    If False or not present, returns None to allow execution.
    """
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    print(f"\n[Callback] Entering agent: {agent_name} (Inv: {invocation_id})")
    print(f"[Callback] Current State: {current_state}")

    # Check the condition in session state dictionary
    if current_state.get("skip_llm_agent", False):
        print(
            f"[Callback] State condition 'skip_llm_agent=True' met: Skipping agent {agent_name}."
        )
        # Return Content to skip the agent's run
        return types.Content(
            parts=[
                types.Part(
                    text=f"Agent {agent_name} skipped by before_agent_callback due to state."
                )
            ],
            role="model",  # Assign model role to the overriding response
        )
    else:
        print(
            f"[Callback] State condition not met: Proceeding with agent {agent_name}."
        )
        # Return None to allow the LlmAgent's normal execution
        return None


root_agent = Agent(
    model="gemini-2.0-flash",
    name="sandbox_agent",
    description=("sandbox 管理agent"),
    instruction="""
      你是专用的sandbox 管理专家.
      你可以调用 list_sandbox_configs 工具, 获取 sandbox 列表.
    """,
    tools=[
        list_sandbox_configs,
        # check_prime,
    ],
    # planner=BuiltInPlanner(
    #     thinking_config=types.ThinkingConfig(
    #         include_thoughts=True,
    #     ),
    # ),
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # avoid false alarm about rolling dice.
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
    before_agent_callback=check_if_agent_should_run,  # Assign the callback
)
