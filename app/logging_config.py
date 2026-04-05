"""
AgentFlow Logging Configuration
Structured JSON logging for production observability.
"""
import logging

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(funcName)s %(lineno)d",
        },
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "json_console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}


def setup_logging(log_level: str = "INFO", log_format: str = "standard"):
    """Configure logging based on settings."""
    handler_name = "json_console" if log_format == "json" else "console"

    LOGGING_CONFIG["root"]["handlers"] = [handler_name]
    LOGGING_CONFIG["root"]["level"] = log_level
    LOGGING_CONFIG["loggers"]["app"]["handlers"] = [handler_name]
    LOGGING_CONFIG["loggers"]["app"]["level"] = log_level

    logging.config.dictConfig(LOGGING_CONFIG)
