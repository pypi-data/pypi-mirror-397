from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ErrorResponse")


@_attrs_define
class ErrorResponse:
    """Standard error response for all non-2xx HTTP responses.
    HTTP status code indicates the error category; code and message provide details.

        Attributes:
            code (str): Machine-readable error code (e.g., INVALID_REQUEST, NOT_FOUND, INTERNAL_ERROR).
                Use this for programmatic error handling.
            message (str): Human-readable error message describing what went wrong and how to fix it.
    """

    code: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        message = self.message

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "code": code,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = d.pop("code")

        message = d.pop("message")

        error_response = cls(
            code=code,
            message=message,
        )

        return error_response
