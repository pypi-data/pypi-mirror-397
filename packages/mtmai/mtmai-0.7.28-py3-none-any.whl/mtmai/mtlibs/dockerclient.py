import logging
import time
from pathlib import Path
from typing import Any, Callable, Tuple

import docker
from docker.models.containers import Container

logger = logging.getLogger(__name__)


class NapcatContainerInfo:
    """Napcat容器信息"""

    def __init__(
        self,
        container_name: str,
        container_id: str,
        http_port: int,
        internal_ip: str,
        server_url: str,
    ):
        self.container_name = container_name
        self.container_id = container_id
        self.http_port = http_port
        self.internal_ip = internal_ip
        self.server_url = server_url


class NapcatStartOptions:
    """Napcat启动选项"""

    def __init__(self, container_name: str = "", remove_existing: bool = False):
        self.container_name = container_name
        self.remove_existing = remove_existing


class NapcatDockerManager:
    """Napcat Docker容器管理器"""

    def __init__(self):
        if docker is None:
            raise ImportError("docker package is required but not installed")
        self.docker_client = docker.from_env()
        self.image_name = "mlikiowa/napcat-docker:latest"
        self.volume_base_path = ".vol/napcat/volume"

    def _get_available_port(self, start_port: int = 6099) -> int:
        """获取可用端口"""
        import socket

        for port in range(start_port, start_port + 1000):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("", port))
                    return port
                except OSError:
                    continue
        raise RuntimeError("无法找到可用端口")

    def _create_directories(self, container_name: str) -> Tuple[str, str, str]:
        """创建持久化目录"""
        instance_path = Path(self.volume_base_path) / container_name
        config_path = instance_path / "config"
        qq_config_path = instance_path / "qq_config"
        cache_path = instance_path / "cache"

        for dir_path in [config_path, qq_config_path, cache_path]:
            dir_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"napcat 持久化目录已创建: {instance_path}")

        return (
            str(config_path.absolute()),
            str(qq_config_path.absolute()),
            str(cache_path.absolute()),
        )

    def start_napcat_container(
        self, opts: NapcatStartOptions
    ) -> Tuple[NapcatContainerInfo, Callable[[], None]]:
        """启动Napcat容器"""
        container_name = opts.container_name or f"napcat-{int(time.time())}"

        logger.info(f"启动napcat容器: {container_name}")

        # 创建持久化目录
        config_path, qq_config_path, _cache_path = self._create_directories(
            container_name
        )

        # 检查是否存在同名容器
        existing_containers = self.docker_client.containers.list(
            all=True, filters={"name": container_name}
        )

        if existing_containers and not opts.remove_existing:
            container = existing_containers[0]
            if container.status != "running":  # type: ignore
                container.start()  # type: ignore

            # 获取容器信息
            container.reload()  # type: ignore
            internal_ip = self._get_container_ip(container)  # type: ignore
            host_port = self._get_host_port(container, "6099/tcp")  # type: ignore

            container_info = NapcatContainerInfo(
                container_name=container_name,
                container_id=container.id,  # type: ignore
                http_port=host_port,
                internal_ip=internal_ip,
                server_url=f"http://172.17.0.1:{host_port}",
            )

            def cleanup() -> None:
                pass

            return container_info, cleanup

        # 移除已存在的容器
        if existing_containers and opts.remove_existing:
            for container in existing_containers:
                try:
                    container.remove(force=True)  # type: ignore
                    logger.info(f"已移除容器: {container.id}")  # type: ignore
                except Exception as e:
                    logger.warning(f"移除容器失败: {e}")

        # 拉取镜像
        try:
            self.docker_client.images.pull(self.image_name)
            logger.info(f"镜像拉取成功: {self.image_name}")
        except Exception as e:
            logger.warning(f"镜像拉取失败，将使用本地镜像: {e}")

        # 获取可用端口
        http_port = self._get_available_port()
        logger.info(f"使用HTTP端口: {http_port}")

        # 容器配置
        environment = {}

        volumes = {
            config_path: {"bind": "/app/napcat/config", "mode": "rw"},
            qq_config_path: {"bind": "/app/.config/QQ", "mode": "rw"},
        }

        ports = {"6099/tcp": http_port}

        # 创建并启动容器
        container = self.docker_client.containers.run(
            self.image_name,
            name=container_name,
            ports=ports,
            volumes=volumes,
            environment=environment,
            privileged=True,
            cap_add=["NET_ADMIN", "NET_RAW"],
            detach=True,
            labels={"napcat.name": container_name},
        )

        # 等待容器就绪
        max_attempts = 15
        for attempt in range(max_attempts):
            container.reload()  # type: ignore
            if container.status == "running":  # type: ignore
                logger.info(f"容器已启动 - 尝试次数: {attempt + 1}")
                break
            time.sleep(2)
            if attempt == max_attempts - 1:
                raise RuntimeError(f"等待容器就绪超时，当前状态: {container.status}")

        # 获取容器信息
        internal_ip = self._get_container_ip(container)  # type: ignore

        container_info = NapcatContainerInfo(
            container_name=container_name,
            container_id=container.id or "",  # type: ignore
            http_port=http_port,
            internal_ip=internal_ip,
            server_url=f"http://172.17.0.1:{http_port}",
        )

        logger.info(f"Napcat容器已就绪, HTTP服务访问地址: {container_info.server_url}")

        def cleanup():
            """清理函数"""
            try:
                container.stop()  # type: ignore
                container.remove(force=True)  # type: ignore
                logger.info(f"容器已清理: {container_name}")
            except Exception as e:
                logger.warning(f"清理容器失败: {e}")

        return container_info, cleanup

    def _get_container_ip(self, container: Container) -> str:
        """获取容器IP地址"""
        container.reload()  # type: ignore
        networks = container.attrs["NetworkSettings"]["Networks"]  # type: ignore
        for network in networks.values():
            if network.get("IPAddress"):
                return network["IPAddress"]
        return ""

    def _get_host_port(self, container: Any, internal_port: str) -> int:
        """获取主机端口映射"""
        container.reload()
        port_bindings = container.attrs.get("NetworkSettings", {}).get("Ports", {})
        if internal_port in port_bindings and port_bindings[internal_port]:
            return int(port_bindings[internal_port][0]["HostPort"])
        return 6099
