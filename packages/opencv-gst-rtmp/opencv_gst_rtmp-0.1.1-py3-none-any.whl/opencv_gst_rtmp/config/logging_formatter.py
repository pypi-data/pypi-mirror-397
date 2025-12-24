
import logging


class LoggingFormatter(logging.Formatter):
    WHITE_BOLD = "\x1b[1;37m"
    GREEN_BOLD = "\x1b[1;32m"
    YELLOW_BOLD = "\x1b[1;33m"
    RED_BOLD = "\x1b[1;31m"
    ORANGE_BOLD = "\x1b[1;38;5;202m"
    RESET = "\x1b[0m"

    def format(self, record):
        if record.levelno == logging.DEBUG:
            record.levelname = f"{self.WHITE_BOLD}{record.levelname:>8}{self.RESET}"
        elif record.levelno == logging.INFO:
            record.levelname = f"{self.GREEN_BOLD}{record.levelname:>8}{self.RESET}"
        elif record.levelno == logging.WARNING:
            record.levelname = f"{self.YELLOW_BOLD}{record.levelname:>8}{self.RESET}"
        elif record.levelno == logging.ERROR:
            record.levelname = f"{self.RED_BOLD}{record.levelname:>8}{self.RESET}"
        elif record.levelno == logging.CRITICAL:
            record.levelname = f"{self.ORANGE_BOLD}{record.levelname:>8}{self.RESET}"
        return super().format(record)
