import logging
import os
from logging.handlers import RotatingFileHandler


class AppLogger:
    _loggers = {}

    @staticmethod
    def get_logger(name: str = "app"):
        if name in AppLogger._loggers:
            return AppLogger._loggers[name]

        # Log level from ENV (default INFO)
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        logger.propagate = False  # prevent duplicate logs

        # Avoid duplicate handlers
        if not logger.handlers:
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
            )

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            # File handler (rotating)
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)

            file_handler = RotatingFileHandler(
                f"{log_dir}/app.log",
                maxBytes=5 * 1024 * 1024,  # 5 MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        AppLogger._loggers[name] = logger
        return logger
