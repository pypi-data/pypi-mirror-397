from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

T = TypeVar("T", bound="RenewSandboxExpirationResponse")


@_attrs_define
class RenewSandboxExpirationResponse:
    """
    Attributes:
        expires_at (datetime.datetime): The new absolute expiration time in UTC (RFC 3339 format).

            Example: "2025-11-16T14:30:45Z"
    """

    expires_at: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        expires_at = self.expires_at.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "expiresAt": expires_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        expires_at = isoparse(d.pop("expiresAt"))

        renew_sandbox_expiration_response = cls(
            expires_at=expires_at,
        )

        return renew_sandbox_expiration_response
