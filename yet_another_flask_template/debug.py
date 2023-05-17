from yet_another_flask_template.types import T_any
from yet_another_flask_template.logger import logger


def see(x: T_any) -> T_any:
    logger.info(f"Value = {x}")
    logger.info(f"Value type = {type(x)}")
    return x

