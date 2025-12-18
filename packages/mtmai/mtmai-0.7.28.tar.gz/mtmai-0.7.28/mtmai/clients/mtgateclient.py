"""
MtgateClient - 统一的 HonoAPI 客户端封装

这个模块提供了一个简洁优雅的接口来调用 honoapi 后端服务。
所有对 honoapi 后端的调用都应该通过这个客户端进行。
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional, Union

from mtmai.clients.mtgate_api.client import AuthenticatedClient, Client
from mtmai.clients.mtgate_api.api.auth import auth_login
from mtmai.clients.mtgate_api.models.auth_login_body import AuthLoginBody

logger = logging.getLogger(__name__)

default_username = "admin@example.com"
default_password = "Admin123!!"


class MtgateClient:
    def __init__(
        self,
        base_url: str = "https://mtgate.yuepa8.com",
        access_token: Optional[str] = None,
        timeout: float = 30.0,
        tenant_id: Optional[str] = None,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.access_token = access_token
        self.tenant_id = tenant_id

        # 根据是否有access_token选择客户端类型
        self._client: Union[AuthenticatedClient, Client]
        if access_token:
            # 当提供 tenant_id 时，默认为所有请求附带 X-Tenant-ID 头，确保多租户上下文正确传递
            headers = {"X-Tenant-ID": tenant_id} if tenant_id else {}
            self._client = AuthenticatedClient(
                base_url=base_url, token=access_token, headers=headers
            )
        else:
            # 无认证场景（一般不推荐用于生产）
            headers = {"X-Tenant-ID": tenant_id} if tenant_id else {}
            self._client = Client(base_url=base_url, headers=headers)

    @asynccontextmanager
    async def _get_client(self):
        yield self._client

    async def login(self, username: str, password: str):
        """登录"""
        try:
            # 导入需要的模块

            response = await auth_login.asyncio_detailed(
                client=self._client,
                body=AuthLoginBody(email=username, password=password),
            )
            if response.status_code == 200:
                logger.info(f"登录成功: {response.parsed}")
                if response.parsed:
                    self.access_token = str(response.parsed.token)
                    self._client = AuthenticatedClient(
                        base_url=self.base_url, token=self.access_token
                    )
        except Exception as e:
            logger.error(f"登录失败: {e}")
            raise e

    # async def create_user(
    #     self, email: str, password: str, name: Optional[str] = None, role: str = "USER"
    # ):
    #     """创建用户"""
    #     try:
    #         # 导入需要的模块
    #         from mtmai.clients.mtgate_api.models.users_create_body import (
    #             UsersCreateBody,
    #         )
    #         from mtmai.clients.mtgate_api.models.users_create_body_role import (
    #             UsersCreateBodyRole,
    #         )

    #         # 转换role字符串为枚举
    #         role_enum = (
    #             UsersCreateBodyRole.USER
    #             if role == "USER"
    #             else UsersCreateBodyRole.ADMIN
    #         )

    #         # 创建请求体
    #         from mtmai.clients.mtgate_api.types import UNSET

    #         body = UsersCreateBody(
    #             email=email,
    #             password=password,
    #             name=name if name is not None else UNSET,
    #             role=role_enum,
    #         )

    #         # 调用API - 使用详细版本获取更多信息
    #         from mtmai.clients.mtgate_api.api.users.users_create import asyncio_detailed

    #         detailed_response = await asyncio_detailed(client=self._client, body=body)

    #         logger.info(f"API响应状态码: {detailed_response.status_code}")
    #         content_str = (
    #             detailed_response.content.decode("utf-8", errors="ignore")
    #             if isinstance(detailed_response.content, bytes)
    #             else str(detailed_response.content)
    #         )
    #         logger.info(f"API响应内容: {content_str}")

    #         # 检查响应状态码
    #         if detailed_response.status_code == 201:
    #             # 成功创建用户
    #             if detailed_response.parsed:
    #                 return (
    #                     detailed_response.parsed.to_dict()
    #                     if hasattr(detailed_response.parsed, "to_dict")
    #                     else detailed_response.parsed
    #                 )
    #             else:
    #                 logger.error("状态码201但解析响应失败")
    #                 raise Exception("创建用户失败：响应解析失败")
    #         elif detailed_response.status_code == 400:
    #             # 请求错误
    #             error_msg = "创建用户失败：请求错误 (400)"
    #             if detailed_response.parsed:
    #                 error_msg += f" - {detailed_response.parsed}"
    #             logger.error(error_msg)
    #             raise Exception(error_msg)
    #         else:
    #             # 其他状态码
    #             error_msg = (
    #                 f"创建用户失败：API返回状态码 {detailed_response.status_code}"
    #             )
    #             if detailed_response.content:
    #                 content_str = (
    #                     detailed_response.content.decode("utf-8", errors="ignore")
    #                     if isinstance(detailed_response.content, bytes)
    #                     else str(detailed_response.content)
    #                 )
    #                 error_msg += f" - 响应内容: {content_str}"
    #             logger.error(error_msg)
    #             raise Exception(error_msg)

    #     except Exception as e:
    #         logger.error(f"创建用户失败: {e}")
    #         raise

    async def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


mtgate_client = None


def create_mtgate_client(
    base_url: str = "https://mtgate.yuepa8.com",
    access_token: Optional[str] = None,
    timeout: float = 30.0,
    tenant_id: Optional[str] = None,
) -> MtgateClient:
    global mtgate_client
    if not mtgate_client:
        mtgate_client = MtgateClient(
            base_url=base_url,
            access_token=access_token,
            timeout=timeout,
            tenant_id=tenant_id,
        )

        # if not mtgate_client.access_token:
        #     await mtgate_client.login(default_username, default_password)

    return mtgate_client
