import logging
from typing import Dict, Any

from google.adk.runners import Runner
from mtmai.agents.simple_chat.agent import chat_agent
from mtmai.adk.session_service import MtAdkSessionService
from mtmai.mtgateapi.mtgate_client.client import Client

logger = logging.getLogger("agent_runner")

_runner_service = None


class AgentRunnerService:
    """
    主要功能: 构建 agent runner 跟 并根据策略执行 ai agent
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session_service = MtAdkSessionService(base_url=base_url)
        self.client = Client(base_url=base_url)
        self.client.raise_on_unexpected_status = True

    async def run_chat_agent(self, payload: Dict[str, Any]):
        try:
            chat_id = payload.get("chat_id")
            user_id = payload.get("user_id")

            if not chat_id or not user_id:
                logger.error(f"Invalid payload: {payload}")
                return

            logger.info(f"🤖 AgentRunner: Starting for ChatID: {chat_id}")
            # 提示: 对于每一个新的消息都应当启动一个新的上下文.
            root_agent = chat_agent()
            await self.session_service.create_session(
                app_name=root_agent.name,
                user_id=user_id,
                session_id=chat_id,
                # 初始化状态, state 是agent的关键状态, 决定了智能体的行为.
                state={
                    # "datetime":  # 传入当前时间
                    "mtgate_api_base_url": self.base_url,
                    # "counter": 1,  # 仅作演示,没实际用途
                    # TODO: 传入更多可能 state 值为智能体提供更多有用的上下文.
                },
            )

            runner = Runner(
                agent=root_agent,
                app_name=root_agent.name,
                session_service=self.session_service,
            )

            async for event in runner.run_async(
                user_id=user_id,
                session_id=chat_id,
                # 每一个新的 agent 运行,内部都会根据实际情况构建上下文, 所以这里没有必要传入 new_message
                # new_message=types.Content(
                #     role="user",
                #     parts=[
                #         types.Part(
                #             # 用户的聊天消息,应当作为智能体内部的上下文进行构建.
                #             # 聊天历史的获取, 应当属于 agent 内部的事情, 简单的说,应该是 agent 内部初始化的时候,主动从数据库获取完整的上下文.
                #             text="你是智能客服系统, 请积极使用你现有的工具库, 获取相关用户的聊天历史,并给出合适的回复."
                #         )
                #     ],
                # ),
            ):
                # 提示: agent 运行输出的最终结果已经不再重要, 因为 ai agent 对于回复用户的动作,发生在工具调用阶段.
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            final_text = part.text
                            logger.info(f"text: {final_text}")

                # if event.grounding_metadata:
                #     grounding_metadata = event.grounding_metadata

        except Exception as e:
            logger.exception("❌ Error during agent execution")
            # TODO: 应当将运行出错的日志写入数据库, 这样管理员可以通过后台了解 agent 的运行情况.
            return


def get_agent_runner(base_url: str) -> AgentRunnerService:
    global _runner_service
    if not _runner_service:
        _runner_service = AgentRunnerService(base_url)
    return _runner_service
