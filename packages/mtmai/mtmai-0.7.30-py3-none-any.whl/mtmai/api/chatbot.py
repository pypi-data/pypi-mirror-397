from typing import Optional
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select, and_
from mtmai.deps import AsyncSessionDep, CurrentUserDep, CurrentTenantDep
from mtmai.models.chatbot import (
    Chatbot,
    ChatbotCreate,
    ChatbotUpdate,
    ChatbotResponse,
    ChatbotListResponse
)


router = APIRouter(prefix="/chatbots", tags=["chatbots"])


@router.get("/", response_model=ChatbotListResponse, operation_id="list_chatbots")
async def list_chatbots(
    session: AsyncSessionDep,
    current_tenant: CurrentTenantDep,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    status: Optional[str] = Query(None, description="按状态过滤"),
    name: Optional[str] = Query(None, description="按名称搜索")
):
    """获取聊天机器人列表"""
    # 构建基础查询，只返回当前租户的聊天机器人
    base_query = select(Chatbot).where(
        and_(
            Chatbot.deleted_at == None,
            Chatbot.tenant_id == current_tenant.id
        )
    )

    if status:
        base_query = base_query.where(Chatbot.status == status)

    if name:
        # 简化名称搜索，直接使用等于比较
        base_query = base_query.where(Chatbot.name == name)

    # 获取总数 - 简化计数，只计算当前租户的聊天机器人
    count_query = select(Chatbot).where(
        and_(
            Chatbot.deleted_at == None,
            Chatbot.tenant_id == current_tenant.id
        )
    )
    if status:
        count_query = count_query.where(Chatbot.status == status)
    if name:
        count_query = count_query.where(Chatbot.name == name)

    count_result = await session.exec(count_query)
    total = len(count_result.all())

    # 获取数据
    stmt = base_query.offset(skip).limit(limit)
    result = await session.exec(stmt)
    chatbots = result.all()

    # 转换为响应模型
    items = [
        ChatbotResponse(
            id=chatbot.id,
            name=chatbot.name,
            description=chatbot.description,
            status=chatbot.status,
            tenant_id=chatbot.tenant_id,
            config=chatbot.config,
            state=chatbot.state,
            created_at=chatbot.created_at,
            updated_at=chatbot.updated_at
        )
        for chatbot in chatbots
    ]

    return ChatbotListResponse(
        items=items,
        total=total,
        page=skip // limit + 1,
        limit=limit
    )


@router.get("/{chatbot_id}", response_model=ChatbotResponse, operation_id="get_chatbot")
async def get_chatbot(
    chatbot_id: uuid.UUID,
    db: AsyncSessionDep,
    current_tenant: CurrentTenantDep
):
    """获取单个聊天机器人详情"""
    stmt = select(Chatbot).where(
        and_(
            Chatbot.id == chatbot_id,
            Chatbot.deleted_at == None,
            Chatbot.tenant_id == current_tenant.id
        )
    )
    result = await db.exec(stmt)
    chatbot = result.first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="聊天机器人不存在")

    return ChatbotResponse(
        id=chatbot.id,
        name=chatbot.name,
        description=chatbot.description,
        status=chatbot.status,
        tenant_id=chatbot.tenant_id,
        config=chatbot.config,
        state=chatbot.state,
        created_at=chatbot.created_at,
        updated_at=chatbot.updated_at
    )


@router.post("/", response_model=ChatbotResponse, operation_id="create_chatbot")
async def create_chatbot(
    chatbot_data: ChatbotCreate,
    session: AsyncSessionDep,
    current_tenant: CurrentTenantDep
):
    """创建新的聊天机器人"""
    # 检查名称是否已存在（在当前租户范围内）
    existing_stmt = select(Chatbot).where(
        and_(
            Chatbot.name == chatbot_data.name,
            Chatbot.deleted_at == None,
            Chatbot.tenant_id == current_tenant.id
        )
    )
    existing_result = await session.exec(existing_stmt)
    if existing_result.first():
        raise HTTPException(status_code=400, detail="聊天机器人名称已存在")

    # 创建新的聊天机器人，使用当前租户ID
    chatbot = Chatbot(
        name=chatbot_data.name,
        description=chatbot_data.description,
        tenant_id=current_tenant.id,
        config=chatbot_data.config,
        status="stopped"
    )

    session.add(chatbot)
    await session.commit()
    await session.refresh(chatbot)

    return ChatbotResponse(
        id=chatbot.id,
        name=chatbot.name,
        description=chatbot.description,
        status=chatbot.status,
        tenant_id=chatbot.tenant_id,
        config=chatbot.config,
        state=chatbot.state,
        created_at=chatbot.created_at,
        updated_at=chatbot.updated_at
    )


