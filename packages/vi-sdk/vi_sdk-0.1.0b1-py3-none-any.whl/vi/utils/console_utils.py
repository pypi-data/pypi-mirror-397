#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   console_utils.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Console utilities for redirecting output to Rich formatting.
"""

import logging
import sys
import threading
import warnings
from contextlib import contextmanager
from io import StringIO

from rich import print as rprint
from rich.console import Console

# Third-party library loggers
TARGET_LOGGERS = [
    "transformers",
    "accelerate",
    "torch",
    "bitsandbytes",
    "peft",
    "xgrammar",
]


class _WarningCaptureHandler:
    """Custom warning handler that captures warnings to a buffer."""

    def __init__(self, warnings_buffer: list[str], rich_console: Console | None = None):
        self.warnings_buffer = warnings_buffer
        self.rich_console = rich_console

    def __call__(
        self,
        message: str | Warning,
        category: type[Warning],
        filename: str,
        lineno: int,
        _file=None,
        _line: str | None = None,
    ):
        """Capture warning to buffer or print immediately."""
        warning_msg = f"{filename}:{lineno}: {category.__name__}: {message}"
        if self.rich_console:
            self.rich_console.print(f"[yellow]warning:[/yellow] {warning_msg}")
        else:
            self.warnings_buffer.append(warning_msg)


class RichLogHandler(logging.Handler):
    """Custom logging handler that redirects log messages to rich.print."""

    def __init__(self, rich_console: Console | None = None):
        """Initialize the Rich log handler with optional console for immediate output.

        Args:
            rich_console: Optional Rich Console for immediate output. If None, uses buffering.

        """
        super().__init__()
        self.log_buffer = []
        self.rich_console = rich_console

    def emit(self, record):
        """Capture log records to buffer or output immediately.

        Args:
            record: The log record to capture.

        """
        try:
            msg = self.format(record)
            if self.rich_console:
                self._print_to_console(record.levelname, msg)
            else:
                self.log_buffer.append((record.levelname, msg))
        except Exception:
            self.handleError(record)

    def _print_to_console(self, level: str, msg: str):
        """Print log message to console with appropriate formatting.

        Args:
            level: Log level name.
            msg: Log message.

        """
        if self.rich_console:
            if level == "WARNING":
                self.rich_console.print(f"[yellow]⚠ {msg}[/yellow]")
            elif level == "ERROR":
                self.rich_console.print(f"[red]✗ {msg}[/red]")
            elif level == "INFO":
                self.rich_console.print(f"[blue]ℹ {msg}[/blue]")
            elif level == "DEBUG":
                self.rich_console.print(f"[dim]🐛 {msg}[/dim]")
            else:
                self.rich_console.print(f"[dim]{level}:[/dim] {msg}")

    def flush_to_rich(self):
        """Flush captured log messages to rich.print.

        Outputs buffered log messages with appropriate colors and icons.
        """
        for level, msg in self.log_buffer:
            self._print_to_console(level, msg)
        self.log_buffer.clear()


class _StreamCapture:
    """Captures stream output and flushes it periodically to Rich console."""

    def __init__(self, stream_name: str, rich_console: Console | None = None):
        """Initialize stream capture.

        Args:
            stream_name: Name of the stream (e.g., "stdout", "stderr")
            rich_console: Optional Rich Console for immediate output

        """
        self.stream_name = stream_name
        self.rich_console = rich_console
        self.buffer = StringIO()
        self.lock = threading.Lock()

    def write(self, text: str):
        """Write text to buffer and optionally flush immediately.

        Args:
            text: Text to write

        """
        if not text or text == "\n":
            return

        with self.lock:
            if self.rich_console:
                # Immediate output mode
                if text.strip():  # Only print non-empty content
                    # Print without stream prefix for cleaner output
                    self.rich_console.print(text.rstrip())
            else:
                # Buffer mode
                self.buffer.write(text)

    def flush(self):
        """Flush any pending output."""
        if self.rich_console:
            pass  # Already flushed in write()
        else:
            # For buffered mode, this will be handled later
            pass

    def get_buffered_content(self) -> str:
        """Get buffered content.

        Returns:
            Buffered content as string

        """
        with self.lock:
            return self.buffer.getvalue()


@contextmanager
def redirect_console(rich_console: Console | None = None):
    """Context manager to redirect stdout, stderr, and logging to rich.print.

    Captures and redirects console output from stdout, stderr, and specific
    third-party library loggers to Rich formatting for better display.

    Only logging messages at WARNING level and above are captured to reduce
    noise from verbose INFO and DEBUG messages.

    Args:
        rich_console: Optional Rich Console for real-time output. If provided,
            output is displayed immediately on new lines. If None, output is
            buffered and displayed at the end.

    Yields:
        None - control is yielded back to the caller.

    """
    # Store original stdout and stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    original_showwarning = warnings.showwarning

    # Create capture objects
    stdout_capture = _StreamCapture("stdout", rich_console)
    stderr_capture = _StreamCapture("stderr", rich_console)
    warnings_buffer: list[str] = []

    # Custom warning handler
    custom_showwarning = _WarningCaptureHandler(warnings_buffer, rich_console)

    # Set up logging capture (only WARNING and above)
    rich_handler = RichLogHandler(rich_console)
    rich_handler.setLevel(logging.WARNING)

    # Get root logger and capture its current handlers and level
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    original_level = root_logger.level

    logger_states = {}
    for logger_name in TARGET_LOGGERS:
        logger = logging.getLogger(logger_name)
        logger_states[logger_name] = {
            "handlers": logger.handlers[:],
            "level": logger.level,
            "propagate": logger.propagate,
        }

    try:
        # Redirect stdout and stderr to our capture objects
        sys.stdout = stdout_capture  # type: ignore[assignment]
        sys.stderr = stderr_capture  # type: ignore[assignment]
        warnings.showwarning = custom_showwarning

        # Add our rich handler to root logger (WARNING and above only)
        root_logger.addHandler(rich_handler)
        if root_logger.level < logging.WARNING:
            root_logger.setLevel(logging.WARNING)

        # Configure specific loggers to use our handler (WARNING and above only)
        for logger_name in TARGET_LOGGERS:
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()
            logger.addHandler(rich_handler)
            logger.setLevel(logging.WARNING)
            logger.propagate = False

        yield

    finally:
        # Restore original stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        warnings.showwarning = original_showwarning

        # Restore logging configuration
        root_logger.handlers = original_handlers
        root_logger.setLevel(original_level)

        # Restore specific loggers
        for logger_name, state in logger_states.items():
            logger = logging.getLogger(logger_name)
            logger.handlers = state["handlers"]
            logger.setLevel(state["level"])
            logger.propagate = state["propagate"]

        # If we're in buffered mode (no rich_console), print captured content now
        if not rich_console:
            stdout_content = stdout_capture.get_buffered_content()
            stderr_content = stderr_capture.get_buffered_content()

            # Print captured content using rich.print if there's any content
            if stdout_content.strip():
                for line in stdout_content.strip().split("\n"):
                    if line.strip():  # Only print non-empty lines
                        rprint(line)

            if stderr_content.strip():
                for line in stderr_content.strip().split("\n"):
                    if line.strip():  # Only print non-empty lines
                        rprint(line)

            if warnings_buffer:
                for warning in warnings_buffer:
                    rprint(f"[yellow]warning:[/yellow] {warning}")

            # Flush any captured log messages
            rich_handler.flush_to_rich()
