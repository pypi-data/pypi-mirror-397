import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

# from mtmai.clients.mtgate_api.api.sandboxes import sandbox_list
from mtmai.mtlibs.napcat_client import NapcatSandboxManager
from mtmai.mtlibs.dockerclient import NapcatDockerManager
from e2b_code_interpreter import Sandbox

router = APIRouter()

logger = logging.getLogger(__name__)


class StartNapcatRequest(BaseModel):
    """启动Napcat沙盒请求模型"""

    sandbox_type: str = Field(..., description="沙盒类型")
    sandboxId: str = Field(..., description="沙盒唯一标识符")


class StartNapcatResponse(BaseModel):
    """启动Napcat沙盒响应模型"""

    sandboxId: str = Field(..., description="沙盒唯一标识符")
    error: str | None = Field(None, description="错误信息，成功时为None")


class SandboxStatusInfo(BaseModel):
    """沙盒状态信息"""

    sandboxId: str = Field(..., description="沙盒唯一标识符")
    status: str = Field(..., description="沙盒状态")
    error: str | None = Field(None, description="错误信息")


@router.post("/", response_model=StartNapcatResponse)
async def start_napcat_sandbox(
    req: StartNapcatRequest,
) -> Any:
    """
    启动 Napcat 沙箱（同步返回结果）
    """
    try:
        logger.info(f"开始启动沙盒 - ID: {req.sandboxId}, 类型: {req.sandbox_type}")

        if req.sandbox_type != "napcat":
            error_msg = f"不支持的沙箱类型: {req.sandbox_type}"
            logger.error(error_msg)
            return StartNapcatResponse(sandboxId=req.sandboxId, error=error_msg)

        napcat_manager = NapcatSandboxManager()
        # 启动napcat沙盒实例，客户端对象存储在管理器中供后续操作使用
        await napcat_manager.get_or_create_napcat_sandbox(req.sandboxId)

        logger.info(f"沙盒启动成功 - ID: {req.sandboxId}")
        # 如有必要，这里可扩展返回更多字段（例如 server_url），保持现有响应类型不变
        return StartNapcatResponse(sandboxId=req.sandboxId, error=None)
    except Exception as e:
        error_msg = f"启动沙盒失败: {str(e)}"
        logger.error(error_msg)
        return StartNapcatResponse(sandboxId=req.sandboxId, error=error_msg)


class CheckSandboxStatusRequest(BaseModel):
    sandboxIds: list[str] = Field(..., description="需要检测是 sandbox id 列表")


class CheckSandboxStatusResponse(BaseModel):
    results: list[SandboxStatusInfo] = Field(
        default_factory=list, description="每个沙盒的状态检测结果"
    )
    total_checked: int = Field(..., description="检查的沙盒总数")


@router.post("/check-status", response_model=CheckSandboxStatusResponse)
async def check_sandbox_status(
    req: CheckSandboxStatusRequest,
):
    """
    检查指定沙盒的状态
    """
    results: list[SandboxStatusInfo] = []

    try:
        logger.info(f"开始检查沙盒状态，共 {len(req.sandboxIds)} 个沙盒")

        for sandbox_id in req.sandboxIds:
            try:
                if not sandbox_id:
                    logger.warning("跳过无效的沙盒ID")
                    continue

                # 检查Docker容器状态
                container_name = f"napcat-{sandbox_id}"
                actual_status = check_container_status(container_name)

                error_msg = None
                if actual_status == "error":
                    error_msg = "容器状态异常"

                results.append(
                    SandboxStatusInfo(
                        sandboxId=sandbox_id,
                        status=actual_status,
                        error=error_msg,
                    )
                )

                logger.debug(f"沙盒 {sandbox_id} 状态: {actual_status}")

            except Exception as e:
                logger.error(f"检查沙盒 {sandbox_id} 状态失败: {e}")
                results.append(
                    SandboxStatusInfo(
                        sandboxId=sandbox_id,
                        status="error",
                        error=str(e),
                    )
                )

        logger.info(f"沙盒状态检查完成，共检查 {len(results)} 个沙盒")
        return CheckSandboxStatusResponse(
            results=results,
            total_checked=len(results),
        )

    except Exception as e:
        logger.error(f"检查沙盒状态失败: {e}")
        return CheckSandboxStatusResponse(
            results=[],
            total_checked=0,
        )


def check_container_status(container_name: str) -> str:
    try:
        docker_manager = NapcatDockerManager()
        containers = docker_manager.docker_client.containers.list(
            all=True, filters={"name": container_name}
        )

        if not containers:
            logger.debug(f"容器 {container_name} 不存在")
            return "stopped"

        container = containers[0]
        docker_status = getattr(container, "status", "unknown")

        # 状态映射
        status_mapping = {
            "running": "active",
            "created": "starting",
            "restarting": "starting",
            "stopped": "stopped",
            "exited": "stopped",
            "paused": "stopped",
        }

        mapped_status = status_mapping.get(docker_status, "error")
        logger.debug(
            f"容器 {container_name} Docker状态: {docker_status} -> 系统状态: {mapped_status}"
        )
        return mapped_status

    except Exception as e:
        logger.error(f"检查容器状态失败 {container_name}: {e}")
        return "error"


