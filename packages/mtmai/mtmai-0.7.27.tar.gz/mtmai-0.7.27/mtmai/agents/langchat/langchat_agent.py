from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

from mtmai.model_client import get_default_litellm_model

# 使用在线的 mtgate mcp 工具
mcp_toolset = MCPToolset(
    connection_params=SseConnectionParams(
        url="https://mtgate.yuepa8.com/api/cf/mcp/sse",
        # 目前 mtgate mcp 工具无须认证
        # headers={"Authorization": "Bearer $(gcloud auth print-access-token)"},
    ),
)


def new_instagram_agent():
    return Agent(
        model=get_default_litellm_model(),
        name="instagram_agent",
        description="跟 instagram 社交媒体操作的专家",
        instruction="你是有用的助理,乐于回答用户问题. 必须使用中文回答.",
        # instruction=get_instagram_instructions(),
        tools=[
            mcp_toolset,
            # 可以添加本地工具,或者更多的mcp 工具.
            # instagram_login,
            # # instagram_write_post,
            # instagram_account_info,
            # instagram_follow_user,
        ],
        # after_tool_callback=after_tool_callback,
        # before_agent_callback=before_agent_callback,
        # before_model_callback=before_model_callback,
        output_key="langchata_agent_output",
    )


root_agent = new_instagram_agent()
