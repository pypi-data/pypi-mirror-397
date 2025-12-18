"""任务处理器注册表模块 - 基于事件驱动的任务处理"""

import asyncio
import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, TypeVar

from pydantic import BaseModel

from .event_system import TaskContext, WorkerEventBus

logger = logging.getLogger(__name__)

# 类型变量
InputType = TypeVar("InputType", bound=BaseModel)
OutputType = TypeVar("OutputType", bound=BaseModel)


class TaskInput(BaseModel):
    """基础任务输入"""

    task_id: str
    task_type: str
    payload: Dict[str, Any] = {}


class TaskOutput(BaseModel):
    """基础任务输出"""

    result: str
    duration: float
    success: bool = True
    error: Optional[str] = None


class TaskRegistry:
    """任务注册表 - 使用修饰器模式注册任务处理器"""

    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.input_validators: Dict[str, Type[BaseModel]] = {}
        self.output_validators: Dict[str, Type[BaseModel]] = {}

    def task(
        self,
        task_type: str,
        input_validator: Optional[Type[InputType]] = None,
        output_validator: Optional[Type[OutputType]] = None,
    ):
        """任务修饰器 - 类似hatchet的@task修饰器"""

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(ctx: TaskContext) -> Any:
                try:
                    # 输入验证
                    if input_validator:
                        validated_input = input_validator(**ctx.event.data)
                        result = await func(validated_input, ctx)
                    else:
                        result = await func(ctx)

                    # 输出验证
                    if output_validator and isinstance(result, dict):
                        validated_output = output_validator(**result)
                        return validated_output

                    return result
                except Exception as e:
                    logger.error(f"任务 {task_type} 执行失败: {e}")
                    await ctx.log(f"任务执行失败: {str(e)}", "error")
                    raise

            # 注册处理器
            self.handlers[task_type] = wrapper
            if input_validator:
                self.input_validators[task_type] = input_validator
            if output_validator:
                self.output_validators[task_type] = output_validator

            logger.info(f"注册任务处理器: {task_type}")
            return wrapper

        return decorator

    def get_handler(self, task_type: str) -> Optional[Callable]:
        """获取任务处理器"""
        return self.handlers.get(task_type)

    def list_tasks(self) -> list[str]:
        """列出所有注册的任务类型"""
        return list(self.handlers.keys())


# 全局任务注册表实例
task_registry = TaskRegistry()


class TaskHandlerRegistry:
    """任务处理器注册表 - 兼容旧接口的适配器"""

    def __init__(self, event_bus: WorkerEventBus):
        self.event_bus = event_bus
        self.task_registry = task_registry

    async def process_task(self, task_id: str, task_type: str, payload: Dict[str, Any]):
        """处理任务 - 使用新的事件驱动架构"""
        try:
            logger.info(f"开始处理任务: {task_id}, 类型: {task_type}")
            await self.event_bus.message_sender.send_worker_heartbeat("busy", task_id)
            from .event_system import Event

            event = Event(type=task_type, data={"taskId": task_id, **payload})
            ctx = TaskContext(self.event_bus, task_id, event)
            handler = self.task_registry.get_handler(task_type)
            if handler:
                start_time = asyncio.get_event_loop().time()
                result = await handler(ctx)
                duration = asyncio.get_event_loop().time() - start_time
                if isinstance(result, TaskOutput):
                    result_str = result.result
                    duration = result.duration
                elif isinstance(result, dict) and "result" in result:
                    result_str = result["result"]
                    duration = result.get("duration", duration)
                else:
                    result_str = str(result) if result else "任务完成"
            else:
                result_str, duration = await self._handle_default_task(
                    task_id, task_type, payload
                )

            await self.event_bus.message_sender.send_task_status(
                task_id, "completed", result_str, duration
            )

            await self.event_bus.message_sender.send_worker_heartbeat("idle")

            logger.info(f"任务 {task_id} 处理完成")

        except Exception as e:
            await self.event_bus.message_sender.send_task_status(
                task_id, "failed", error=str(e)
            )
            logger.error(f"任务 {task_id} 处理失败: {e}")

    async def _handle_default_task(
        self, task_id: str, task_type: str, payload: Dict[str, Any]
    ) -> tuple[str, float]:
        """处理默认任务"""
        result = f"Task {task_id} of type {task_type} completed successfully"
        duration = 2.0
        await asyncio.sleep(2)
        return result, duration