@router.put("/{chatbot_id}", response_model=ChatbotResponse, operation_id="update_chatbot")
async def update_chatbot(
    chatbot_id: uuid.UUID,
    chatbot_data: ChatbotUpdate,
    session: AsyncSessionDep,
    current_tenant: CurrentTenantDep
):
    """更新聊天机器人"""
    # 获取现有的聊天机器人（确保属于当前租户）
    stmt = select(Chatbot).where(
        and_(
            Chatbot.id == chatbot_id,
            Chatbot.deleted_at == None,
            Chatbot.tenant_id == current_tenant.id
        )
    )
    result = await session.exec(stmt)
    chatbot = result.first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="聊天机器人不存在")

    # 更新字段
    update_data = chatbot_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chatbot, field, value)

    await session.commit()
    await session.refresh(chatbot)

    return ChatbotResponse(
        id=chatbot.id,
        name=chatbot.name,
        description=chatbot.description,
        status=chatbot.status,
        tenant_id=chatbot.tenant_id,
        config=chatbot.config,
        state=chatbot.state,
        created_at=chatbot.created_at,
        updated_at=chatbot.updated_at
    )


@router.delete("/{chatbot_id}", operation_id="delete_chatbot")
async def delete_chatbot(
    chatbot_id: uuid.UUID,
    session: AsyncSessionDep,
    current_tenant: CurrentTenantDep
):
    """删除聊天机器人（软删除）"""
    stmt = select(Chatbot).where(
        and_(
            Chatbot.id == chatbot_id,
            Chatbot.deleted_at == None,
            Chatbot.tenant_id == current_tenant.id
        )
    )
    result = await session.exec(stmt)
    chatbot = result.first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="聊天机器人不存在")

    # 软删除
    chatbot.deleted_at = datetime.now()

    await session.commit()

    return {"message": "聊天机器人删除成功"}


@router.post("/{chatbot_id}/start", operation_id="start_chatbot")
async def start_chatbot(
    chatbot_id: uuid.UUID,
    session: AsyncSessionDep,
    current_tenant: CurrentTenantDep
):
    """启动聊天机器人"""
    stmt = select(Chatbot).where(
        and_(
            Chatbot.id == chatbot_id,
            Chatbot.deleted_at == None,
            Chatbot.tenant_id == current_tenant.id
        )
    )
    result = await session.exec(stmt)
    chatbot = result.first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="聊天机器人不存在")

    if chatbot.status == "running":
        raise HTTPException(status_code=400, detail="聊天机器人已在运行中")

    # 更新状态为启动中
    chatbot.status = "starting"
    await session.commit()

    # TODO: 这里应该触发实际的启动工作流
    # 例如调用 hatchet 工作流或其他异步任务

    return {"message": "聊天机器人启动中", "status": "starting"}


@router.post("/{chatbot_id}/stop", operation_id="stop_chatbot")
async def stop_chatbot(
    chatbot_id: uuid.UUID,
    session: AsyncSessionDep,
    current_tenant: CurrentTenantDep
):
    """停止聊天机器人"""
    stmt = select(Chatbot).where(
        and_(
            Chatbot.id == chatbot_id,
            Chatbot.deleted_at == None,
            Chatbot.tenant_id == current_tenant.id
        )
    )
    result = await session.exec(stmt)
    chatbot = result.first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="聊天机器人不存在")

    if chatbot.status == "stopped":
        raise HTTPException(status_code=400, detail="聊天机器人已停止")

    # 更新状态为停止
    chatbot.status = "stopped"
    await session.commit()

    # TODO: 这里应该触发实际的停止工作流

    return {"message": "聊天机器人已停止", "status": "stopped"}
