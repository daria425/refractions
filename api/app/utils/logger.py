"""Basic logging configuration for the Refractions project using structlog.

This module provides a small, easy-to-use logger interface:

- configure_logging(level=logging.INFO) -> None
- get_logger(name: Optional[str]) -> structlog.BoundLogger
- logger -> module-level logger bound to the project/service name

Notes:
- Emits JSON logs to stdout by default.
"""

from __future__ import annotations

import logging
import sys
from typing import Optional

import structlog

SERVICE_NAME = "refractions-api"


def configure_logging(level: int = logging.INFO) -> None:
	"""Configure structlog and the standard logging module.

	Logs are emitted to stdout as JSON by default. Call this early in
	application startup (for example, in FastAPI startup events or main
	entrypoints).
	"""

	timestamper = structlog.processors.TimeStamper(fmt="iso")
	processors = [
		structlog.stdlib.filter_by_level,
		structlog.processors.add_log_level,
		timestamper,
		structlog.processors.StackInfoRenderer(),
		structlog.processors.format_exc_info,
		structlog.processors.JSONRenderer(sort_keys=True),
	]

	# Configure standard library logging to be compatible with structlog
	logging.basicConfig(
		format="%(message)s",
		stream=sys.stdout,
		level=level,
	)

	structlog.configure(
		processors=processors,
		context_class=dict,
		logger_factory=structlog.stdlib.LoggerFactory(),
		wrapper_class=structlog.stdlib.BoundLogger,
		cache_logger_on_first_use=True,
	)


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
	"""Return a structlog logger bound with the project/service name.

	Example:
		from api.logger import get_logger
		log = get_logger(__name__)
		log.info("started")
	"""

	name = name or SERVICE_NAME
	return structlog.get_logger(name).bind(service=SERVICE_NAME)


# Configure a reasonable default logger at import time so other modules can
# simply `from api.logger import logger` and start logging.
configure_logging()
logger = get_logger()

__all__ = ["configure_logging", "get_logger", "logger"]

