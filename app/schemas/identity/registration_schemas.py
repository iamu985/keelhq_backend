import re

from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator, model_validator


class RegisterNewUserRequest(BaseModel):
    """
    Use:
    This schema is used when sending data from register page to the backend api.
    """

    username: str = Field(min_length=8, max_length=15, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    first_name: str
    last_name: str | None = None
    password: SecretStr
    password_confirm: SecretStr

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if v[0].isdigit():
            raise ValueError("username cannot start with a number.")
        return v

    @field_validator("password", "password_confirm")
    @classmethod
    def validate_password(cls, v: SecretStr) -> SecretStr:
        secret = v.get_secret_value()
        if not re.search(r"[A-Z]", secret):
            raise ValueError("password must contain at least one uppercase letter.")
        if not re.search(r"[0-9]", secret):
            raise ValueError("password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', secret):
            raise ValueError("password must contain at least one special character.")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterNewUserRequest":
        if self.password != self.password_confirm:
            raise ValueError("passwords do not match.")
        return self


class RegistrationSuccessfulResponse(BaseModel):
    """
    Response schema for successfully registering user.
    Not inteded for API and only meant for frontend
    """

    message: str
    email: EmailStr
    verification_required: bool
