import logging
from typing import Optional


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure the application's logging behavior.

    This function attempts to use Rich's ``RichHandler`` for enhanced,
    colorful, and trace-friendly logging. If Rich is not installed,
    it silently falls back to Python's standard logging configuration.
    See more about Rich (https://pypi.org/project/rich/).

    :param level: Logging level to use. Defaults to ``logging.INFO``.
    :type level: int
    :return: None
    """
    handler = None

    try:
        from rich.logging import RichHandler

        handler = RichHandler(rich_tracebacks=True)
        handlers = [handler]
        fmt = "%(message)s"
        datefmt = None

    except (ImportError, ModuleNotFoundError):
        handlers = None
        fmt = "%(asctime)s | %(levelname)-8s | %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt=datefmt,
        handlers=handlers,
        force=True,
    )

    logger = logging.getLogger(__name__)
    if handler is None:
        logger.debug("Rich library not found, using standard logging.")


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Return a logger instance.

    If no name is provided, the module's ``__name__`` is used.

    :param name: Name of the logger. If ``None``, defaults to the current module.
    :type name: str or None
    :return: A configured logger instance.
    """
    return logging.getLogger(name or __name__)
