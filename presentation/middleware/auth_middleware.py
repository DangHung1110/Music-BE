from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from business.services.auth_service import AuthService
from shared.exceptions import AuthFailureError

security = HTTPBearer()
auth_service = AuthService()

# verify token middleware
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        return payload
    except Exception:
        raise AuthFailureError("Invalid authentication credentials")

# Optional authentication (không bắt buộc login)
async def get_current_user_optional(request: Request) -> Optional[dict]:
    try:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        payload = auth_service.verify_token(token)
        return payload
    except Exception:
        return None