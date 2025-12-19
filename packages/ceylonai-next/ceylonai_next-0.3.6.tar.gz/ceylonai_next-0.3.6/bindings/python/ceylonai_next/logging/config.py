"""Logging configuration and initialization."""

from ceylonai_next.ceylonai_next import (
    PyLoggingConfig,
    PyLoggingHandle,
    init_logging_py,
)


# Logging aliases
LoggingConfig = PyLoggingConfig
LoggingHandle = PyLoggingHandle
init_logging = init_logging_py
