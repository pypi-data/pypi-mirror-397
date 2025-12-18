from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.adk_event import AdkEvent


T = TypeVar("T", bound="AdkSessionGetRespData")


@_attrs_define
class AdkSessionGetRespData:
    """
    Attributes:
        state (Any):
        id (str | Unset):
        app_name (str | Unset):
        user_id (str | Unset):
        events (list[AdkEvent] | Unset):
        update_at (datetime.datetime | Unset):
    """

    state: Any
    id: str | Unset = UNSET
    app_name: str | Unset = UNSET
    user_id: str | Unset = UNSET
    events: list[AdkEvent] | Unset = UNSET
    update_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        state = self.state

        id = self.id

        app_name = self.app_name

        user_id = self.user_id

        events: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.events, Unset):
            events = []
            for events_item_data in self.events:
                events_item = events_item_data.to_dict()
                events.append(events_item)

        update_at: str | Unset = UNSET
        if not isinstance(self.update_at, Unset):
            update_at = self.update_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "state": state,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if app_name is not UNSET:
            field_dict["appName"] = app_name
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if events is not UNSET:
            field_dict["events"] = events
        if update_at is not UNSET:
            field_dict["updateAt"] = update_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.adk_event import AdkEvent

        d = dict(src_dict)
        state = d.pop("state")

        id = d.pop("id", UNSET)

        app_name = d.pop("appName", UNSET)

        user_id = d.pop("userId", UNSET)

        _events = d.pop("events", UNSET)
        events: list[AdkEvent] | Unset = UNSET
        if _events is not UNSET:
            events = []
            for events_item_data in _events:
                events_item = AdkEvent.from_dict(events_item_data)

                events.append(events_item)

        _update_at = d.pop("updateAt", UNSET)
        update_at: datetime.datetime | Unset
        if isinstance(_update_at, Unset):
            update_at = UNSET
        else:
            update_at = isoparse(_update_at)

        adk_session_get_resp_data = cls(
            state=state,
            id=id,
            app_name=app_name,
            user_id=user_id,
            events=events,
            update_at=update_at,
        )

        adk_session_get_resp_data.additional_properties = d
        return adk_session_get_resp_data

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
