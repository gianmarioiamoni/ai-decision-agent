# infrastructure/logging/node_logger.py

from functools import wraps
from infrastructure.logging.logger import get_logger

def log_node(node_name: str):
    logger = get_logger(f"node.{node_name}")

    def decorator(func):
        @wraps(func)
        def wrapper(state):
            logger.info("start")
            result = func(state)
            logger.info("end")
            return result
        return wrapper
    return decorator
