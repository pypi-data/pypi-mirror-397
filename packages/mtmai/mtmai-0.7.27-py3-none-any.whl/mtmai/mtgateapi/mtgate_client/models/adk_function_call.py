from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.adk_function_call_args import AdkFunctionCallArgs


T = TypeVar("T", bound="AdkFunctionCall")


@_attrs_define
class AdkFunctionCall:
    """
    Attributes:
        name (str):
        args (AdkFunctionCallArgs):
        id (str | Unset):
    """

    name: str
    args: AdkFunctionCallArgs
    id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        args = self.args.to_dict()

        id = self.id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "args": args,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.adk_function_call_args import AdkFunctionCallArgs

        d = dict(src_dict)
        name = d.pop("name")

        args = AdkFunctionCallArgs.from_dict(d.pop("args"))

        id = d.pop("id", UNSET)

        adk_function_call = cls(
            name=name,
            args=args,
            id=id,
        )

        adk_function_call.additional_properties = d
        return adk_function_call

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
