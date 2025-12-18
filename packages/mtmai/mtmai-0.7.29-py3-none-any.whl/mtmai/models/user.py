import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel

from mtmai.models.base_model import MtmBaseSqlModel


class UserBase(SQLModel):
    """用户基础模型"""

    username: str = Field(max_length=255, description="用户名")
    email: EmailStr = Field(max_length=255, description="邮箱")
    is_active: bool = Field(default=True, description="是否激活")
    is_superuser: bool = Field(default=False, description="是否超级用户")
    full_name: Optional[str] = Field(default=None, max_length=255, description="全名")


class User(UserBase, MtmBaseSqlModel, table=True):
    """用户数据库模型"""

    __tablename__ = "mtmai_user"  # 使用不同的表名避免与models.py中的User冲突

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(description="哈希密码")
    deleted_at: Optional[datetime] = Field(default=None, description="软删除时间")


class UserCreate(BaseModel):
    """创建用户请求模型"""

    username: str = Field(max_length=255, description="用户名")
    email: EmailStr = Field(max_length=255, description="邮箱")
    password: str = Field(min_length=6, max_length=40, description="密码")
    full_name: Optional[str] = Field(default=None, max_length=255, description="全名")


class UserUpdate(BaseModel):
    """更新用户请求模型"""

    username: Optional[str] = Field(default=None, max_length=255, description="用户名")
    email: Optional[EmailStr] = Field(default=None, max_length=255, description="邮箱")
    is_active: Optional[bool] = Field(default=None, description="是否激活")
    is_superuser: Optional[bool] = Field(default=None, description="是否超级用户")
    full_name: Optional[str] = Field(default=None, max_length=255, description="全名")


class UserResponse(BaseModel):
    """用户响应模型"""

    id: uuid.UUID
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    full_name: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


# 租户成员关系模型（多对多关系）
class TenantMemberBase(SQLModel):
    """租户成员基础模型"""

    tenant_id: uuid.UUID = Field(description="租户ID")
    user_id: uuid.UUID = Field(description="用户ID")
    role: str = Field(default="member", description="角色")


class TenantMember(TenantMemberBase, MtmBaseSqlModel, table=True):
    """租户成员数据库模型"""

    __tablename__ = "mtmai_tenant_member"  # 使用不同的表名避免冲突

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    deleted_at: Optional[datetime] = Field(default=None, description="软删除时间")
