from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            # Handle custom HTTP exceptions
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "status": "error",
                    "code": exc.status_code,
                    "message": exc.detail,
                }
            )
        except Exception as exc:
            # Handle unexpected exceptions
            logger.error(f"Unexpected error: {str(exc)}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error", 
                    "code": 500,
                    "message": "Internal Server Error",
                }
            )
