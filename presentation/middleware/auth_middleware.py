from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from business.services.auth_service import AuthService
from shared.exceptions import AuthFailureError, ForbiddenError, NotFoundError
from infrastructure.config.database import get_db, AsyncSession
from data.repositories.user_repository import UserRepository

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

# Role-based access dependencies
async def require_admin(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user.get("user_id"))
    if not user:
        raise NotFoundError("User not found")
    if user.role != "admin":
        raise ForbiddenError("Admin access required")
    return {"auth_user": user.to_dict()}

async def require_self_or_admin(user_id: int, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    user_repo = UserRepository(db)
    auth_user = await user_repo.get_by_id(current_user.get("user_id"))
    if not auth_user:
        raise NotFoundError("User not found")
    if auth_user.role == "admin" or auth_user.id == user_id:
        return {"auth_user": auth_user.to_dict()}
    raise ForbiddenError("Not allowed. Must be owner or admin")