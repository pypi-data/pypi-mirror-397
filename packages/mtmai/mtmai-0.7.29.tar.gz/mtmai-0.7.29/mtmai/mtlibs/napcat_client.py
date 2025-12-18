import asyncio
import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class QRCodeResponse:
    def __init__(self, data: Dict[str, Any]):
        self.data = data.get("data", {})
        self.message = data.get("message", "")

    @property
    def qrcode(self) -> str:
        return self.data.get("qrcode", "")


class LoginStatusResponse:
    def __init__(self, data: Dict[str, Any]):
        self.data = data.get("data", {})
        self.message = data.get("message", "")

    @property
    def is_login(self) -> bool:
        return self.data.get("isLogin", False)

    @property
    def qrcode_url(self) -> str:
        return self.data.get("qrcodeurl", "")


class LoginInfoResponse:
    def __init__(self, data: Dict[str, Any]):
        self.data = data.get("data", {})
        self.message = data.get("message", "")

    @property
    def qq(self) -> str:
        return self.data.get("qq", "")

    @property
    def nickname(self) -> str:
        return self.data.get("nickname", "")

    @property
    def avatar(self) -> str:
        return self.data.get("avatar", "")


class OneBotConfig:
    def __init__(self, gomtm_server_url: str):
        self.network = {
            "websocketClients": [
                {
                    "name": "gomtm-reverse-ws",
                    "enable": True,
                    "url": gomtm_server_url,
                    "messagePostFormat": "array",
                    "reportSelfMessage": False,
                    "reconnectInterval": 5000,
                    "token": "",
                    "debug": False,
                    "heartInterval": 30000,
                }
            ],
            "httpServers": [
                {
                    "name": "gomtm-http-server",
                    "enable": True,
                    "port": 3000,
                    "host": "0.0.0.0",
                    "enableCors": True,
                    "enableWebsocket": True,
                    "messagePostFormat": "array",
                    "token": "",
                    "debug": False,
                }
            ],
        }
        self.musicSignUrl = ""
        self.enableLocalFile2Url = False
        self.parseMultMsg = False


class NapcatClient:
    """Napcat客户端，用于与napcat容器进行通信"""

    def __init__(self, url: str, api_token: str = "napcat"):
        self.url = url
        self.api_token = api_token
        self.authorization_token = ""
        self.qr_code_url = ""
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        await self.client.aclose()

    async def _ensure_authenticated(self) -> None:
        """确保客户端已认证，如果未认证则自动登录"""
        if not self.authorization_token:
            await self.api_login()

    async def _make_request(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        auth_required: bool = True,
    ) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.url}/api/{endpoint}"
        headers = {}

        if auth_required:
            await self._ensure_authenticated()
            headers["Authorization"] = f"Bearer {self.authorization_token}"

        try:
            if data:
                response = await self.client.post(url, json=data, headers=headers)
            else:
                response = await self.client.post(url, headers=headers)

            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(
                f"HTTP请求失败: endpoint:{endpoint}, authorization_token:{self.authorization_token}, {e}"
            )
            raise

    async def api_login(self) -> None:
        """通过API登录获取Authorization token"""
        hash_input = f"{self.api_token}.napcat"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()

        login_data = {"hash": hash_value}
        response = await self._make_request(
            "auth/login", login_data, auth_required=False
        )

        self.authorization_token = response.get("data", {}).get("Credential", "")
        if not self.authorization_token:
            raise RuntimeError("登录失败，未获取到认证令牌")

    async def get_qq_login_qrcode(self) -> str:
        """获取QQ登录二维码"""
        max_retries = 10

        for i in range(max_retries):
            try:
                response = await self._make_request("QQLogin/GetQQLoginQrcode")
                qr_response = QRCodeResponse(response)
                self.qr_code_url = qr_response.qrcode
                return self.qr_code_url
            except Exception as e:
                logger.warning(f"获取二维码失败 (尝试 {i + 1}/{max_retries}): {e}")
                if i < max_retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise RuntimeError(f"获取二维码失败，已重试{max_retries}次") from e

        # 这行代码理论上不会执行到，但为了类型检查添加
        raise RuntimeError("获取二维码失败")

    async def check_login_status(self) -> tuple[bool, str]:
        """检查登录状态"""
        response = await self._make_request("QQLogin/CheckLoginStatus")
        status_response = LoginStatusResponse(response)
        return status_response.is_login, status_response.qrcode_url

    async def wait_qq_login(self, timeout: int = 120) -> str:
        """等待扫描二维码登录成功，返回selfId"""
        start_time = time.time()
        check_interval = 2

        while time.time() - start_time < timeout:
            try:
                is_login, _ = await self.check_login_status()
                if is_login:
                    login_info = await self.get_login_info()
                    return login_info.qq
            except Exception as e:
                logger.warning(f"检查登录状态失败: {e}")

            await asyncio.sleep(check_interval)

        raise TimeoutError("等待登录超时")

    async def get_login_info(self) -> LoginInfoResponse:
        """获取登录信息"""
        response = await self._make_request("QQLogin/GetQQLoginInfo")
        return LoginInfoResponse(response)

    async def setup_onebot11_reverse_websocket(self, gomtm_server_url: str) -> None:
        """设置OneBot11反向WebSocket"""
        config = OneBotConfig(gomtm_server_url)
        config_json = json.dumps(config.__dict__)

        request_data = {"config": config_json}
        await self._make_request("OB11Config/SetConfig", request_data)

    async def is_valid(self) -> bool:
        """验证客户端是否有效"""
        try:
            await self.api_login()
            return True
        except Exception:
            return False


class NapcatSandboxManager:
    """Napcat沙盒管理器 - Python版本"""

    def __init__(self):
        self.napcat_instances: Dict[str, NapcatClient] = {}

    async def get_or_create_napcat_sandbox(self, instance_id: str) -> NapcatClient:
        """获取或创建napcat沙盒实例"""
        # 检查现有实例
        if instance_id in self.napcat_instances:
            client = self.napcat_instances[instance_id]
            if await client.is_valid():
                return client
            else:
                # 清理无效实例
                await client.client.aclose()
                del self.napcat_instances[instance_id]

        # 创建新的容器和客户端
        from .dockerclient import NapcatDockerManager, NapcatStartOptions

        docker_manager = NapcatDockerManager()
        container_name = f"napcat-{instance_id}"

        container_info, _cleanup = docker_manager.start_napcat_container(
            NapcatStartOptions(container_name=container_name, remove_existing=False)
        )

        # 创建客户端
        client = NapcatClient(container_info.server_url)
        self.napcat_instances[instance_id] = client

        return client

    def remove_invalid_client(self, instance_id: str) -> None:
        """移除无效的客户端"""
        if instance_id in self.napcat_instances:
            del self.napcat_instances[instance_id]


# 全局单例
_sandbox_manager: Optional[NapcatSandboxManager] = None


def get_sandbox_manager() -> NapcatSandboxManager:
    """获取沙盒管理器单例"""
    global _sandbox_manager
    if _sandbox_manager is None:
        _sandbox_manager = NapcatSandboxManager()
    return _sandbox_manager
