from uuid import UUID
from fastapi import APIRouter
from pydantic import Secret
from app import repositories
from app.db.models.identity.local_user import LocalUser
from app.schemas.identity import CreateLocalUser, LocalUserDetail
from app.repositories.identity import LocalUserRepository
from app.db.session import SessionLocal
from app.utils.mappers import LocalUserMapper

router = APIRouter(prefix="/local-user")


@router.post("/create")
async def create_local_user(payload: CreateLocalUser):
    async with SessionLocal() as session:
        repository = LocalUserRepository(session=session)
        user_to_create = LocalUserMapper.from_create(payload)
        created_user = await repository.create(user_to_create)
        if created_user:
            await session.commit()
            response = LocalUserMapper.to_detail(created_user)
            return response
        await session.rollback()
        return {}


@router.get("/list")
async def list_local_users():
    async with SessionLocal() as session:
        repository = LocalUserRepository(session)
        users = await repository.list()
        return LocalUserMapper.to_list(users)


@router.get("/{user_id}/detail")
async def get_user_detail_by_id(user_id: str):
    async with SessionLocal() as session:
        repository = LocalUserRepository(session)
        user = await repository.get(user_id=UUID(user_id))
        if user:
            return LocalUserMapper.to_detail(user)
        else:
            return {}
