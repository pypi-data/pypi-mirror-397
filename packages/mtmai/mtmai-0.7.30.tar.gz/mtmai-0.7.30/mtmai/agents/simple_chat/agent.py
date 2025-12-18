import logging
from textwrap import dedent
from typing import Any, Dict, Optional
import uuid

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.utils import instructions_utils
from google.adk.code_executors import BuiltInCodeExecutor
from datetime import datetime

from mtmai.clients.supabase import get_supabase_async
from mtmai.model_client import get_default_litellm_model

logger = logging.getLogger(__name__)


async def reply_to_user_tool(
    reply_text: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """
    专用于回复用户的工具。当你想对用户说任何话时，必须使用此工具。
    不要直接在思维链中结束，必须调用此工具才算回复完成。

    Args:
        reply_text: 回复给用户的具体文本内容。
    """
    # 1. 获取上下文
    chat_id = tool_context.state.get("chat_id")
    target_user_id = tool_context.state.get("target_user_id")

    if not chat_id:
        return {"status": "error", "message": "Missing chat_id in session state"}
    if not target_user_id:
        logger.error("Missing target_user_id. The AI reply will belong to no one!")
        return {"status": "error", "message": "Missing target_user_id in session state"}

    logger.info(f"🤖 [Tool] Replying to Chat: {chat_id}, User: {target_user_id}")

    sb = await get_supabase_async()

    try:
        # 注意: parts json 格式,使用的是 vercel aisdk UIMessage中的格式, 因为前端用的是 vercel "ai"这个包.
        parts_json = [{"text": reply_text, "type": "text"}]
        msg_id = str(uuid.uuid4())

        rpc_params = {
            "p_chat_id": chat_id,
            "p_id": msg_id,
            "p_parts": parts_json,
            "p_role": "assistant",
            "p_attachments": [],
            "p_user_id": target_user_id,
        }

        await sb.rpc("chat_message_upsert", rpc_params).execute()
        # logger.info(f"✅ [Tool] Reply persisted. DB Response: {response.data}")
        return {
            "status": "success",
            "result": "Reply sent successfully.",
            "message_id": msg_id,
        }

    except Exception as e:
        logger.error(f"❌ [Tool] Failed to persist reply: {e}", exc_info=True)
        return {"status": "error", "message": f"Database error: {str(e)}"}


def before_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """钩子: 暂时留空"""
    # Add new state
    callback_context.state["temp:last_operation_status"] = "success"
    now = datetime.now()

    # 格式化为字符串 (例如: 2025-12-12 14:30:00)
    callback_context.state["current_datetime"] = now.strftime("%Y-%m-%d %H:%M:%S")


def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """显示必要的日志"""
    # agent_name = callback_context.agent_name
    # history_text = callback_context.state.get("history_text")
    logger.info(f"llm request {llm_request}")

    # Inspect the last user message in the request contents
    # last_user_message = ""
    # if llm_request.contents and llm_request.contents[-1].role == "user":
    #     if llm_request.contents[-1].parts:
    #         last_user_message = llm_request.contents[-1].parts[0].text
    # print(f"[Callback] Inspecting last user message: '{last_user_message}'")


# This is an InstructionProvider
async def instruction_provider(context: ReadonlyContext) -> str:
    # TODO: 将聊天历史,和用户最新输入的 状态做正确区分.
    # TODO: 添加和完善基础上下文资料,例如当前时间,基本环境, 让 ai agent 回复用户或者处理相关任务有更多的依据.
    template = dedent("""
        <instruction>
        你是一个智能客服专员。
        用户当前在聊天页面输入了消息。

        你的任务是：
        1. 阅读 <chat_history> 中的上下文。
        2. 理解用户的最新意图。
        3. 必须调用 [reply_to_user_tool] 工具来回复用户。
        4. 语气要亲切、专业。

        其他提示:
        1. 聊天历史列表的最后一个user消息,最新输入的聊天消息.
        2. 你拥有python代码执行能力,当运行复杂任务是,应当考虑运行python程序辅助进行思考和解决问题.
        </instruction>

        <base_info>
        current_datetime: {{current_datetime}}
        </base_info>

        <tools_usage>
        你必须使用 reply_to_user_tool 进行回复。不要直接输出文本。
        </tools_usage>

        <chat_history>
        {{history_text}}
        </chat_history>

        <last_user_message>
        last_user_message
        </last_user_message>


        """)
    return await instructions_utils.inject_session_state(template, context)


def chat_agent():
    """创建 Agent 实例"""
    model = get_default_litellm_model("qwen2.5-coder-32b-instruct")
    root_agent = Agent(
        name="assistant",
        model=model,
        instruction=instruction_provider,
        description="An AI assistant",
        tools=[reply_to_user_tool],
        before_agent_callback=before_agent_callback,
        before_model_callback=before_model_callback,
        code_executor=BuiltInCodeExecutor(),
    )
    return root_agent
