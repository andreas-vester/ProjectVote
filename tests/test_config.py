"""Tests for the configuration module."""

import pytest

from lvd_fv_form.backend.config import Settings
from lvd_fv_form.backend.main import get_app_settings


def test_settings_load_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that settings are correctly loaded from environment variables."""
    # Arrange
    monkeypatch.setenv("BOARD_MEMBERS", "test1@example.com,test2@example.com")
    monkeypatch.setenv("MAIL_DRIVER", "smtp")
    monkeypatch.setenv("MAIL_FROM", "test@example.com")
    monkeypatch.setenv("MAIL_FROM_NAME", "Test Sender")

    # Act
    settings = Settings()

    # Assert
    assert settings.board_members == "test1@example.com,test2@example.com"
    assert settings.mail_driver == "smtp"
    assert settings.mail_from == "test@example.com"
    assert settings.mail_from_name == "Test Sender"


def test_settings_missing_required_raises_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that a validation error is raised if required settings are missing."""
    # Pydantic settings are cached. To test this properly, we need to clear the cache.
    Settings.model_config["env_file"] = "non_existent_file"  # Avoid loading from .env
    monkeypatch.delenv("BOARD_MEMBERS", raising=False)
    # Also need to invalidate pydantic's internal cache
    Settings.model_rebuild(force=True)

    # Act & Assert
    with pytest.raises(
        ValueError, match="BOARD_MEMBERS environment variable is not set."
    ):
        get_app_settings()

    # Clean up for other tests
    Settings.model_config["env_file"] = ".env"
    Settings.model_rebuild(force=True)
