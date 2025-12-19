import logging
import string
import time
from typing import Any, Dict, Tuple

import requests
import structlog

from .context_vars import (
    version_contextvar,
    path_contextvar,
    trace_id_contextvar,
    user_code_contextvar,
    website_contextvar,
)

default_logger = structlog.stdlib.get_logger("default")


class LokiHandler(logging.Handler):
    """Custom logging handler to send logs to Loki."""

    #: String contains chars that can be used in label names in LogQL.
    label_allowed_chars: str = "".join((string.ascii_letters, string.digits, "_"))
    #: A list of pairs of characters to replace in the label name.
    label_replace_with: Tuple[Tuple[str, str], ...] = (
        ("'", ""),
        ('"', ""),
        (" ", "_"),
        (".", "_"),
        ("-", "_"),
    )

    def __init__(self, url: str, level: int, source: str):
        super().__init__(level)
        self.base_url: str = url
        self.source = source

    def emit(self, record):
        """Emit a log record to Loki."""
        if not self.base_url:
            default_logger.error(record.getMessage())
            return

        try:
            payload = self.format(record)
            response = requests.post(
                f"{self.base_url}/api/v1/push",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            if not response.ok:
                raise ValueError(
                    "Unexpected Loki API response status code: {0} - {1}".format(
                        response.status_code, response.text
                    )
                )
        except Exception:
            self.handleError(record)

    def format(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Build JSON payload with a log entry."""
        labels = self.build_labels(record)
        ns = 1e9
        ts = str(int(time.time() * ns))
        stream = {
            "stream": labels,
            "values": [[ts, super().format(record)]],
        }
        return {"streams": [stream]}

    def format_label(self, label: str) -> str:
        """Build labels that can be used in LogQL."""
        for char_from, char_to in self.label_replace_with:
            label = label.replace(char_from, char_to)
        return "".join(char for char in label if char in self.label_allowed_chars)

    def build_labels(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Return labels that must be send to Loki with a log record."""
        labels = {
            "job": "dattos-app-logs",
            "traceId": trace_id_contextvar.get() or "NoTraceId",
            "level": record.levelname,
            "website": website_contextvar.get() or "NoWebsite",
            "path": path_contextvar.get() or "NoHttpRequestContext",
            "version": version_contextvar.get() or "UnknownVersion",
            "user": user_code_contextvar.get() or "UnknownUser",
            "source": self.source,
        }

        extra_labels = getattr(record, "labels", {})
        if not isinstance(extra_labels, dict):
            return labels

        for label_name, label_value in extra_labels.items():
            cleared_name = self.format_label(label_name)
            if cleared_name:
                labels[cleared_name] = label_value

        return labels
