# Python built-in packages
import logging
import sys
import threading
from pathlib import Path
from types import TracebackType

# Third-party packages
from colorlog import ColoredFormatter


def setup_logger(log_dir: Path):
    """
    Initializes logging with both console and file handlers.

    Args:
        log_dir: Full path to the log file
    """
    # Clear existing handlers to avoid duplicate logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Console handler with colors
    console_formatter = CustomFormatter(
        fmt=(
            "%(log_color)s%(asctime)-8s%(reset)s "
            "%(log_color)s[%(levelname)s]%(reset)s "
            "%(log_color)s%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # File handler (plain, no colors)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler(log_dir, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Capture uncaught exceptions
    sys.excepthook = exception_handler
    threading.excepthook = thread_exception_handler


def exception_handler(
    exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType
):
    """
    Handles uncaught exceptions in the main thread and logs them.

    Args:
        exc_type: Exception type
        exc_value: Exception instance
        exc_traceback: Traceback object
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback),
    )


def thread_exception_handler(args: threading.ExceptHookArgs):
    """
    Handles uncaught exceptions in threads and logs them.

    Args:
        args: Thread exception arguments
    """
    logging.critical(
        f"Uncaught thread exception in {args.thread.name}",
        exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
    )


class CustomFormatter(ColoredFormatter):
    """Custom formatter to override default colorlog colors."""

    # ANSI color codes
    COLORS = dict(
        BRIGHT_WHITE="\033[97m",
        LIGHT_WHITE="\033[38;5;250m",
        BRIGHT_YELLOW="\033[93m",
        RED="\033[91m",
        RESET="\033[0m",
    )

    def _get_escape_code(self, log_colors: dict, level_name: str) -> str:
        """
        Returns ANSI escape codes for log levels.

        Overrides DEBUG/INFO to light-white, CRITICAL to non-bold red. WARNING/ERROR remain
        default.

        Args:
            log_colors: Mapping of log levels to colors
            level_name: Log level name

        Returns:
            ANSI escape code string
        """
        if level_name in ("DEBUG", "INFO"):
            return CustomFormatter.COLORS["LIGHT_WHITE"]
        if level_name == "CRITICAL":
            return super()._get_escape_code(log_colors, "ERROR")
        else:
            return super()._get_escape_code(log_colors, level_name)
