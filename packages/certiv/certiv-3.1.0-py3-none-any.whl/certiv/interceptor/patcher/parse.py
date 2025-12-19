# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
from typing import Any

from ...logger import logger


def parse_json_body(
    body_string: str | bytes | None, headers: dict[str, str]
) -> Any | None:
    if not body_string:
        return None

    content_type = headers.get("content-type", "")
    if "application/json" not in content_type:
        return None

    try:
        if isinstance(body_string, bytes):
            body_string = body_string.decode("utf-8")
        return json.loads(body_string)
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.debug("Failed to parse JSON body")
        return None
