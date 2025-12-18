
import uuid
from datetime import datetime
from typing import Literal, Optional, Dict, Any
from sqlmodel import Field, SQLModel, JSON, Column
from mtmai.models.base_model import MtmBaseSqlModel
from pydantic import BaseModel


class TenantBase(SQLModel):
    """租户基础模型"""
    name: str = Field(max_length=255, description="租户名称")
    slug: str = Field(max_length=255, description="租户标识符")
    analytics_opt_out: bool = Field(default=False, description="是否选择退出分析")
    alert_member_emails: bool = Field(default=True, description="是否发送成员邮件提醒")
    data_retention_period: str = Field(default="720h", description="数据保留期")


class Tenant(TenantBase, MtmBaseSqlModel, table=True):
    """租户数据库模型"""
    __tablename__ = "tenant"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    deleted_at: Optional[datetime] = Field(default=None, description="软删除时间")


class TenantCreate(BaseModel):
    """创建租户请求模型"""
    name: str = Field(max_length=255, description="租户名称")
    slug: str = Field(max_length=255, description="租户标识符")
    analytics_opt_out: bool = Field(default=False, description="是否选择退出分析")
    alert_member_emails: bool = Field(default=True, description="是否发送成员邮件提醒")


class TenantUpdate(BaseModel):
    """更新租户请求模型"""
    name: Optional[str] = Field(default=None, max_length=255, description="租户名称")
    slug: Optional[str] = Field(default=None, max_length=255, description="租户标识符")
    analytics_opt_out: Optional[bool] = Field(default=None, description="是否选择退出分析")
    alert_member_emails: Optional[bool] = Field(default=None, description="是否发送成员邮件提醒")


class TenantResponse(BaseModel):
    """租户响应模型"""
    id: uuid.UUID
    name: str
    slug: str
    analytics_opt_out: bool
    alert_member_emails: bool
    data_retention_period: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
