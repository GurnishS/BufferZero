import functools
from app.logger import logger
from fastapi import HTTPException
from app.utils.api_error import ApiError
import traceback

def async_handler(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ApiError as e:
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=e.status_code, detail=e.message)
    return wrapper
