from __future__ import annotations

# import copy
from datetime import datetime
import logging
from typing import Any, Optional, TypeVar, Union

from google.adk.events.event import Event
from google.adk.sessions.base_session_service import (
    BaseSessionService,
    GetSessionConfig,
    ListSessionsResponse,
)
from google.adk.sessions.session import Session
from google.adk.sessions.state import State
from google.genai import types
from typing_extensions import override

from mtmai.mtgateapi.mtgate_client.client import Client
from mtmai.mtgateapi.mtgate_client.models.adk_session_create_body import (
    AdkSessionCreateBody,
)
from mtmai.mtgateapi.mtgate_client.types import Unset
from mtmai.mtgateapi.mtgate_client.api.adk import (
    adk_events_append,
    adk_event_list,
    adk_session_create,
    adk_session_get,
)
from mtmai.mtgateapi.mtgate_client.models.adk_event import AdkEvent as ApiAdkEvent
from mtmai.mtgateapi.mtgate_client.models.adk_events_append_body import (
    AdkEventsAppendBody,
)
# from mtmai.mtgateapi.mtgate_client.models.adk_session_create_body import (
#     AdkCreateSessionRequest,
# )

logger = logging.getLogger(__name__)

T = TypeVar("T")


class MtAdkSessionService(BaseSessionService):
    """
    实现了 Google ADK BaseSessionService 接口。
    通过 HTTP (MtGate API) 与后端交互，而非直接操作数据库。
    """

    def __init__(self, base_url: str, **kwargs: Any):
        logger.info(f"[Init] MtAdkSessionService base_url={base_url}")
        self.client = Client(base_url=base_url)
        # 允许客户端处理特定状态码，而不是抛出异常
        self.client.raise_on_unexpected_status = True

    def _unwrap(self, value: Union[T, Unset], default: T) -> T:
        """辅助函数: 处理 Generated Client 中的 Unset 类型"""
        if isinstance(value, Unset):
            return default
        return value

    @override
    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        """创建一个新的 Session"""
        response = await adk_session_create.asyncio_detailed(
            client=self.client,
            body=AdkSessionCreateBody(
                agent_name=app_name,
                user_id=user_id,
                state=state or {},
                session_id=session_id if session_id else "",
            ),
        )

        if not response.parsed or response.status_code != 200:
            raise RuntimeError(f"Failed to create session: {response.status_code}")

        data = response.parsed.data
        if not data:
            raise RuntimeError("API returned empty data for session create")

        updated_at_val = getattr(data, "updated_at", getattr(data, "update_at", None))

        return Session(
            id=self._unwrap(data.id, ""),
            app_name=self._unwrap(getattr(data, "app_name", app_name), app_name),
            user_id=self._unwrap(getattr(data, "user_id", user_id), user_id),
            state=self._unwrap(data.state, {}),
            events=[],
            last_update_time=self._parse_timestamp(str(updated_at_val))
            if updated_at_val
            else 0.0,
        )

    @override
    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        """
        获取 Session 及其 Events。
        """
        logger.debug(f"[get_session] {app_name}:{session_id}")

        # 1. 获取 Session 元数据
        sess_resp = await adk_session_get.asyncio_detailed(
            id=session_id, client=self.client
        )

        if (
            sess_resp.status_code != 200
            or not sess_resp.parsed
            or not sess_resp.parsed.data
        ):
            logger.info(f"[get_session] Session not found: {session_id}")
            return None

        sess_data = sess_resp.parsed.data

        # 2. 获取 Events 列表
        events_resp = await adk_event_list.asyncio_detailed(
            client=self.client, session_id=session_id
        )

        adk_events: list[Event] = []
        if events_resp.parsed and events_resp.parsed.data:
            for raw_event in events_resp.parsed.data:
                try:
                    ev = self._map_api_event_to_adk_event(raw_event)
                    adk_events.append(ev)
                except Exception as e:
                    logger.error(f"Error mapping event: {e}")
                    continue

        # 假设 API 返回的是 updated_at DESC (最新在前)，我们需要反转为正序供 Session 使用
        adk_events.reverse()

        # 安全获取字段
        s_user_id = self._unwrap(getattr(sess_data, "user_id", user_id), user_id)
        s_id = self._unwrap(getattr(sess_data, "id", session_id), session_id)
        s_state = self._unwrap(getattr(sess_data, "state", {}), {})

        # 安全获取 updated_at
        s_updated_at = getattr(
            sess_data, "updated_at", getattr(sess_data, "update_at", None)
        )
        # 兼容: 如果是 additional_properties (当 generated model 缺少字段时)
        if s_updated_at is None and hasattr(sess_data, "additional_properties"):
            s_updated_at = sess_data.additional_properties.get(
                "updatedAt"
            ) or sess_data.additional_properties.get("updated_at")

        return Session(
            app_name=app_name,
            user_id=s_user_id,
            id=s_id,
            state=s_state,
            events=adk_events,
            last_update_time=self._parse_timestamp(str(s_updated_at))
            if s_updated_at
            else 0.0,
        )

    @override
    async def list_sessions(
        self, *, app_name: str, user_id: Optional[str] = None
    ) -> ListSessionsResponse:
        """
        列出 Sessions。
        """
        logger.warning("[list_sessions] Not fully implemented in MtGate API yet")
        return ListSessionsResponse(sessions=[])

    @override
    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        """
        删除 Session。
        注意: 增加了 *, 强制关键字参数以匹配父类签名。
        """
        # TODO: Implement DELETE /adk/session/:id in mtgate
        pass

    @override
    async def append_event(self, session: Session, event: Event) -> Event:
        """
        追加事件。
        """
        if event.partial:
            return event

        # 1. 清理临时状态
        event = self._trim_temp_delta_state(event)

        # 2. 转换 ADK Event -> JSON Dict
        event_dict = event.model_dump(mode="json", exclude_none=True)

        if "timestamp" not in event_dict:
            event_dict["timestamp"] = event.timestamp

        # 3. 调用 API
        # ApiAdkEvent.from_dict 可能会因为 event_dict 结构与 definition 不完全匹配而报错
        # 建议直接使用 API 客户端生成的类型，或者确保 types.ts 定义了 flat 结构
        try:
            api_event_payload = ApiAdkEvent.from_dict(event_dict)
        except Exception:
            # Fallback: 如果 from_dict 失败，可能需要手动构造，或者 event_dict 包含多余字段
            # 这里假设 generated client 比较宽容，或者我们直接传 dict (取决于 client生成配置)
            api_event_payload = ApiAdkEvent.from_dict(event_dict)

        body = AdkEventsAppendBody(
            session_id=session.id,
            event=api_event_payload,
        )

        try:
            resp = await adk_events_append.asyncio_detailed(
                client=self.client, body=body
            )
            if resp.status_code != 200:
                logger.error(f"[append_event] API Error: {resp.content}")
                raise RuntimeError(f"Append event failed: {resp.status_code}")

            # 4. 更新内存中的 Session
            await super().append_event(session=session, event=event)
            return event

        except Exception as e:
            logger.exception("[append_event] Exception")
            raise e

    # --- Helpers ---

    def _parse_timestamp(self, ts_str: str | None) -> float:
        if not ts_str or ts_str == "None":
            return 0.0
        try:
            # 兼容带有 Z 的 ISO 格式
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            return dt.timestamp()
        except Exception:
            # 容错: 也许是纯数字字符串
            try:
                return float(ts_str)
            except ValueError:
                return 0.0

    def _map_api_event_to_adk_event(self, api_evt: Any) -> Event:
        """
        将 API 返回的 Event 数据转换为 Google ADK Event 对象。
        修正: 不再尝试读取 `llmResponse` 嵌套对象，而是直接读取扁平属性。
        """
        if hasattr(api_evt, "to_dict"):
            d = api_evt.to_dict()
        elif hasattr(api_evt, "model_dump"):
            d = api_evt.model_dump()
        else:
            d = api_evt

        # 必须使用 types.Content 等强类型构建 ADK Event
        from google.adk.sessions import _session_util
        from google.adk.events.event_actions import EventActions

        # 优先读取扁平化字段，这些字段对应 types.ts 中的 zAdkEvent 定义
        content_data = d.get("content")
        grounding_data = d.get("grounding_metadata") or d.get("groundingMetadata")
        usage_data = d.get("usage_metadata") or d.get("usageMetadata")
        citation_data = d.get("citation_metadata") or d.get("citationMetadata")
        custom_data = d.get("custom_metadata") or d.get("customMetadata")

        # 处理 Unset
        if isinstance(content_data, Unset):
            content_data = None
        if isinstance(grounding_data, Unset):
            grounding_data = None
        if isinstance(usage_data, Unset):
            usage_data = None

        # 转换 Actions
        actions_raw = d.get("actions") or {}
        if isinstance(actions_raw, Unset):
            actions_raw = {}

        return Event(
            id=self._unwrap(d.get("id"), None),
            invocation_id=self._unwrap(
                d.get("invocation_id") or d.get("invocationId"), None
            ),
            author=self._unwrap(d.get("author"), "user"),
            branch=self._unwrap(d.get("branch"), None),
            timestamp=float(self._unwrap(d.get("timestamp"), 0.0)),
            long_running_tool_ids=set(
                self._unwrap(
                    d.get("long_running_tool_ids") or d.get("longRunningToolIds"), []
                )
            ),
            partial=self._unwrap(d.get("partial"), False),
            # Actions
            actions=EventActions(**actions_raw),
            # LLM Response components (Flat structure)
            content=_session_util.decode_model(content_data, types.Content),
            grounding_metadata=_session_util.decode_model(
                grounding_data, types.GroundingMetadata
            ),
            usage_metadata=_session_util.decode_model(
                usage_data, types.GenerateContentResponseUsageMetadata
            ),
            citation_metadata=_session_util.decode_model(
                citation_data, types.CitationMetadata
            ),
            custom_metadata=custom_data,
            # Error / Status
            turn_complete=self._unwrap(
                d.get("turn_complete") or d.get("turnComplete"), None
            ),
            interrupted=self._unwrap(d.get("interrupted"), None),
            error_code=self._unwrap(d.get("error_code") or d.get("errorCode"), None),
            error_message=self._unwrap(
                d.get("error_message") or d.get("errorMessage"), None
            ),
        )

    def _trim_temp_delta_state(self, event: Event) -> Event:
        """从事件动作中移除临时状态变量 (以 temp_ 开头)"""
        if not event.actions or not event.actions.state_delta:
            return event

        filtered_delta = {}
        for k, v in event.actions.state_delta.items():
            if not k.startswith(State.TEMP_PREFIX):
                filtered_delta[k] = v

        event.actions.state_delta = filtered_delta
        return event
