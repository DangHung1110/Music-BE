from fastapi import Response
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

class SuccessResponse:
    def __init__(
        self,
        message: str = "OK",
        status_code: int = 200,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.status = status
        self.metadata = metadata or {}

    def send(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content={
                "status": self.status,
                "code": self.status_code,
                "message": self.message,
                "metadata": self.metadata
            }
        )

class OK(SuccessResponse):
    def __init__(self, message: str = "OK", metadata: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=200, metadata=metadata)

class CREATED(SuccessResponse):
    def __init__(
        self,
        message: str = "Created",
        metadata: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, status_code=201, metadata=metadata)
        self.options = options or {}