"""Worker主模块 - 基于事件驱动架构的Worker实现"""

import asyncio
import logging

# 导入任务定义以注册任务处理器
from . import tasks  # noqa: F401
from .event_system import Event, EventProcessor, WorkerEventBus
from .task_handlers import TaskHandlerRegistry
from .websocket_transport import WebSocketTransport

logger = logging.getLogger(__name__)


class Worker(EventProcessor):
    """主Worker类 - 基于事件驱动架构"""

    def __init__(
        self, endpoint: str = "wss://mtgate.yuepa8.com/agents/worker-agent/default"
    ):
        self.transport = WebSocketTransport(endpoint)
        self.event_bus = WorkerEventBus(self.transport)
        super().__init__(self.event_bus)
        self.task_registry = TaskHandlerRegistry(self.event_bus)
        self.is_running = False

    def register_handlers(self):
        """注册事件处理器"""
        self.event_bus.on_event("worker_ping", self._handle_ping_event)
        self.event_bus.on_event("task_submit", self._handle_task_submit_event)
        self.event_bus.on_event("task_assigned", self._handle_task_assigned_event)
        self.event_bus.on_event("start_napcat", self._handle_start_napcat_event)

    async def start(self):
        """启动Worker"""
        logger.info("启动Worker...")
        self.is_running = True
        await self.event_bus.start()

        logger.info("Worker启动完成")

    async def stop(self):
        """停止Worker"""
        logger.info("停止Worker...")
        self.is_running = False

        await self.event_bus.stop()

        logger.info("Worker已停止")

    async def _handle_ping_event(self, event: Event):
        """处理ping事件"""
        worker_id = self.event_bus.worker_id
        response_data = {
            "type": "worker_pong",
            "data": {
                "workerId": worker_id,
                "timestamp": int(asyncio.get_event_loop().time() * 1000),
                "message": f"Pong from {worker_id}",
            },
        }
        await self.send_response(response_data)
        logger.info(f"已响应ping事件: {worker_id}")

    async def _handle_task_submit_event(self, event: Event):
        """处理任务提交事件"""
        data = event.data
        task_id = data.get("taskId")
        task_type = data.get("taskType")
        payload = data.get("payload", {})

        if not task_id or not task_type:
            logger.warning(
                f"任务提交事件缺少必要参数: taskId={task_id}, taskType={task_type}"
            )
            return

        logger.info(f"收到任务提交事件: {task_id}, 类型: {task_type}")
        await self.task_registry.process_task(str(task_id), str(task_type), payload)

    async def _handle_task_assigned_event(self, event: Event):
        """处理任务分配事件"""
        data = event.data
        task_id = data.get("taskId")
        task_type = data.get("taskType")
        target_worker = data.get("workerId")
        worker_id = self.event_bus.worker_id

        if not task_id or not task_type:
            logger.warning(
                f"任务分配事件缺少必要参数: taskId={task_id}, taskType={task_type}"
            )
            return

        if target_worker == "all_workers" or target_worker == worker_id:
            logger.info(f"收到分配任务事件: {task_id}, 类型: {task_type}")
            await self.task_registry.process_task(str(task_id), str(task_type), {})

    async def _handle_start_napcat_event(self, event: Event):
        """处理启动napcat事件"""
        data = event.data
        task_id = data.get(
            "taskId", f"napcat_start_{int(asyncio.get_event_loop().time() * 1000)}"
        )

        logger.info(f"收到启动NapCat事件: {task_id}")
        await self.task_registry.process_task(task_id, "start_napcat", data)


async def start_worker(
    endpoint: str = "wss://mtgate.yuepa8.com/agents/worker-agent/default",
):
    """启动Worker的便捷函数"""
    worker = Worker(endpoint)
    await worker.start()
    return worker
