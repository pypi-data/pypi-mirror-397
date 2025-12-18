"""WebSocket传输层模块 - 实现MessageTransport接口"""

import asyncio
import json
import logging
import uuid
from typing import Any, Awaitable, Callable, Dict, Optional
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException
from .event_system import Event, MessageTransport

logger = logging.getLogger(__name__)


class WebSocketTransport(MessageTransport):
    """WebSocket传输层实现"""

    def __init__(
        self, endpoint: str = "wss://mtgate.yuepa8.com/agents/worker-agent/default"
    ):
        self.endpoint = endpoint
        self.worker_id = f"worker_{uuid.uuid4().hex[:8]}"
        self.websocket: Optional[Any] = None
        self.message_callback: Optional[Callable[[Event], Awaitable[None]]] = None
        self.is_running = False
        self._heartbeat_task: Optional[asyncio.Task] = None

    def set_message_callback(self, callback: Callable[[Event], Awaitable[None]]):
        """设置消息回调函数"""
        self.message_callback = callback

    def get_worker_id(self) -> str:
        """获取worker ID"""
        return self.worker_id

    async def send_message(self, message: Dict[str, Any]):
        """发送消息"""
        if self.websocket:
            try:
                await self.websocket.send(json.dumps(message))
                logger.debug(f"消息已发送: {message.get('type', 'unknown')}")
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
        else:
            logger.warning("WebSocket连接未建立，无法发送消息")

    async def start(self):
        """启动传输层"""
        logger.info("启动WebSocket传输层...")
        self.is_running = True

        max_retries = 5
        retry_count = 0

        while retry_count < max_retries and self.is_running:
            try:
                logger.info(
                    f"尝试连接到 {self.endpoint} (重试 {retry_count + 1}/{max_retries})"
                )

                async with websockets.connect(self.endpoint) as websocket:
                    self.websocket = websocket
                    logger.info(f"WebSocket连接已建立，Worker ID: {self.worker_id}")
                    await self._send_register_message()
                    self._heartbeat_task = asyncio.create_task(self._send_heartbeat())

                    try:
                        async for message in websocket:
                            if not self.is_running:
                                break
                            if isinstance(message, bytes):
                                message_str = message.decode("utf-8")
                            elif isinstance(message, bytearray):
                                message_str = message.decode("utf-8")
                            else:
                                message_str = str(message)
                            await self._handle_raw_message(message_str)
                    except ConnectionClosed:
                        logger.warning("WebSocket连接已关闭")
                        break
                    finally:
                        if self._heartbeat_task:
                            self._heartbeat_task.cancel()
                        self.websocket = None

            except (ConnectionClosed, WebSocketException) as e:
                retry_count += 1
                logger.error(f"WebSocket连接错误: {e}")
                if retry_count < max_retries and self.is_running:
                    wait_time = min(2**retry_count, 30)
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("达到最大重试次数或已停止，停止连接")
                    break
            except Exception as e:
                logger.error(f"意外错误: {e}")
                break

    async def stop(self):
        """停止传输层"""
        logger.info("停止WebSocket传输层...")
        self.is_running = False

        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        if self.websocket:
            await self.websocket.close()
            self.websocket = None

    async def _handle_raw_message(self, raw_message: str):
        """处理原始消息并转换为事件"""
        try:
            data = json.loads(raw_message)
            message_type = data.get("type")
            message_data = data.get("data", {})

            logger.info(f"收到消息类型: {message_type}")

            if message_type in self._get_system_message_types():
                logger.debug(f"收到系统消息或广播消息: {message_type}")
                return

            event = Event(type=message_type, data=message_data, source="websocket")

            if self.message_callback:
                await self.message_callback(event)
            else:
                logger.warning(f"未设置消息回调，忽略消息: {message_type}")

        except json.JSONDecodeError as e:
            logger.error(f"消息解析失败: {e}")
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")

    async def _send_register_message(self):
        """发送worker注册消息"""
        register_message = {
            "type": "worker_register",
            "data": {
                "workerId": self.worker_id,
                "workerType": "worker",
                "metadata": {
                    "version": "2.0.0",
                    "capabilities": [
                        "task_processing",
                        "ping_response",
                        "event_driven",
                    ],
                    "started_at": int(asyncio.get_event_loop().time() * 1000),
                },
            },
        }
        await self.send_message(register_message)
        logger.info(f"Worker {self.worker_id} 注册消息已发送")

    async def _send_heartbeat(self):
        """定期发送心跳消息"""
        while self.is_running:
            try:
                heartbeat_message = {
                    "type": "worker_heartbeat",
                    "data": {
                        "workerId": self.worker_id,
                        "status": "idle",
                        "currentTask": None,
                    },
                }
                await self.send_message(heartbeat_message)
                logger.debug(f"心跳消息已发送: {self.worker_id}")
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"发送心跳失败: {e}")
                break

    def _get_system_message_types(self) -> list:
        """获取系统消息类型列表"""
        return [
            "cf_agent_state",
            "cf_agent_mcp_servers",
            "log",
            "state_updated",
            "worker_connected",
            "worker_disconnected",
            "worker_status_changed",
            "agent_restarted",
            "settings_updated",
            "toast",
            "task_failed",
            "task_completed",
            "napcat_status_update",
            "napcat_qrcode_update",
        ]


def workerEntry():
    """
    worker 入口函数, 用于在单独的进程中启动worker.
    基于新的事件驱动架构实现.
    """
    logger.info("启动事件驱动Worker...")

    from .worker import start_worker

    asyncio.run(start_worker())
