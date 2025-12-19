from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Endpoint")


@_attrs_define
class Endpoint:
    """Endpoint for accessing a service running in the sandbox.
    The service must be listening on the specified port inside the sandbox for the endpoint to be available.

        Attributes:
            endpoint (str): Public URL to access the service from outside the sandbox.
                Format: {endpoint-host}/sandboxes/{sandboxId}/port/{port}
                Example: endpoint.opensandbox.dev/sandboxes/abc123/port/8080
    """

    endpoint: str

    def to_dict(self) -> dict[str, Any]:
        endpoint = self.endpoint

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "endpoint": endpoint,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        endpoint = d.pop("endpoint")

        endpoint = cls(
            endpoint=endpoint,
        )

        return endpoint
