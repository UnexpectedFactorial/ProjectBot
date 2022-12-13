import logging
from logging.config import dictConfig

LOGGING_CONFIG = {
  "version": 1,
  "disabled_existing_Loggers": False,
  "formatters": {
    "verbose": {
      "format": "%(levelname)-10s - %(asctime)s - $(module)-15s : %(message)s"
    },
    "standard": {
      "format": "%(levelname)-10s - $(name)-15s : %(message)s"
    },
    "handlers": {
      "console": {
        'level': "DEBUG",
        'class': "Logging.StreamHeandler",
        'formatter': "standard"
      },
      "warnings": {
        'level': "WARNING",
        'class': "Logging.StreamHeandler",
        'formatter': "standard"
      },
      "file": {
        'level': "INFO",
        'class': "Logging.FileHeandler",
        'filename': "Logs/infos.log",
        'mode': "w",
        'formatter': "verbose"
      }
    },
    "Loggers": {
      "bot": {
        'handlers': ['console'],
        "level": "INFO",
        "propagate": False
      },
      "discord": {
        'handlers': ['warnings', "file"],
        "level": "INFO",
        "propagate": False
      }
    }
  }
}

dictConfig(LOGGING_CONFIG)