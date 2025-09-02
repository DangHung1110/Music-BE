from fastapi import APIRouter, Depends, Path, Query
from shared.decorators import async_handler
from shared.responses import OK, CREATED
from business.services.users_service import UsersService
from presentation.validator.user_validator import (
    CreateUserRequest,
    UpdateUserRequest,
    ListUsersQuery,
)
from presentation.middleware.auth_middleware import (
    get_current_user,
    require_admin,
    require_self_or_admin,
)
from infrastructure.config.database import get_db, AsyncSession


router = APIRouter(prefix="/users", tags=["Users"])
users_service = UsersService()


@router.get("/all")
@async_handler
async def get_all_users(
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    users = await users_service.get_all_users(db)
    return OK(message="Fetched all users", metadata={"users": users}).send()


@router.get("/me")
@async_handler
async def get_me(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await users_service.get_user_by_id(db, current_user["user_id"]) 
    return OK(message="Fetched profile", metadata={"user": result}).send()


@router.get("")
@async_handler
async def list_users(
    q: ListUsersQuery = Depends(),
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await users_service.list_users(db, limit=q.limit, offset=q.offset)
    return OK(message="Fetched users", metadata=result).send()


@router.get("/{user_id}")
@async_handler
async def get_user(
    user_id: int = Path(..., ge=1),
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await users_service.get_user_by_id(db, user_id)
    return OK(message="Fetched user", metadata={"user": result}).send()


@router.post("")
@async_handler
async def create_user(
    req: CreateUserRequest,
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await users_service.create_user(
        db=db,
        username=req.username,
        email=req.email,
        password=req.password,
        full_name=req.full_name,
        bio=req.bio,
        image_url=req.image_url,
        role=req.role or "user",
        is_active=req.is_active if req.is_active is not None else True,
    )
    return CREATED(message="User created", metadata={"user": user}).send()


@router.patch("/{user_id}")
@async_handler
async def update_user(
    user_id: int = Path(..., ge=1),
    req: UpdateUserRequest = None,
    db: AsyncSession = Depends(get_db),
    _auth: dict = Depends(require_self_or_admin),
):
    update_payload = req.dict(exclude_unset=True)
    result = await users_service.update_user(db, user_id, update_payload)
    return OK(message="User updated", metadata={"user": result}).send()


@router.delete("/{user_id}")
@async_handler
async def delete_user(
    user_id: int = Path(..., ge=1),
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await users_service.delete_user(db, user_id)
    return OK(message="User deleted", metadata=result).send()



