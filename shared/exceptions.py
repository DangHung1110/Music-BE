from fastapi import HTTPException
from typing import Dict, Any, Optional

class ErrorResponse(HTTPException):
    """Base error response class"""
    def __init__(self, message: str, status_code: int):
        super().__init__(status_code=status_code, detail=message)
        self.message = message
        self.status_code = status_code

class ConflictRequestError(ErrorResponse):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message=message, status_code=409)

class BadRequestError(ErrorResponse):
    def __init__(self, message: str = "Bad Request"):
        super().__init__(message=message, status_code=400)

class AuthFailureError(ErrorResponse):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, status_code=401)

class NotFoundError(ErrorResponse):
    def __init__(self, message: str = "Not Found"):
        super().__init__(message=message, status_code=404)

class ForbiddenError(ErrorResponse):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, status_code=403)

class InternalServerError(ErrorResponse):
    def __init__(self, message: str = "Internal Server Error"):
        super().__init__(message=message, status_code=500)
