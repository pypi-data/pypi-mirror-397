import asyncio
import json
import logging
from typing import Dict, Any, Callable

from mtmai.agent_runner import get_agent_runner
from mtmai.mtgateapi.mtgate_client.client import Client
from mtmai.mtgateapi.mtgate_client.api.queue import queue_pull, queue_ack
from mtmai.mtgateapi.mtgate_client.models.worker_pull_request import WorkerPullRequest
from mtmai.mtgateapi.mtgate_client.models.worker_ack_request import WorkerAckRequest

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [Worker] - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mtworker")


class MtWorker:
    """
    功能: 从中心服务器拉取新消费队列消息.
    """

    def __init__(self, base_url: str, worker_id: str = "default"):
        self.base_url = base_url
        self.worker_id = worker_id
        self.client = Client(base_url=base_url)
        self.client.raise_on_unexpected_status = True
        self.running = False

        self.handlers: Dict[str, Callable] = {
            "new_chat_message": self.handle_new_chat_message
        }

    async def start(self):
        """启动 Worker 主循环"""
        self.running = True
        logger.info(
            f"🚀 MtWorker started. ID: {self.worker_id}, Target: {self.base_url}"
        )

        while self.running:
            try:
                await self.pull_and_process()
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                await asyncio.sleep(5)

            await asyncio.sleep(2)

    async def pull_and_process(self):
        """拉取并处理一批消息"""
        try:
            response = await queue_pull.asyncio_detailed(
                client=self.client, body=WorkerPullRequest(worker_id=self.worker_id)
            )

            if response.status_code != 200 or not response.parsed:
                logger.warning(f"Pull failed: {response.status_code}")
                return
            messages = getattr(response.parsed, "data", [])
            if not messages:
                return

            logger.info(f"📥 Received {len(messages)} messages")

            for msg in messages:
                await self.process_single_message(msg)

        except Exception as e:
            logger.error(f"Pull request failed: {e}")

    async def process_single_message(self, msg: Any):
        """处理单条消息"""
        if isinstance(msg, dict):
            msg_id = msg.get("msg_id")
            read_ct = msg.get("read_ct")
            payload = msg.get("message")
        else:
            msg_id = getattr(msg, "msg_id", None)
            read_ct = getattr(msg, "read_ct", 0)
            payload = getattr(msg, "message", {})
        if msg_id is None:
            logger.error("Message missing msg_id")
            return

        logger.info(f"Processing MsgID: {msg_id} (Retry: {read_ct})")

        if read_ct is not None and read_ct > 10:
            logger.error(f"❌ MsgID {msg_id} exceeded max retries.")
            await self.ack_message(msg_id)
            return

        try:
            if isinstance(payload, str):
                payload = json.loads(payload)
            msg_type = payload.get("type") if isinstance(payload, dict) else None

            if not msg_type:
                logger.warning(f"⚠️ MsgID {msg_id} has no 'type'. Payload: {payload}")
                await self.ack_message(msg_id)
                return

            handler = self.handlers.get(msg_type)
            if handler:
                await handler(payload)
                await self.ack_message(msg_id)
            else:
                logger.warning(f"⚠️ No handler for type: {msg_type}")
                await self.ack_message(msg_id)

        except Exception as e:
            logger.error(f"❌ Error processing MsgID {msg_id}: {e}")

    async def ack_message(self, msg_id: float):
        try:
            await queue_ack.asyncio_detailed(
                client=self.client, body=WorkerAckRequest(msg_id=msg_id)
            )
            logger.info(f"✅ Acked MsgID: {msg_id}")
        except Exception as e:
            logger.error(f"Failed to Ack MsgID {msg_id}: {e}")

    async def handle_new_chat_message(self, payload: Dict[str, Any]):
        chat_id = payload.get("chat_id")
        user_id = payload.get("user_id")

        logger.info(f"📨 [NewChatMessage] Chat: {chat_id}, User: {user_id}")

        runner = await get_agent_runner(self.base_url)
        await runner.run_chat_agent(payload)
