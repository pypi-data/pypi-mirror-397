# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

import atexit
from typing import Callable

_shutdown_handlers: list[Callable[[], None]] = []


def run_before_shutdown(handler: Callable[[], None]) -> None:
    _shutdown_handlers.append(handler)


def _execute_shutdown_handlers() -> None:
    for handler in _shutdown_handlers:
        try:
            handler()
        except Exception:
            pass


atexit.register(_execute_shutdown_handlers)
