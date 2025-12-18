from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.worker_up_resp_tunnel_cloudflared import WorkerUpRespTunnelCloudflared
    from ..models.worker_up_resp_tunnel_tailscale import WorkerUpRespTunnelTailscale


T = TypeVar("T", bound="WorkerUpRespTunnel")


@_attrs_define
class WorkerUpRespTunnel:
    """
    Attributes:
        cloudflared (WorkerUpRespTunnelCloudflared):
        tailscale (WorkerUpRespTunnelTailscale):
    """

    cloudflared: WorkerUpRespTunnelCloudflared
    tailscale: WorkerUpRespTunnelTailscale
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cloudflared = self.cloudflared.to_dict()

        tailscale = self.tailscale.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cloudflared": cloudflared,
                "tailscale": tailscale,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.worker_up_resp_tunnel_cloudflared import WorkerUpRespTunnelCloudflared
        from ..models.worker_up_resp_tunnel_tailscale import WorkerUpRespTunnelTailscale

        d = dict(src_dict)
        cloudflared = WorkerUpRespTunnelCloudflared.from_dict(d.pop("cloudflared"))

        tailscale = WorkerUpRespTunnelTailscale.from_dict(d.pop("tailscale"))

        worker_up_resp_tunnel = cls(
            cloudflared=cloudflared,
            tailscale=tailscale,
        )

        worker_up_resp_tunnel.additional_properties = d
        return worker_up_resp_tunnel

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
