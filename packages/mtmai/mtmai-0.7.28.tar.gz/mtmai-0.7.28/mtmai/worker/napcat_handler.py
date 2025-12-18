"""NapCat处理模块，负责处理NapCat相关的任务和状态管理"""

import asyncio
import logging
import time

logger = logging.getLogger(__name__)


class NapcatHandler:
    """NapCat处理器"""

    async def _wait_for_napcat_ready(
        self, napcat_client, max_retries: int = 10, retry_delay: int = 2
    ) -> bool:
        """等待napcat服务就绪"""
        for attempt in range(max_retries):
            try:
                if await napcat_client.is_valid():
                    return True
                else:
                    logger.info(
                        f"NapCat服务未就绪，等待中... (尝试 {attempt + 1}/{max_retries})"
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
            except Exception as e:
                logger.warning(
                    f"检查NapCat服务状态失败 (尝试 {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
        return False

    async def handle_start_napcat_task(
        self, event_bus, task_id: str, payload: dict
    ) -> tuple[str, float]:
        """处理启动napcat任务"""
        try:
            logger.info(f"开始启动NapCat容器 - 任务ID: {task_id}")

            # 发送toast消息通知前端
            await event_bus.message_sender.send_toast(
                f"Worker {event_bus.worker_id} 正在启动 NapCat 容器..."
            )

            # 导入napcat客户端
            from mtmai.mtlibs.napcat_client import NapcatSandboxManager

            # 创建napcat沙盒管理器
            napcat_manager = NapcatSandboxManager()

            # 使用worker_id作为实例ID启动napcat容器
            instance_id = f"worker_{event_bus.worker_id}"

            # 启动napcat容器
            napcat_client = await napcat_manager.get_or_create_napcat_sandbox(
                instance_id
            )

            # 等待napcat服务就绪
            napcat_ready = await self._wait_for_napcat_ready(napcat_client)

            if napcat_ready:
                success_message = f"NapCat 容器启动成功 - 实例ID: {instance_id}"
                logger.info(success_message)

                # 发送成功toast消息
                await event_bus.message_sender.send_toast(
                    f"✅ NapCat 容器启动成功！实例ID: {instance_id}"
                )

                # 主动检查登录状态并发送状态更新
                await self.check_and_send_napcat_status(
                    event_bus, instance_id, napcat_client
                )

                return success_message, 5.0
            else:
                error_message = (
                    f"NapCat 容器启动失败 - 实例ID: {instance_id} (服务未就绪)"
                )
                logger.error(error_message)

                # 发送失败toast消息
                await event_bus.message_sender.send_toast(
                    "❌ NapCat 容器启动失败！服务未就绪"
                )

                # 发送错误状态
                await event_bus.message_sender.send_napcat_status(
                    instance_id, "error", "NapCat容器启动失败 - 服务未就绪"
                )

                raise Exception(error_message)

        except Exception as e:
            error_message = f"启动NapCat容器时发生错误: {str(e)}"
            logger.error(error_message)

            # 发送错误toast消息
            await event_bus.message_sender.send_toast(f"❌ 启动 NapCat 失败: {str(e)}")

            # 发送错误状态
            await event_bus.message_sender.send_napcat_status(
                f"worker_{event_bus.worker_id}", "error", str(e)
            )

            raise Exception(error_message)

    async def check_and_send_napcat_status(
        self, event_bus, instance_id: str, napcat_client
    ):
        """检查napcat状态并发送状态更新"""
        try:
            logger.info(f"检查NapCat状态 - 实例ID: {instance_id}")

            # 检查登录状态
            is_login, qrcode_url = await napcat_client.check_login_status()

            if is_login:
                await self._handle_logged_in_status(
                    event_bus, instance_id, napcat_client
                )
            else:
                await self._handle_login_required_status(
                    event_bus, instance_id, napcat_client, qrcode_url
                )

        except Exception as e:
            logger.error(f"检查NapCat状态失败: {e}")
            await event_bus.message_sender.send_napcat_status(
                instance_id, "error", f"检查登录状态失败: {str(e)}"
            )

    async def _handle_logged_in_status(
        self, event_bus, instance_id: str, napcat_client
    ):
        """处理已登录状态"""
        try:
            login_info = await napcat_client.get_login_info()
            status_message = {
                "type": "napcat_status_update",
                "data": {
                    "workerId": event_bus.worker_id,
                    "instanceId": instance_id,
                    "status": "logged_in",
                    "loginInfo": {
                        "qq": login_info.qq,
                        "nickname": login_info.nickname,
                        "avatar": login_info.avatar,
                    },
                    "timestamp": int(time.time() * 1000),
                },
            }
            await event_bus.send_response(status_message)
            logger.info(f"NapCat已登录，QQ: {login_info.qq}")
        except Exception as e:
            logger.warning(f"获取登录信息失败: {e}")
            status_message = {
                "type": "napcat_status_update",
                "data": {
                    "workerId": event_bus.worker_id,
                    "instanceId": instance_id,
                    "status": "logged_in",
                    "timestamp": int(time.time() * 1000),
                },
            }
            await event_bus.send_response(status_message)
            logger.info("NapCat已登录")

    async def _handle_login_required_status(
        self, event_bus, instance_id: str, napcat_client, qrcode_url: str
    ):
        """处理需要登录状态"""
        if not qrcode_url:
            try:
                qrcode_url = await napcat_client.get_qq_login_qrcode()
            except Exception as e:
                logger.warning(f"获取二维码失败: {e}")
                await event_bus.message_sender.send_napcat_status(
                    instance_id, "error", f"获取二维码失败: {str(e)}"
                )
                return

        # 发送状态更新和二维码
        status_message = {
            "type": "napcat_status_update",
            "data": {
                "workerId": event_bus.worker_id,
                "instanceId": instance_id,
                "status": "login_required",
                "qrCodeUrl": qrcode_url,
                "timestamp": int(time.time() * 1000),
            },
        }
        await event_bus.send_response(status_message)

        # 单独发送二维码更新事件
        qrcode_message = {
            "type": "napcat_qrcode_update",
            "data": {
                "workerId": event_bus.worker_id,
                "instanceId": instance_id,
                "qrCodeUrl": qrcode_url,
                "timestamp": int(time.time() * 1000),
            },
        }
        await event_bus.send_response(qrcode_message)
        logger.info("NapCat需要扫码登录，二维码已获取")
