from functools import wraps
from fastapi import Request, HTTPException
import asyncio
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

def async_handler(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    return wrapper