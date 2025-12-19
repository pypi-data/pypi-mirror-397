# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class InterceptedRequest(BaseModel):
    url: str
    method: str
    headers: dict[str, str]
    body: Any | None = None

    class Config:
        arbitrary_types_allowed = True


class InterceptedResponse(BaseModel):
    status: int
    headers: dict[str, str]
    body: Any | None = None

    class Config:
        arbitrary_types_allowed = True


class HandlerResult(BaseModel):
    body: str
    additional_headers: dict[str, str] | None = None
