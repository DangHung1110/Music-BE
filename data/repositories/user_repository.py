from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from typing import Optional, List, Dict, Any
from data.models.user import User
from infrastructure.config.database import get_db

class UserRepository:
    def __init_(self):
        pass
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        async with get_db() as session:
            result = await session.execute(
                select(User).where(User.id == user_id, User.is_active == True)
            )
            return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        async with get_db() as session:
            result = await session.execute(
                select(User).where(User.email == email, User.is_active == True)
            )
            return result.scalar_one_or_none()
    
    async def create(self, user_data: Dict[str, Any]) -> User:
        async with get_db() as session:
            # Create user instance
            user = User(
                email=user_data["email"],
                password=user_data["password"],
                name=user_data["name"],
                avatar_url=user_data.get("avatar_url"),
                role=user_data.get("role", "user"),
                is_verified=user_data.get("is_verified", False)
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)  # Refresh để lấy ID
            
            return user
    
    async def update(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        async with get_db as session:
            await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(**update_data)
            )
            await session.commit()
            
            return await self.get_by_id(user_id)
    
    async def delete(self, user_id: int) -> bool:
        async with get_db as session:
            result = await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(is_active=False)
            )
            await session.commit()
            return result.rowcount > 0
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        async with get_db as session:
            result = await session.execute(
                select(User)
                .where(User.is_active == True)
                .offset(offset)
                .limit(limit)
            )
            return result.scalars().all()