class CheckAllSandboxesRequest(BaseModel):
    """检查所有沙盒状态请求模型"""

    pass


class CheckAllSandboxesResponse(BaseModel):
    """检查所有沙盒状态响应模型"""

    message: str = Field(..., description="操作结果消息")
    total_checked: int = Field(..., description="检查的沙盒总数")
    updated_count: int = Field(..., description="状态发生变化的沙盒数量")
    results: list[SandboxStatusInfo] = Field(
        default_factory=list, description="每个沙盒的状态检测结果"
    )


# @router.post("/check-all", response_model=CheckAllSandboxesResponse)
# async def check_all_sandboxes(
#     req: CheckAllSandboxesRequest,  # noqa: ARG001
# ) -> CheckAllSandboxesResponse:
#     """
#     检查所有沙盒的状态并返回计算结果（不使用回调机制）
#     """
#     total_checked = 0
#     updated_count = 0
#     results: list[SandboxStatusInfo] = []

#     try:
#         logger.info("开始检查所有沙盒状态")

#         # 获取所有沙盒列表
#         from mtmai.clients.mtgateclient import create_mtgate_client

#         mtgateclient = await create_mtgate_client()
#             # from mtmai.clients.mtgate_api.api.sandboxes.sandbox_list import (
#             #     asyncio_detailed as sandbox_list_detailed,
#             # )

#             detailed_response = await sandbox_list.asyncio_detailed(
#                 client=mtgateclient._client,
#                 limit=100,
#                 offset=0,
#             )

#             if detailed_response.status_code != 200:
#                 logger.error(f"API调用失败，状态码: {detailed_response.status_code}")
#                 if detailed_response.content:
#                     logger.error(f"响应内容: {detailed_response.content}")
#                 return CheckAllSandboxesResponse(
#                     message="获取沙盒列表失败",
#                     total_checked=0,
#                     updated_count=0,
#                     results=[],
#                 )

#             response = detailed_response.parsed

#             services = []
#             if hasattr(response, "services") and response.services:
#                 services = response.services
#                 logger.info(f"获取到沙盒列表，数量: {len(services)}")
#             else:
#                 logger.warning("获取沙盒列表失败：响应格式不正确或无数据")
#                 return CheckAllSandboxesResponse(
#                     message="响应格式不正确或无数据",
#                     total_checked=0,
#                     updated_count=0,
#                     results=[],
#                 )

#             total_checked = len(services)

#             for service in services:
#                 try:
#                     sandbox_id = (
#                         str(service.id) if hasattr(service, "id") and service.id else ""
#                     )
#                     current_status = getattr(service, "status", "unknown")

#                     if not sandbox_id:
#                         logger.warning("跳过无效的沙盒ID")
#                         continue

#                     # 检查Docker容器状态
#                     container_name = f"napcat-{sandbox_id}"
#                     actual_status = check_container_status(container_name)

#                     error_msg = None
#                     if actual_status == "error":
#                         error_msg = "容器状态异常"

#                     if actual_status != current_status:
#                         updated_count += 1

#                     results.append(
#                         SandboxStatusInfo(
#                             sandboxId=sandbox_id,
#                             status=actual_status,
#                             error=error_msg,
#                         )
#                     )
#                 except Exception as e:
#                     logger.error(f"检查沙盒状态失败: {e}")
#                     results.append(
#                         SandboxStatusInfo(
#                             sandboxId=str(getattr(service, "id", "")),
#                             status="error",
#                             error=str(e),
#                         )
#                     )

#         return CheckAllSandboxesResponse(
#             message="检查完成",
#             total_checked=total_checked,
#             updated_count=updated_count,
#             results=results,
#         )
#     except Exception as e:
#         logger.error(f"检查所有沙盒状态失败: {e}")
#         return CheckAllSandboxesResponse(
#             message="检查失败",
#             total_checked=0,
#             updated_count=0,
#             results=[],
#         )


# @router.post("/sandbox-create-e2b", response_model=CheckSandboxStatusResponse)
# async def sandbox_create_e2b(
#     req: CheckSandboxStatusRequest,
# ):
#     sbx = Sandbox.create()  # By default the sandbox is alive for 5 minutes
#     execution = sbx.run_code(
#         "print('hello world')"
#     )  # Execute Python inside the sandbox
#     print(execution.logs)

#     files = sbx.files.list("/")
#     print(files)


# # e2b_68d30187ad93a038e15893ce915ea8df55c3e7b8
