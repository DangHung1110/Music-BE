from fastapi import APIRouter, Depends, HTTPException
from shared.decorators import async_handler
from shared.responses import OK, CREATED
from business.services.auth_service import AuthService
from presentation.validator.auth_validator import RegisterRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest
from presentation.middleware.auth_middleware import get_current_user
from datetime import datetime
from infrastructure.config.database import get_db, AsyncSession

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()

@router.post("/register")
@async_handler
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await auth_service.register_user(
        db=db,
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name
    )
    return CREATED(message="User registered successfully", metadata=result).send()

@router.post("/login")
@async_handler
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await auth_service.login_user(
        db=db,
        email=request.email,
        password=request.password
    )
    return OK(message="Login successful", metadata=result).send()

@router.get("/profile")
@async_handler
async def get_profile(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user_info = await auth_service.get_user_by_token(db, current_user)
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

@router.post("/forgot-password")
@async_handler
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await auth_service.forgot_password(db, request.email)
    return OK(message="If the email exists, a reset link has been sent", metadata=result).send()

@router.post("/reset-password")
@async_handler
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await auth_service.reset_password(
        db=db,
        reset_token=request.reset_token,
        new_password=request.new_password
    )
    return OK(message="Password reset successfully", metadata=result).send()

@router.post("/logout")
@async_handler
async def logout(current_user: dict = Depends(get_current_user)):
    return OK(
        message="Logout successful",
        metadata={"message": "Please remove token from client storage"}
    ).send()