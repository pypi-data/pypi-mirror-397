from functools import wraps
from loguru import logger

def handle_exceptions(default=None, log_error=False):
    """
    异常处理装饰器
    
    :param default: 异常发生时返回的默认值
    :param log_error: 是否记录错误日志
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                return default
        return wrapper
    return decorator
