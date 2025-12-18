"""事件系统模块 - 提供事件驱动的消息处理架构"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Event(BaseModel):
    """事件数据结构 - 使用Pydantic进行强类型定义"""

    type: str = Field(..., description="事件类型")
    data: Dict[str, Any] = Field(default_factory=dict, description="事件数据")
    source: str = Field(default="unknown", description="事件来源")
    timestamp: float = Field(default_factory=time.time, description="事件时间戳")


class TaskContext:
    """任务上下文 - 提供任务执行时的上下文信息和工具"""

    def __init__(self, event_bus: "WorkerEventBus", task_id: str, event: Event):
        self.event_bus = event_bus
        self.task_id = task_id
        self.event = event

    async def log(self, message: str, level: str = "info"):
        """发送日志事件"""
        log_event = {
            "type": "log",
            "data": {
                "taskId": self.task_id,
                "workerId": self.event_bus.worker_id,
                "level": level,
                "message": message,
                "timestamp": int(time.time() * 1000),
            },
        }
        await self.event_bus.send_response(log_event)

    async def send_status(self, status: str, data: Optional[Dict[str, Any]] = None):
        """发送状态更新"""
        # 使用MessageSender的统一接口，但保持TaskContext的特殊数据格式
        status_data = {
            "taskId": self.task_id,
            "workerId": self.event_bus.worker_id,
            "status": status,
            "timestamp": int(time.time() * 1000),
        }
        if data:
            status_data.update(data)

        status_event = {"type": "task_status_update", "data": status_data}
        await self.event_bus.send_response(status_event)


class EventEmitter:
    """事件发射器 - 负责事件的发布和订阅"""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def on(self, event_type: str, handler: Callable):
        """注册事件监听器"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(handler)

    def off(self, event_type: str, handler: Callable):
        """移除事件监听器"""
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(handler)
            except ValueError:
                pass

    async def emit(self, event: Event):
        """发射事件"""
        logger.debug(f"发射事件: {event.type}")

        if event.type in self._listeners:
            for handler in self._listeners[event.type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"事件处理器执行失败 {event.type}: {e}")


class MessageTransport(ABC):
    """消息传输抽象基类"""

    @abstractmethod
    async def send_message(self, message: Dict[str, Any]):
        """发送消息"""
        pass

    @abstractmethod
    async def start(self):
        """启动传输层"""
        pass

    @abstractmethod
    async def stop(self):
        """停止传输层"""
        pass


class MessageSender:
    """统一的消息发送器 - 减少重复代码"""

    def __init__(self, event_bus: "WorkerEventBus"):
        self.event_bus = event_bus

    async def send_worker_heartbeat(
        self, status: str, current_task: Optional[str] = None
    ):
        """发送worker心跳消息"""
        message = {
            "type": "worker_heartbeat",
            "data": {
                "workerId": self.event_bus.worker_id,
                "status": status,
                "currentTask": current_task,
            },
        }
        await self.event_bus.send_response(message)

    async def send_task_status(
        self,
        task_id: str,
        status: str,
        result: Optional[str] = None,
        duration: Optional[float] = None,
        error: Optional[str] = None,
    ):
        """发送任务状态消息"""
        message_type = {
            "completed": "task_completed",
            "failed": "task_failed",
            "started": "task_started",
        }.get(status, "task_status_update")

        data: Dict[str, Any] = {"taskId": task_id, "workerId": self.event_bus.worker_id}
        if result is not None:
            data["result"] = result
        if duration is not None:
            data["duration"] = duration
        if error is not None:
            data["error"] = error

        message = {"type": message_type, "data": data}
        await self.event_bus.send_response(message)

    async def send_toast(self, message: str):
        """发送toast消息"""
        toast_message = {
            "type": "toast",
            "data": {"message": message},
        }
        await self.event_bus.send_response(toast_message)

    async def send_napcat_status(
        self, instance_id: str, status: str, error: Optional[str] = None
    ):
        """发送NapCat状态更新"""
        data = {
            "workerId": self.event_bus.worker_id,
            "instanceId": instance_id,
            "status": status,
        }
        if error:
            data["error"] = error

        message = {
            "type": "napcat_status_update",
            "data": data,
        }
        await self.event_bus.send_response(message)


class WorkerEventBus:
    """Worker事件总线 - 协调事件发射器和消息传输"""

    def __init__(self, transport: MessageTransport):
        self.emitter = EventEmitter()
        self.transport = transport
        self._worker_id: Optional[str] = None
        self.message_sender = MessageSender(self)

        # 设置传输层的消息回调
        if hasattr(transport, "set_message_callback"):
            transport.set_message_callback(self._handle_incoming_message)

    def set_worker_id(self, worker_id: str):
        """设置worker ID"""
        self.worker_id = worker_id

    @property
    def worker_id(self) -> str:
        """获取worker ID"""
        if hasattr(self.transport, "get_worker_id"):
            return self.transport.get_worker_id()
        return self._worker_id or "unknown"

    @worker_id.setter
    def worker_id(self, value: str):
        """设置worker ID"""
        self._worker_id = value

    async def _handle_incoming_message(self, event: Event):
        """处理传入的消息事件"""
        await self.emit_event(event)

    async def emit_event(self, event: Event):
        """发射事件"""
        await self.emitter.emit(event)

    async def send_response(self, response_data: Dict[str, Any]):
        """发送响应消息"""
        await self.transport.send_message(response_data)

    def on_event(self, event_type: str, handler: Callable):
        """注册事件处理器"""
        self.emitter.on(event_type, handler)

    async def start(self):
        """启动事件总线"""
        await self.transport.start()

    async def stop(self):
        """停止事件总线"""
        await self.transport.stop()


class EventProcessor:
    """事件处理器基类"""

    def __init__(self, event_bus: WorkerEventBus):
        self.event_bus = event_bus
        self.register_handlers()

    def register_handlers(self):
        """注册事件处理器 - 子类需要重写此方法"""
        pass

    async def send_response(self, response_data: Dict[str, Any]):
        """发送响应"""
        await self.event_bus.send_response(response_data)
