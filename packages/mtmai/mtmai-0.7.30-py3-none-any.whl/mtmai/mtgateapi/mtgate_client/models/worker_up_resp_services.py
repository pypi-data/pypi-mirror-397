from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.worker_up_resp_services_browser_api import WorkerUpRespServicesBrowserApi
    from ..models.worker_up_resp_services_mainapi import WorkerUpRespServicesMainapi
    from ..models.worker_up_resp_services_vnc import WorkerUpRespServicesVnc


T = TypeVar("T", bound="WorkerUpRespServices")


@_attrs_define
class WorkerUpRespServices:
    """
    Attributes:
        mainapi (WorkerUpRespServicesMainapi):
        vnc (WorkerUpRespServicesVnc):
        browser_api (WorkerUpRespServicesBrowserApi):
    """

    mainapi: WorkerUpRespServicesMainapi
    vnc: WorkerUpRespServicesVnc
    browser_api: WorkerUpRespServicesBrowserApi
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mainapi = self.mainapi.to_dict()

        vnc = self.vnc.to_dict()

        browser_api = self.browser_api.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "mainapi": mainapi,
                "vnc": vnc,
                "browserApi": browser_api,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.worker_up_resp_services_browser_api import WorkerUpRespServicesBrowserApi
        from ..models.worker_up_resp_services_mainapi import WorkerUpRespServicesMainapi
        from ..models.worker_up_resp_services_vnc import WorkerUpRespServicesVnc

        d = dict(src_dict)
        mainapi = WorkerUpRespServicesMainapi.from_dict(d.pop("mainapi"))

        vnc = WorkerUpRespServicesVnc.from_dict(d.pop("vnc"))

        browser_api = WorkerUpRespServicesBrowserApi.from_dict(d.pop("browserApi"))

        worker_up_resp_services = cls(
            mainapi=mainapi,
            vnc=vnc,
            browser_api=browser_api,
        )

        worker_up_resp_services.additional_properties = d
        return worker_up_resp_services

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
