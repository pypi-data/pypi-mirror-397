# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys
from typing import Any, Literal

LogLevel = Literal["debug", "info", "warn", "error"]


class Logger:
    def __init__(self) -> None:
        self._level: LogLevel = "warn"
        self._level_priority: dict[LogLevel, int] = {
            "debug": 0,
            "info": 1,
            "warn": 2,
            "error": 3,
        }

    def set_log_level(self, level: LogLevel) -> None:
        self._level = level

    def _should_log(self, level: LogLevel) -> bool:
        return self._level_priority[level] >= self._level_priority[self._level]

    def _log(self, level: LogLevel, message: str, data: Any = None) -> None:
        if not self._should_log(level):
            return

        prefix_map = {
            "debug": "[DEBUG]",
            "info": "[INFO]",
            "warn": "[WARN]",
            "error": "[ERROR]",
        }

        prefix = prefix_map[level]
        output = sys.stderr if level == "error" else sys.stdout

        if data is not None:
            print(f"{prefix} {message}", data, file=output)
        else:
            print(f"{prefix} {message}", file=output)

    def debug(self, message: str, data: Any = None) -> None:
        self._log("debug", message, data)

    def info(self, message: str, data: Any = None) -> None:
        self._log("info", message, data)

    def warn(self, message: str, data: Any = None) -> None:
        self._log("warn", message, data)

    def error(self, message: str, data: Any = None) -> None:
        self._log("error", message, data)


logger = Logger()
