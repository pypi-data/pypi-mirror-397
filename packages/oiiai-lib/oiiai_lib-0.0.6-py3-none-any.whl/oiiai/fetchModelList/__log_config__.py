"""
Logging configuration module for fetchModelList.

Provides centralized logging configuration with JSON formatting support
and async logging capabilities.
"""

import json
import logging
import logging.handlers
from datetime import datetime, timezone
from queue import Queue
from typing import Optional

# Module-level logger namespace
LOGGER_NAMESPACE = "oiiai.fetchModelList"

# Module-level queue and listener for async logging
_log_queue: Optional[Queue] = None
_queue_listener: Optional[logging.handlers.QueueListener] = None


class JsonFormatter(logging.Formatter):
    """
    JSON formatter for structured logging output.

    Formats log records as JSON strings containing timestamp, level,
    provider, message, and optional extra fields.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as a JSON string.

        Args:
            record: The log record to format.

        Returns:
            JSON-formatted string with log data.
        """
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "provider": getattr(record, "provider", record.name.split(".")[-1]),
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def configure_logging(
    level: int = logging.WARNING,
    handler: Optional[logging.Handler] = None,
    use_json: bool = True,
    async_enabled: bool = False,
) -> None:
    """
    Configure global logging settings for fetchModelList module.

    Args:
        level: Log level (default: WARNING).
        handler: Custom handler to use. If None, uses StreamHandler or NullHandler.
        use_json: Whether to use JSON format (default: True).
        async_enabled: Whether to enable async logging with QueueHandler (default: False).
    """
    global _log_queue, _queue_listener

    logger = logging.getLogger(LOGGER_NAMESPACE)
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers.clear()

    if handler is not None:
        # Use custom handler provided by user
        if use_json:
            handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    elif async_enabled:
        # Use async logging with QueueHandler
        queue_handler = get_queue_handler()
        logger.addHandler(queue_handler)
    else:
        # Default: use NullHandler to avoid "No handler found" warnings
        logger.addHandler(logging.NullHandler())


def get_queue_handler() -> logging.handlers.QueueHandler:
    """
    Get an async QueueHandler for non-blocking logging.

    Creates a QueueHandler that buffers log records and processes them
    in a separate thread via QueueListener.

    Returns:
        Configured QueueHandler instance.
    """
    global _log_queue, _queue_listener

    if _log_queue is None:
        _log_queue = Queue(-1)  # Unlimited queue size

    # Create a stream handler for the listener to use
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(JsonFormatter())

    # Stop existing listener if any
    if _queue_listener is not None:
        _queue_listener.stop()

    # Create and start the queue listener
    _queue_listener = logging.handlers.QueueListener(
        _log_queue, stream_handler, respect_handler_level=True
    )
    _queue_listener.start()

    return logging.handlers.QueueHandler(_log_queue)


def shutdown_logging() -> None:
    """
    Shutdown async logging and clean up resources.

    Should be called when the application exits to ensure all
    queued log records are processed.
    """
    global _queue_listener

    if _queue_listener is not None:
        _queue_listener.stop()
        _queue_listener = None
