import asyncio
import os
import time
from typing import Dict, Any

from daytona_sdk import (
    CodeLanguage,
    CreateSandboxFromImageParams,
    Daytona,
    DaytonaConfig,
    Resources,
    SessionExecuteRequest,
    VolumeMount,
)
from loguru import logger


async def create_sandbox(name: str, image: str) -> Dict[str, Any]:
    """
    创建 Daytona Sandbox

    Args:
        name: Sandbox 名称
        image: Docker 镜像

    Returns:
        包含 sandbox_id, sandbox_url, status 的字典
    """
    try:
        # 从环境变量或配置中获取 API Key
        api_key = os.getenv(
            "DAYTONA_API_KEY",
            "dtn_277b52c5d3c7efaf40752743aa4dad5c3297697b86ae441b04d6ec24c8d1f2ef",
        )

        logger.info(f"Initializing Daytona client with API key: {api_key[:10]}...")

        daytona = Daytona(
            DaytonaConfig(
                api_key=api_key,
            )
        )

        # 检查是否已存在同名的 sandbox
        logger.info(f"Checking for existing sandbox with name: {name}")
        existing_sandboxes = await daytona.list({"name": name})

        if existing_sandboxes:
            logger.info(f"Found existing sandbox: {existing_sandboxes[0].id}")
            sandbox = existing_sandboxes[0]
        else:
            logger.info(f"Creating new sandbox: {name}")

            # 创建 volume（如果需要）
            try:
                volume = daytona.volume.get("gomtm-volume", create=True)
                logger.info(f"Using volume: {volume.id}")
            except Exception as e:
                logger.warning(
                    f"Failed to create/get volume: {e}, continuing without volume"
                )
                volume = None

            # 设置挂载点
            volumes = []
            if volume:
                mount_dir = "/home/daytona/workspace"
                volumes = [VolumeMount(volumeId=volume.id, mountPath=mount_dir)]

            # 创建 sandbox
            sandbox = daytona.create(
                timeout=60 * 60 * 2,  # 2小时超时
                params=CreateSandboxFromImageParams(
                    language=CodeLanguage.PYTHON,
                    image=image,
                    auto_stop_interval=30,  # 30分钟后自动停止
                    resources=Resources(
                        cpu=2,
                        memory=4,  # 4GB RAM
                        disk=10,  # 10GB disk
                    ),
                    volumes=volumes,
                    labels={
                        "created_by": "gomtm",
                        "name": name,
                        "image": image,
                        "created_at": str(int(time.time())),
                    },
                ),
            )

            logger.info(f"Sandbox created: {sandbox.id}")

            # 等待 sandbox 启动
            logger.info("Waiting for sandbox to be ready...")
            await asyncio.sleep(10)  # 等待10秒让sandbox启动

            # 执行初始化命令
            try:
                await setup_sandbox(sandbox)
            except Exception as e:
                logger.warning(f"Failed to setup sandbox: {e}")

        # 构建 sandbox URL
        sandbox_url = f"https://sandbox.daytona.io/{sandbox.id}"

        # 尝试获取实际的访问URL（如果API提供）
        try:
            if hasattr(sandbox, "url") and sandbox.url:
                sandbox_url = sandbox.url
            elif hasattr(sandbox, "access_url") and sandbox.access_url:
                sandbox_url = sandbox.access_url
        except Exception as e:
            logger.warning(f"Failed to get sandbox URL: {e}")

        result = {
            "sandbox_id": sandbox.id,
            "sandbox_url": sandbox_url,
            "status": "created",
            "name": name,
            "image": image,
        }

        logger.info(f"Sandbox creation completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to create sandbox: {e}")
        raise


async def setup_sandbox(sandbox) -> None:
    """
    设置 sandbox 环境

    Args:
        sandbox: Daytona sandbox 实例
    """
    try:
        session_id = f"setup-session-{int(time.time())}"
        logger.info(f"Creating setup session: {session_id}")

        # 创建执行会话
        sandbox.process.create_session(session_id)

        # 执行初始化命令
        setup_commands = [
            # 创建必要的目录
            "sudo mkdir -p ~/.vol && sudo chmod -R 777 ~/.vol && sudo chown -R $(whoami) ~/.vol",
            "sudo mkdir -p ~/workspace && sudo chmod -R 777 ~/workspace && sudo chown -R $(whoami) ~/workspace",
            # 安装 gomtm-cli
            "sudo npm install -g gomtm-cli",
            # 启动 gomtm 服务
            "nohup gomtm server --ts-name=dtn -s=box -s=sshd -s=vnc -s=devcontainer > ~/gomtm.log 2>&1 &",
        ]

        for i, cmd in enumerate(setup_commands):
            logger.info(f"Executing setup command {i + 1}/{len(setup_commands)}: {cmd}")

            try:
                command = sandbox.process.execute_session_command(
                    session_id,
                    SessionExecuteRequest(
                        command=cmd,
                        runAsync=False,  # 同步执行
                    ),
                )

                logger.info(
                    f"Command {i + 1} completed with exit code: {command.exit_code}"
                )
                if command.exit_code != 0:
                    logger.warning(
                        f"Command {i + 1} failed with exit code: {command.exit_code}"
                    )

            except Exception as e:
                logger.warning(f"Failed to execute command {i + 1}: {e}")
                continue

        logger.info("Sandbox setup completed")

    except Exception as e:
        logger.error(f"Failed to setup sandbox: {e}")
        raise


async def list_sandboxes() -> list:
    """
    列出所有 sandbox

    Returns:
        sandbox 列表
    """
    try:
        api_key = os.getenv(
            "DAYTONA_API_KEY",
            "dtn_277b52c5d3c7efaf40752743aa4dad5c3297697b86ae441b04d6ec24c8d1f2ef",
        )

        daytona = Daytona(
            DaytonaConfig(
                api_key=api_key,
            )
        )

        sandboxes = await daytona.list()

        result = []
        for sandbox in sandboxes:
            result.append(
                {
                    "id": sandbox.id,
                    "name": getattr(sandbox, "name", "unknown"),
                    "status": getattr(sandbox, "status", "unknown"),
                    "created_at": getattr(sandbox, "created_at", "unknown"),
                }
            )

        return result

    except Exception as e:
        logger.error(f"Failed to list sandboxes: {e}")
        raise


async def delete_sandbox(sandbox_id: str) -> bool:
    """
    删除 sandbox

    Args:
        sandbox_id: Sandbox ID

    Returns:
        是否成功删除
    """
    try:
        api_key = os.getenv(
            "DAYTONA_API_KEY",
            "dtn_277b52c5d3c7efaf40752743aa4dad5c3297697b86ae441b04d6ec24c8d1f2ef",
        )

        daytona = Daytona(
            DaytonaConfig(
                api_key=api_key,
            )
        )

        # 获取 sandbox
        sandbox = daytona.get(sandbox_id)

        # 删除 sandbox
        daytona.delete(sandbox)

        logger.info(f"Sandbox {sandbox_id} deleted successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to delete sandbox {sandbox_id}: {e}")
        return False


if __name__ == "__main__":
    # 测试函数
    async def test():
        result = await create_sandbox("test-sandbox", "gitgit188/gomtm")
        print(result)

    asyncio.run(test())
