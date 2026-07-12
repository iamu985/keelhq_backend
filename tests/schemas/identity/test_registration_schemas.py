"""Tests for the registration request schema.

Responsibility:
- Validate that RegisterNewUserRequest enforces username, email, password
  complexity, and password confirmation rules.
"""

import pytest
from pydantic import SecretStr, ValidationError

from keelhq.schemas.identity.registration_schemas import RegisterNewUserRequest

VALID_USERNAME = "valid_user"
VALID_EMAIL = "user@example.com"
VALID_FIRST_NAME = "Frank"
VALID_LAST_NAME = "Castle"
VALID_PASSWORD = "Secret123!"


def _make_request(
    username: str = VALID_USERNAME,
    email: str = VALID_EMAIL,
    first_name: str = VALID_FIRST_NAME,
    last_name: str | None = VALID_LAST_NAME,
    password: str = VALID_PASSWORD,
    password_confirm: str = VALID_PASSWORD,
) -> RegisterNewUserRequest:
    """Build a RegisterNewUserRequest with the requested overrides."""
    return RegisterNewUserRequest(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=SecretStr(password),
        password_confirm=SecretStr(password_confirm),
    )


# TODO: add unit tests for edge cases such as unicode or boundary whitespace handling.
def test_valid_register_new_user_request() -> None:
    """A fully valid payload should instantiate successfully."""
    request = _make_request()

    assert request.username == VALID_USERNAME
    assert str(request.email) == VALID_EMAIL
    assert request.first_name == VALID_FIRST_NAME
    assert request.last_name == VALID_LAST_NAME
    assert request.password.get_secret_value() == VALID_PASSWORD
    assert request.password_confirm.get_secret_value() == VALID_PASSWORD


@pytest.mark.parametrize("username", ["short", "x" * 16])
def test_username_length_validation(username: str) -> None:
    """Usernames shorter than 8 or longer than 15 characters are rejected."""
    with pytest.raises(ValidationError):
        _make_request(username=username)


@pytest.mark.parametrize("username", ["invalid user", "user@example"])
def test_username_pattern_validation(username: str) -> None:
    """Usernames containing characters outside the allowed set are rejected."""
    with pytest.raises(ValidationError):
        _make_request(username=username)


def test_username_cannot_start_with_digit() -> None:
    """Usernames starting with a number are rejected by the custom validator."""
    with pytest.raises(ValidationError) as exc_info:
        _make_request(username="1valid_user")

    assert "username cannot start with a number" in str(exc_info.value)


def test_invalid_email() -> None:
    """Non-email strings are rejected by EmailStr."""
    with pytest.raises(ValidationError):
        _make_request(email="not-an-email")


@pytest.mark.parametrize(
    "password",
    [
        "nouppercase1!",  # missing uppercase
        "NoDigits!!",  # missing digit
        "NoSpecial123",  # missing special character
    ],
)
def test_password_must_contain_required_character_types(password: str) -> None:
    """Passwords missing uppercase, digit, or special character are rejected."""
    with pytest.raises(ValidationError):
        _make_request(password=password, password_confirm=password)


def test_passwords_must_match() -> None:
    """The model validator rejects mismatched password and confirmation."""
    with pytest.raises(ValidationError) as exc_info:
        _make_request(password_confirm="Different123!")

    assert "passwords do not match" in str(exc_info.value)
