from fastapi import APIRouter, Depends, HTTPException
from shared.decorators import async_handler
from shared.responses import OK, CREATED
from business.services.auth_service import AuthService
from presentation.validators.auth_validator import RegisterRequest, LoginRequest, ChangePasswordRequest
from presentation.middleware.auth_middleware import get_current_user
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()

@router.post("/register")
@async_handler
async def register(request: RegisterRequest):
    result = await auth_service.register_user(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name
    )
    return CREATED(message="User registered successfully", metadata=result).send()

@router.post("/login")
@async_handler
async def login(request: LoginRequest):
    result = await auth_service.login_user(
        email=request.email,
        password=request.password
    )
    return OK(message="Login successful", metadata=result).send()

@router.get("/profile")
@async_handler
async def get_profile(current_user: dict = Depends(get_current_user)):
    user_info = await auth_service.get_user_by_token(current_user)
    return OK(message="Profile retrieved successfully", metadata={"user": user_info}).send()

@router.post("/refresh")
@async_handler
async def refresh_token(current_user: dict = Depends(get_current_user)):
    token_payload = {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "username": current_user["username"]
    }
    new_token = auth_service.create_access_token(token_payload)
    return OK(
        message="Token refreshed successfully",
        metadata={
            "access_token": new_token,
            "token_type": "bearer",
            "expires_in": auth_service.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    ).send()

@router.post("/change-password")
@async_handler
async def change_password(request: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    user = await auth_service.user_repo.get_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not auth_service.verify_password(request.current_password, user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    new_hashed_password = auth_service.hash_password(request.new_password)
    await auth_service.user_repo.update(user.id, {
        "password": new_hashed_password,
        "updated_at": datetime.utcnow()
    })
    return OK(message="Password changed successfully", metadata={}).send()

@router.post("/logout")
@async_handler
async def logout(current_user: dict = Depends(get_current_user)):
    return OK(
        message="Logout successful",
        metadata={"message": "Please remove token from client storage"}
    ).send()
