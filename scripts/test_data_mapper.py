from uuid import uuid4

from devtools import pprint

from keelhq.db.engine import create_engine
from keelhq.db.session import create_session_factory
from keelhq.repositories.identity import LocalUserRepository
from keelhq.schemas.identity import CreateLocalUser
from keelhq.utils.mappers import LocalUserMapper

engine = create_engine()
SessionLocal = create_session_factory(engine)


def test_local_user_mapper_from_create() -> None:
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


async def test_localUserMapper_toList() -> None:
    async with SessionLocal() as session:
        repository = LocalUserRepository(session)
        users = await repository.list()
        pprint(LocalUserMapper.to_list(users))


async def test_localUserMapper_toDetail() -> None:
    pass
