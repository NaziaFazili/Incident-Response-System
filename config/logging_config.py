import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def configure_logging():
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
