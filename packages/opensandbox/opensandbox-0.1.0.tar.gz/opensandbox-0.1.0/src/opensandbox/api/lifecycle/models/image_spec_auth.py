from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ImageSpecAuth")


@_attrs_define
class ImageSpecAuth:
    """Registry authentication credentials (required for private registries)

    Attributes:
        username (str | Unset): Registry username or service account
        password (str | Unset): Registry password or authentication token
    """

    username: str | Unset = UNSET
    password: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        username = self.username

        password = self.password

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if username is not UNSET:
            field_dict["username"] = username
        if password is not UNSET:
            field_dict["password"] = password

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        username = d.pop("username", UNSET)

        password = d.pop("password", UNSET)

        image_spec_auth = cls(
            username=username,
            password=password,
        )

        return image_spec_auth
