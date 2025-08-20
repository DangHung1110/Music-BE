from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from business.services.auth_service import AuthService
from shared.exceptions import AuthFailureError

security = HTTPBearer()
auth_service = AuthService()

# verify token and get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try: 
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        return payload
    except Exception:
        raise AuthFailureError("Invalid authentication credentials!")

