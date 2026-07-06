from fastapi import APIRouter
from pydantic import Secret
from app import repositories
from app.db.models.identity.local_user import LocalUser
from app.schemas.identity import CreateLocalUser, LocalUserDetail
from app.repositories.identity import LocalUserRepository
from app.db.session import SessionLocal

router = APIRouter(prefix="/local-user")


@router.post("/create")
async def create_local_user(payload: CreateLocalUser):
    async with SessionLocal() as session:
        repository = LocalUserRepository(session=session)
        user_to_create = LocalUser(
            email=payload.email,
            username=payload.username,
            password_hash=payload.password_hash.hex,
            first_name=payload.first_name,
            middle_name=payload.middle_name,
            last_name=payload.last_name,
        )
        created_user = await repository.create(user_to_create)
        if created_user:
            await session.commit()
            return LocalUserDetail(
                id=created_user.id,
                email=created_user.email,
                username=created_user.username,
                first_name=created_user.first_name,
                middle_name=created_user.middle_name,
                last_name=created_user.last_name,
                created_at=created_user.created_at.isoformat(),
                is_active=created_user.is_active,
                is_superuser=created_user.is_superuser,
            )
        await session.rollback()
        return {}
