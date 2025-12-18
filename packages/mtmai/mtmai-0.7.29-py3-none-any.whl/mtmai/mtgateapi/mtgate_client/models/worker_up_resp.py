from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.worker_up_resp_services import WorkerUpRespServices
    from ..models.worker_up_resp_supabase import WorkerUpRespSupabase
    from ..models.worker_up_resp_tunnel import WorkerUpRespTunnel


T = TypeVar("T", bound="WorkerUpResp")


@_attrs_define
class WorkerUpResp:
    """WorkerUpResp

    Attributes:
        worker_id (str):
        supabase (WorkerUpRespSupabase):
        tunnel (WorkerUpRespTunnel):
        services (WorkerUpRespServices):
    """

    worker_id: str
    supabase: WorkerUpRespSupabase
    tunnel: WorkerUpRespTunnel
    services: WorkerUpRespServices
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        worker_id = self.worker_id

        supabase = self.supabase.to_dict()

        tunnel = self.tunnel.to_dict()

        services = self.services.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workerId": worker_id,
                "supabase": supabase,
                "tunnel": tunnel,
                "services": services,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.worker_up_resp_services import WorkerUpRespServices
        from ..models.worker_up_resp_supabase import WorkerUpRespSupabase
        from ..models.worker_up_resp_tunnel import WorkerUpRespTunnel

        d = dict(src_dict)
        worker_id = d.pop("workerId")

        supabase = WorkerUpRespSupabase.from_dict(d.pop("supabase"))

        tunnel = WorkerUpRespTunnel.from_dict(d.pop("tunnel"))

        services = WorkerUpRespServices.from_dict(d.pop("services"))

        worker_up_resp = cls(
            worker_id=worker_id,
            supabase=supabase,
            tunnel=tunnel,
            services=services,
        )

        worker_up_resp.additional_properties = d
        return worker_up_resp

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
