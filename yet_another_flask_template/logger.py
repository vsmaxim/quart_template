import logging

from quart.logging import default_handler

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(module)s-%(process)s] [%(levelname)s] %(message)s",
    handlers=[default_handler],  # type: ignore
)

logger = logging.getLogger("yaft")

