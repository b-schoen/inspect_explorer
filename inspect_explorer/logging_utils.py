import logging
from typing import Optional


def get_logger(name: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name (Optional[str]): The name of the logger. If None, uses the root logger.
        level (int): The logging level. Defaults to logging.INFO.

    Returns:
        logging.Logger: A configured logger instance.

    Example:
        >>> logger = get_logger("my_module")
        >>> logger.info("This is an info message")
    """
    # Create or get the logger
    logger = logging.getLogger(name)

    # Set the logging level
    logger.setLevel(level)

    # Create a console handler if no handlers are present
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Create a formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(console_handler)

    return logger


def configure_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Configure the root logger with basic settings.

    This function sets up the root logger with a specified logging level and,
    optionally, a file handler. It's intended to be called once at the start
    of the main program to set up logging for the entire application.

    Args:
        level (int): The logging level. Defaults to logging.INFO.
        log_file (Optional[str]): Path to a log file. If provided, logs will be written to this file
                                  in addition to the console. Defaults to None.

    Example:
        >>> configure_logging(level=logging.DEBUG, log_file="app.log")
        >>> logger = logging.getLogger(__name__)
        >>> logger.debug("Logging is now configured.")
    """
    # Configure the basic logging
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # If a log file is specified, add a file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(file_handler)

    # Log that the configuration is complete
    logging.info("Logging configuration completed.")
