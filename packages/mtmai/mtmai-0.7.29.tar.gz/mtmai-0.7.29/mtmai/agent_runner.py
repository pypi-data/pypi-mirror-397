import asyncio
import logging
import json
from typing import Dict, Any, List, cast

from fastuuid import uuid4
from supabase import AsyncClient

from mtmai.clients.supabase import get_supabase_async
from mtmai.agents.simple_chat.agent import chat_agent
from mtmai.models.chat_v2 import ChatMessage
from google.adk.runners import Runner
from mtmai.adk.session_service import MtAdkSessionService
from google.genai import types


logger = logging.getLogger(__name__)


class AgentRunner:
    def __init__(self, base_url: str, sb: AsyncClient):
        self.base_url = base_url
        self.sb = sb
        self.session_service = MtAdkSessionService(base_url=base_url)

    async def get_chat_history(self, chat_id: str) -> str:
        """从 Supabase 获取最近聊天记录并格式化为字符串"""
        try:
            # 调用 SQL 函数: chat_message_list(p_chat_id uuid)
            # 注意: 该函数不接受 limit 参数，我们获取全部后在内存截取
            response = await self.sb.rpc(
                "chat_message_list", {"p_chat_id": chat_id}
            ).execute()

            # 显式类型转换，消除 JSON 类型的歧义
            rows = cast(List[Dict[str, Any]], response.data)

            if not rows:
                return "(No history)"

            # 在内存中处理 Limit (取最后 20 条)
            # 假设 DB 返回的是按时间正序 (ASC) 排列的
            limit = 20
            if len(rows) > limit:
                rows = rows[-limit:]

            messages = [ChatMessage(**row) for row in rows]

            formatted_history = []
            for msg in messages:
                # 拼接格式: "user: hello"
                # 过滤系统消息或无效内容
                if msg.text_content:
                    formatted_history.append(f"{msg.role}: {msg.text_content}")

            return "\n".join(formatted_history)

        except Exception as e:
            logger.error(f"Failed to fetch history: {e}")
            return "(Error fetching history)"

    async def run_chat_agent(self, payload: Dict[str, Any]):
        """运行 Chat Agent"""
        chat_id = payload.get("chat_id")
        # 强制指定 User ID，确保权限一致
        user_id = "3714c15c-f3e3-419c-b178-abba2a2fd994"

        if not chat_id:
            logger.error("Payload missing chat_id")
            return

        logger.info(f"🏃 [Runner] Starting for Chat {chat_id}")

        # 1. 获取历史记录文本
        history_text = await self.get_chat_history(chat_id)

        # 2. 初始化 Agent
        root_agent = chat_agent()

        # 3. 使用 chat_id 作为 Session ID，确保记忆连续性
        adk_session_id = chat_id

        # 4. 创建 Session 并注入 State
        # ADK 会自动将 instruction 中的 {history_text} 替换为 state["history_text"] 的值
        await self.session_service.create_session(
            app_name=root_agent.name,
            user_id=user_id,
            session_id=adk_session_id,
            state={
                "mtgate_api_base_url": self.base_url,
                "chat_id": chat_id,
                "history_text": history_text,
                "target_user_id": user_id,
            },
        )

        runner = Runner(
            agent=root_agent,
            app_name=root_agent.name,
            session_service=self.session_service,
        )

        try:
            logger.info("🤖 [Runner] Invoking Agent...")
            async for event in runner.run_async(
                user_id=user_id,
                session_id=adk_session_id,
                new_message=types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            text="有新的用户提交的聊天消息,现在请你给用户做出正确的回复",
                        )
                    ],
                ),
            ):
                # Print final output (either from LLM or callback override)
                if event.is_final_response() and event.content:
                    # print(f"Final Output: [{event.author}] {event.content.parts[0].text.strip()}")
                    ...
                elif event.error_message is not None:
                    logger.error(f"agent error event: {event.error_message}")
                # 记录思考过程 (Debug用)
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            # 简单的日志截断，避免刷屏
                            clean_text = part.text.replace("\n", " ")
                            if len(clean_text) > 100:
                                logger.debug(f"[Thinking]: {clean_text[:100]}...")
                            else:
                                logger.debug(f"[Thinking]: {clean_text}")

        except Exception as e:
            logger.error(f"❌ Agent execution failed: {e}", exc_info=True)


async def get_agent_runner(base_url: str) -> AgentRunner:
    sb = await get_supabase_async()
    return AgentRunner(base_url, sb)
