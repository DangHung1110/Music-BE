from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from typing import Optional, List, Dict, Any
from data.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email, User.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.username == username, User.is_active == True)
        )
        return result.scalars().first()

    async def create(self, user_data: Dict[str, Any]) -> User:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
            full_name=user_data.get("full_name"),
            bio=user_data.get("bio"),
            image_url=user_data.get("image_url"),
            role=user_data.get("role", "user"),
            is_active=user_data.get("is_active", True)
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )
        await self.db.commit()
        return await self.get_by_id(user_id)

    async def delete(self, user_id: int) -> bool:
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        result = await self.db.execute(
            select(User)
            .where(User.is_active == True)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()