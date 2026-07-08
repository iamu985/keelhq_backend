from uuid import uuid4

from devtools import pprint

from app.db.session import SessionLocal
from app.repositories.identity import LocalUserRepository
from app.schemas.identity import CreateLocalUser
from app.utils.mappers import LocalUserMapper


def test_local_user_mapper_from_create():
    contract = CreateLocalUser(
        email="some@example.com",
        username="some123",
        first_name="some",
        password_hash=uuid4().hex,
        middle_name=None,
        last_name=None,
    )

    result = LocalUserMapper.from_create(contract)
    pprint(result.username)


async def test_localUserMapper_toList():
    async with SessionLocal() as session:
        repository = LocalUserRepository(session)
        users = await repository.list()
        pprint(LocalUserMapper.to_list(users))


async def test_localUserMapper_toDetail():
    pass
