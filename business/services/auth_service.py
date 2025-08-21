import jwt
import os
import secrets
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Dict, Any
from shared.exceptions import AuthFailureError, ConflictRequestError, NotFoundError
from data.repositories.user_repository import UserRepository
from infrastructure.external.email_service import EmailService


class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.user_repo = UserRepository()
        self.email_service = EmailService()
        self.SECRET_KEY = os.getenv("JWT_SECRET", "your-fallback-secret-key")
        self.ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "60"))

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def generate_secure_token(self) -> str:
        return secrets.token_urlsafe(32)

    def create_access_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def create_reset_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.RESET_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "reset"})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("type") != token_type:
                raise AuthFailureError(f"Invalid token type. Expected {token_type}")
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthFailureError("Token has expired")
        except jwt.JWTError:
            raise AuthFailureError("Invalid token")

    async def register_user(self, username: str, email: str, password: str, full_name: str = None) -> Dict[str, Any]:
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ConflictRequestError("Email already registered")

        existing_username = await self.user_repo.get_by_username(username)
        if existing_username:
            raise ConflictRequestError("Username already taken")

        hashed_password = self.hash_password(password)

        user_data = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "full_name": full_name,
            "is_active": True
        }

        user = await self.user_repo.create(user_data)

        token_payload = {"user_id": user.id, "email": user.email, "username": user.username}
        access_token = self.create_access_token(token_payload)

        return {
            "user": user.to_dict(),
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        user = await self.user_repo.get_by_email(email)
        if not user or not self.verify_password(password, user.password):
            raise AuthFailureError("Invalid email or password")
        if not user.is_active:
            raise AuthFailureError("Account has been deactivated")

        token_payload = {"user_id": user.id, "email": user.email, "username": user.username}
        access_token = self.create_access_token(token_payload)

        return {
            "user": user.to_dict(),
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    async def forgot_password(self, email: str) -> Dict[str, Any]:
        user = await self.user_repo.get_by_email(email)
        if not user or not user.is_active:
            return {"message": "If the email exists, a reset link has been sent."}

        reset_token = self.create_reset_token({"user_id": user.id, "email": user.email})
        reset_expires = datetime.utcnow() + timedelta(minutes=self.RESET_TOKEN_EXPIRE_MINUTES)

        await self.user_repo.update(user.id, {"reset_token": reset_token, "reset_expiration": reset_expires})

        try:
            await self.email_service.send_reset_password_email(email, reset_token, user.full_name or user.username)
        except Exception as e:
            print(f"Failed to send reset email: {e}")

        return {"message": "If the email exists, a reset link has been sent."}

    async def reset_password(self, reset_token: str, new_password: str) -> Dict[str, Any]:
        try:
            payload = self.verify_token(reset_token, "reset")
            user_id = payload.get("user_id")
            if not user_id:
                raise AuthFailureError("Invalid reset token")

            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise AuthFailureError("Invalid reset token")

            if user.reset_token != reset_token or not user.reset_expiration or user.reset_expiration < datetime.utcnow():
                raise AuthFailureError("Reset token has expired or is invalid")

            hashed_password = self.hash_password(new_password)
            await self.user_repo.update(user.id, {"password": hashed_password, "reset_token": None, "reset_expiration": None})

            try:
                await self.email_service.send_password_changed_notification(user.email, user.full_name or user.username)
            except Exception as e:
                print(f"Failed to send password changed notification: {e}")

            return {"message": "Password has been reset successfully"}

        except jwt.ExpiredSignatureError:
            raise AuthFailureError("Reset token has expired")
        except jwt.JWTError:
            raise AuthFailureError("Invalid reset token")

    async def get_user_by_token(self, token_payload: Dict[str, Any]) -> Dict[str, Any]:
        user_id = token_payload.get("user_id")
        if not user_id:
            raise AuthFailureError("Invalid token payload")

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        return user.to_dict()
