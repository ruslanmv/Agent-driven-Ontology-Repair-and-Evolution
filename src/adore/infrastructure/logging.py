"""Structured logging configuration for ADORE using structlog.

This module provides JSON-formatted structured logging with contextual
information for better observability and debugging.
"""

import logging
import sys
from pathlib import Path
from typing import Any

import structlog
from rich.console import Console
from rich.logging import RichHandler

from adore.infrastructure.config import get_settings


def configure_logging(json_output: bool | None = None, log_level: str | None = None) -> None:
    """Configure structured logging for the application.

    Args:
        json_output: Enable JSON logging output. If None, uses settings.
        log_level: Logging level. If None, uses settings.
    """
    settings = get_settings()
    json_mode = json_output if json_output is not None else settings.log_json
    level = log_level or settings.log_level

    # Configure structlog
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_mode:
        # JSON output for production
        structlog.configure(
            processors=shared_processors
            + [
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Configure standard logging to output JSON
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, level.upper()),
        )
    else:
        # Pretty console output for development
        console = Console(stderr=True)

        structlog.configure(
            processors=shared_processors
            + [
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Configure standard logging with Rich handler
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format="%(message)s",
            handlers=[RichHandler(console=console, rich_tracebacks=True, markup=True)],
        )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Name of the logger (typically __name__).

    Returns:
        structlog.stdlib.BoundLogger: Configured logger instance.
    """
    return structlog.get_logger(name)


class LogContext:
    """Context manager for adding temporary context to logs.

    Example:
        >>> with LogContext(cycle_id=1, agent="LLMGen"):
        ...     logger.info("Processing axiom")
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize log context.

        Args:
            **kwargs: Key-value pairs to add to log context.
        """
        self.context = kwargs
        self.token: object | None = None

    def __enter__(self) -> "LogContext":
        """Enter context and bind variables."""
        self.token = structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context and unbind variables."""
        structlog.contextvars.unbind_contextvars(*self.context.keys())


def log_to_file(log_path: Path, message: dict[str, Any]) -> None:
    """Write a log message to a JSON file.

    Args:
        log_path: Path to the log file.
        message: Log message as a dictionary.
    """
    import json

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as f:
        f.write(json.dumps(message, default=str) + "\n")
