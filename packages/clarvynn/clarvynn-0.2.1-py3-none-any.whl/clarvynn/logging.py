"""
Clarvynn Logging System

This file provides a simple, consistent logging system for Clarvynn that supports:
1. Simple [clarvynn] prefix format for infrastructure tool consistency
2. Configurable log levels (debug, info, warning, error, silent)
3. Cross-language consistency (works with Python, Go, Ruby, etc.)
4. Clean output suitable for infrastructure tooling
5. Thread-safe logging for multi-threaded applications

LOGGING ARCHITECTURE:
- Uses Python's standard logging module as the foundation
- Simple [clarvynn] prefix for all messages
- Minimal formatting to maintain consistency across languages
- Supports both console and file logging (extensible)

INFRASTRUCTURE TOOL DESIGN:
Clarvynn is an infrastructure tool, not a development tool, so logging needs to be:
- Consistent across multiple programming languages (Python, Go, Ruby, etc.)
- Simple and clean for operations teams
- Easy to parse and filter in log aggregation systems
- Minimal overhead for production use

LOG LEVELS:
- debug: Detailed information for debugging
- info: General information about system operation
- warning: Warning messages for potential issues
- error: Error messages for failures
- silent: No logging output (useful for production)

CROSS-LANGUAGE CONSISTENCY:
The [clarvynn] format is designed to be consistent whether Clarvynn is:
- Running Python applications (current)
- Running Go applications (future)
- Running Ruby applications (future)
- Running other language applications (future)

THREAD SAFETY:
Python's logging module is thread-safe by default, making this
suitable for multi-threaded web applications.

ARCHITECTURE ROLE:
This logging system provides observability into Clarvynn's operations,
which is crucial for:
- Operations teams monitoring instrumentation
- Debugging configuration issues
- Tracking export operations
- Understanding system health
"""

import logging
import os
import sys
from typing import Optional

# LOGGING CONFIGURATION
# Global configuration for the logging system
_configured = False  # Flag to prevent duplicate configuration
_current_level = "info"  # Current log level setting
_loggers = {}  # Cache of created loggers for reuse

# LOG LEVEL MAPPING
# Maps string log levels to Python logging constants
LOG_LEVELS = {
    "debug": logging.DEBUG,  # Detailed debugging information
    "info": logging.INFO,  # General information messages
    "warning": logging.WARNING,  # Warning messages
    "error": logging.ERROR,  # Error messages
    "silent": logging.CRITICAL + 1,  # No output (higher than CRITICAL)
}


class ClarvynnFormatter(logging.Formatter):
    """
    SIMPLE FORMATTER FOR CLARVYNN INFRASTRUCTURE LOGS

    PURPOSE: Provide simple, consistent formatting for all Clarvynn log messages.
    This formatter ensures all log messages have the simple [clarvynn] prefix that
    works consistently across multiple programming languages.

    FORMAT STRUCTURE:
    [clarvynn] MESSAGE

    EXAMPLE OUTPUT:
    [clarvynn] Configuration loaded for profile: production
    [clarvynn] Exemplar created value=0.123 trace_id=abc123
    [clarvynn] Failed to start server: Connection refused

    FEATURES:
    - Simple [clarvynn] prefix for all messages
    - No timestamps (handled by log aggregation systems)
    - No component separation (keeps it simple)
    - Cross-language consistency
    - Infrastructure tool appropriate formatting
    """

    def __init__(self):
        """Initialize the formatter with simple format string."""
        # FORMAT TEMPLATE
        # Simple [clarvynn] prefix format for infrastructure consistency
        format_string = "[clarvynn] %(message)s"

        super().__init__(fmt=format_string)

    def format(self, record):
        """
        FORMAT LOG RECORD

        PURPOSE: Format a log record with simple [clarvynn] prefix.
        This method maintains the simple format needed for infrastructure tools.

        Args:
            record: LogRecord object to format

        Returns:
            str: Formatted log message with [clarvynn] prefix
        """
        # Apply base formatting
        formatted = super().format(record)

        return formatted


def configure_logging(level: str = "info", log_file: Optional[str] = None):
    """
    LOGGING SYSTEM CONFIGURATION

    PURPOSE: Configure the global logging system with specified level and output options.
    This is the main function used to set up logging for the entire Clarvynn system.

    WHAT IT DOES:
    1. Sets the global log level for all Clarvynn loggers
    2. Configures console output with simple [clarvynn] formatting
    3. Optionally configures file output (if log_file specified)
    4. Prevents duplicate configuration
    5. Updates existing loggers with new configuration

    LOG LEVEL BEHAVIOR:
    - debug: Shows all messages (very verbose)
    - info: Shows info, warning, and error messages
    - warning: Shows only warning and error messages
    - error: Shows only error messages
    - silent: Shows no messages (production mode)

    CONSOLE OUTPUT:
    Always configures console output with simple [clarvynn] formatting.
    Uses stderr to avoid interfering with application stdout.

    FILE OUTPUT:
    If log_file is specified, also logs to file with the same format.
    File logging is in addition to console logging.

    Args:
        level (str): Log level ("debug", "info", "warning", "error", "silent")
        log_file (str, optional): Path to log file for file output
    """
    global _configured, _current_level

    # LEVEL VALIDATION
    # Ensure the specified log level is valid
    if level not in LOG_LEVELS:
        raise ValueError(f"Invalid log level: {level}. Must be one of {list(LOG_LEVELS.keys())}")

    # PREVENT DUPLICATE CONFIGURATION
    # Only configure once unless level changes
    if _configured and _current_level == level:
        return

    _current_level = level

    # ROOT LOGGER CONFIGURATION
    # Configure the root logger to ensure consistent behavior
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVELS[level])

    # CLEAR EXISTING HANDLERS
    # Remove any existing handlers to prevent duplicate output
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # SILENT MODE HANDLING
    # For silent mode, don't add any handlers
    if level == "silent":
        _configured = True
        return

    # CONSOLE HANDLER SETUP
    # Create console handler with simple [clarvynn] formatting
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(LOG_LEVELS[level])
    console_handler.setFormatter(ClarvynnFormatter())
    root_logger.addHandler(console_handler)

    # FILE HANDLER SETUP (OPTIONAL)
    # If log file is specified, add file handler
    if log_file:
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # Create file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(LOG_LEVELS[level])
            file_handler.setFormatter(ClarvynnFormatter())
            root_logger.addHandler(file_handler)
        except Exception as e:
            # Log file creation failed, continue with console only
            print(f"[clarvynn] Warning: Could not create log file {log_file}: {e}", file=sys.stderr)

    # UPDATE EXISTING LOGGERS
    # Update any existing component loggers with new level
    for logger_name, logger in _loggers.items():
        logger.setLevel(LOG_LEVELS[level])

    _configured = True


