# infrastructure/logging/node_logger.py

from infrastructure.logging.logger import get_logger

def log_node(node_name: str):
    logger = get_logger(f"node.{node_name}")

    def decorator(func):
        def wrapper(*args, **kwargs):
                logger.info("start")
                result = func(*args, **kwargs)
                logger.info("end")
                return result
        return wrapper
    
    return decorator

