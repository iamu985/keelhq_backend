from collections.abc import Sequence

from keelhq.db.models import LocalUser
from keelhq.schemas.identity import CreateLocalUser, LocalUserDetail


class LocalUserMapper:
    @staticmethod
    def from_create(dto: CreateLocalUser) -> LocalUser:
        return LocalUser(**dto.model_dump(exclude_none=True, exclude_unset=True))

    @staticmethod
    def to_detail(user: LocalUser) -> LocalUserDetail:
        return LocalUserDetail(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            created_at=user.created_at.isoformat(),
        )

    @staticmethod
    def to_list(users: Sequence[LocalUser]) -> list[LocalUserDetail]:
        local_users = []
        for user in users:
            user_detail = LocalUserDetail(
                id=user.id,
                email=user.email,
                username=user.username,
                first_name=user.first_name,
                middle_name=user.middle_name,
                last_name=user.last_name,
                created_at=user.created_at.isoformat(),
            )
            local_users.append(user_detail)

        return local_users
