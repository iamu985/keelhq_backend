from pwdlib import PasswordHash
from pydantic import SecretStr


class PasswordService:
    def __init__(self) -> None:
        self.hasher = PasswordHash.recommended()

    def hash_password(self, password: SecretStr) -> str:
        return self.hasher.hash(password=password.get_secret_value())

    def verify_password(self, password: SecretStr, hashed_password: str) -> bool:
        return self.hasher.verify(password=password.get_secret_value(), hash=hashed_password)
