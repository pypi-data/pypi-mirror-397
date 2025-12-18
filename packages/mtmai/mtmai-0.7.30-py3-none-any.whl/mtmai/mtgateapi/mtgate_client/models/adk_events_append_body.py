from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.adk_event import AdkEvent


T = TypeVar("T", bound="AdkEventsAppendBody")


@_attrs_define
class AdkEventsAppendBody:
    """
    Attributes:
        session_id (str):
        event (AdkEvent):
    """

    session_id: str
    event: AdkEvent
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        session_id = self.session_id

        event = self.event.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "session_id": session_id,
                "event": event,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.adk_event import AdkEvent

        d = dict(src_dict)
        session_id = d.pop("session_id")

        event = AdkEvent.from_dict(d.pop("event"))

        adk_events_append_body = cls(
            session_id=session_id,
            event=event,
        )

        adk_events_append_body.additional_properties = d
        return adk_events_append_body

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
