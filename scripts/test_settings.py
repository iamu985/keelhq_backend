from keelhq.core.config import settings


def test_settings() -> None:
    """Verify the application settings load without validation errors."""
    assert settings is not None
    assert settings.database is not None
