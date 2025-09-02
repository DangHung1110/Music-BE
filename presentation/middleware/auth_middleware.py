from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from business.services.auth_service import AuthService
from shared.exceptions import AuthFailureError, ForbiddenError, NotFoundError
from infrastructure.config.database import get_db, AsyncSession
from data.repositories.user_repository import UserRepository
from infrastructure.cache.redis_service import RedisService

security = HTTPBearer()
auth_service = AuthService()
redis_service = RedisService()

# verify token middleware with Redis session validation
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        
        # Verify token and check if blacklisted
        payload = await auth_service.verify_session_token(token)
        
        # Update session activity if session_id is available
        session_id = payload.get("session_id")
        if session_id:
            await redis_service.update_session_activity(session_id)
        
        return payload
    except Exception as e:
        raise AuthFailureError("Invalid authentication credentials")

# Optional authentication (không bắt buộc login)
async def get_current_user_optional(request: Request) -> Optional[dict]:
    try:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        
        # Check if token is blacklisted
        if await redis_service.is_token_blacklisted(token):
            return None
        
        payload = auth_service.verify_token(token)
        return payload
    except Exception:
        return None

# Role-based access dependencies
async def require_admin(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    user_id = current_user.get("user_id")
    
    # Try to get user from cache first
    cached_user = await redis_service.get_cached_user_data(user_id)
    if cached_user:
        if cached_user.get("role") != "admin":
            raise ForbiddenError("Admin access required")
        return {"auth_user": cached_user}
    
    # Get from database if not cached
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise NotFoundError("User not found")
    
    if user.role != "admin":
        raise ForbiddenError("Admin access required")
    
    user_dict = user.to_dict()
    # Cache the user data
    await redis_service.cache_user_data(user_id, user_dict)
    
    return {"auth_user": user_dict}

async def require_self_or_admin(user_id: int, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    auth_user_id = current_user.get("user_id")
    
    # Try to get user from cache first
    cached_user = await redis_service.get_cached_user_data(auth_user_id)
    if cached_user:
        if cached_user.get("role") == "admin" or cached_user.get("id") == user_id:
            return {"auth_user": cached_user}
        raise ForbiddenError("Not allowed. Must be owner or admin")
    
    # Get from database if not cached
    user_repo = UserRepository(db)
    auth_user = await user_repo.get_by_id(auth_user_id)
    if not auth_user:
        raise NotFoundError("User not found")
    
    if auth_user.role == "admin" or auth_user.id == user_id:
        user_dict = auth_user.to_dict()
        await redis_service.cache_user_data(auth_user_id, user_dict)
        return {"auth_user": user_dict}
    
    raise ForbiddenError("Not allowed. Must be owner or admin")