def get_logger(component: str = "") -> logging.Logger:
    """
    COMPONENT LOGGER FACTORY

    PURPOSE: Get or create a logger for Clarvynn.
    This ensures consistent logger naming and configuration across the system.

    SIMPLE APPROACH:
    Since Clarvynn is an infrastructure tool, we use a simple approach:
    - All loggers use the same [clarvynn] prefix
    - Component parameter is accepted but not used in formatting
    - This maintains consistency across multiple programming languages

    LOGGER CACHING:
    Loggers are cached to avoid creating duplicate loggers.
    This improves performance and ensures consistent behavior.

    AUTOMATIC CONFIGURATION:
    If logging hasn't been configured yet, automatically configures with default settings.

    Args:
        component (str, optional): Component name (for internal organization only)

    Returns:
        logging.Logger: Configured logger with [clarvynn] formatting
    """
    # AUTOMATIC CONFIGURATION
    # Ensure logging is configured before creating loggers
    if not _configured:
        configure_logging()

    # SIMPLE LOGGER NAME
    # Use simple "clarvynn" name for all loggers to maintain consistency
    logger_name = "clarvynn"

    # LOGGER CACHING
    # Return cached logger if it exists
    if logger_name in _loggers:
        return _loggers[logger_name]

    # LOGGER CREATION
    # Create new logger with simple name
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOG_LEVELS[_current_level])

    # CACHE THE LOGGER
    # Store for future use
    _loggers[logger_name] = logger

    return logger


def log_startup_block(component: str, message: str, details: Optional[dict] = None):
    """
    STARTUP BLOCK LOGGING

    PURPOSE: Log startup information in a visually distinct block format.
    This makes system initialization information clearly visible and well-organized.

    WHAT IT DOES:
    1. Creates a visually distinct block around startup messages
    2. Uses simple [clarvynn] prefix for consistency
    3. Optionally includes structured details
    4. Uses consistent formatting for all startup blocks

    VISUAL FORMAT:
    [clarvynn] ───────────────────────────────────────────
    [clarvynn] MESSAGE
    [clarvynn] Key: Value
    [clarvynn] Key: Value
    [clarvynn] ───────────────────────────────────────────

    USAGE:
    This is typically used during system initialization to log:
    - Configuration loading
    - OpenTelemetry initialization
    - Server startup
    - Adapter registration

    Args:
        component (str): Component name for the startup message (not used in output)
        message (str): Main startup message
        details (dict, optional): Additional key-value details to display
    """
    logger = get_logger()

    # BLOCK HEADER
    # Create visually distinct header with simple format
    logger.info("───────────────────────────────────────────")

    # MAIN MESSAGE
    # Log the primary startup message
    logger.info(message)

    # DETAILS SECTION
    # Log additional details if provided
    if details:
        for key, value in details.items():
            logger.info(f"{key}: {value}")

    # BLOCK FOOTER
    # Create visually distinct footer
    logger.info("───────────────────────────────────────────")


def set_log_level(level: str):
    """
    DYNAMIC LOG LEVEL CHANGE

    PURPOSE: Change the log level for all Clarvynn loggers at runtime.
    This allows dynamic control of logging verbosity without restarting the application.

    WHAT IT DOES:
    1. Validates the new log level
    2. Updates all existing loggers
    3. Updates the global log level setting
    4. Reconfigures handlers if necessary

    USAGE:
    This can be used for:
    - Runtime debugging (increase to debug level)
    - Production quieting (decrease to error level)
    - Temporary troubleshooting

    Args:
        level (str): New log level to set
    """
    global _current_level

    # LEVEL VALIDATION
    if level not in LOG_LEVELS:
        raise ValueError(f"Invalid log level: {level}. Must be one of {list(LOG_LEVELS.keys())}")

    # UPDATE GLOBAL SETTING
    _current_level = level

    # UPDATE ROOT LOGGER
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVELS[level])

    # UPDATE ALL HANDLERS
    for handler in root_logger.handlers:
        handler.setLevel(LOG_LEVELS[level])

    # UPDATE COMPONENT LOGGERS
    for logger in _loggers.values():
        logger.setLevel(LOG_LEVELS[level])


def get_current_log_level() -> str:
    """
    GET CURRENT LOG LEVEL

    PURPOSE: Get the current log level setting.
    This is useful for components that need to know the current logging configuration.

    Returns:
        str: Current log level string
    """
    return _current_level


# INITIALIZATION
# Ensure logging is configured with defaults when module is imported
if not _configured:
    configure_logging()
