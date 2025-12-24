from .logging_formatter import LoggingFormatter
from logging import Logger
from typing import Dict
import logging.config

class LogConfig:
    BLACK: str = "\x1b[30m"
    CYAN_BOLD: str = "\x1b[1;36m"
    RESET: str = "\x1b[0m"
    name: str
    logging_schema: Dict
    logger: Logger

    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.logging_schema = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console_formatter": {
                    "()": LoggingFormatter,
                    "format": f"{LogConfig.BLACK}%(asctime)s{LogConfig.RESET} - [%(levelname)s] - {LogConfig.CYAN_BOLD}%(filename)s:%(lineno)d{LogConfig.RESET} - %(message)s",
                },
                "file_formatter": {
                    "class": "logging.Formatter",
                    "format": f"%(asctime)s - [%(levelname)8s] - %(filename)s:%(lineno)d - %(message)s",
                }
            },
            "handlers": {
                "console_handler": {
                    "class": "logging.StreamHandler",
                    "formatter": "console_formatter",
                }
            },
            "loggers": {
                self.name: {
                    "level": level,
                    "handlers": ["console_handler"],
                    "propagate": False

                }
            }
        }
        logging.config.dictConfig(self.logging_schema)
        self.logger = logging.getLogger(self.name)

    def get_config(self) -> Dict:
        return self.logging_schema

    def add_console_handler(self) -> Dict:
        self.logging_schema['handlers']['console_handler'] = {
            "class": "logging.StreamHandler",
            "formatter": "console_formatter",
        }
        if 'console_handler' not in self.logging_schema['loggers'][self.name]['handlers']:
            self.logging_schema['loggers'][self.name]['handlers'].append(
                'console_handler')
        logging.config.dictConfig(self.logging_schema)
        return self.logging_schema

    def remove_console_handler(self) -> Dict:
        if 'console_handler' in self.logging_schema['handlers']:
            del self.logging_schema['handlers']['console_handler']
        if 'console_handler' in self.logging_schema['loggers'][self.name]['handlers']:
            self.logging_schema['loggers'][self.name]['handlers'].remove(
                'console_handler')
        logging.config.dictConfig(self.logging_schema)
        return self.logging_schema
