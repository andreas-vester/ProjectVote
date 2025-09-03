"""Configuration for the application, loaded from environment variables."""

from pathlib import Path

from pydantic import EmailStr, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Board members - comma-separated string
    board_members: str | None = None

    @field_validator("board_members")
    @classmethod
    def board_members_must_be_set(cls, v: str | None) -> str:
        """Validate that board_members is not empty."""
        if v is None or not v.strip():
            raise ValueError("BOARD_MEMBERS environment variable is not set.")
        return v

    # Mail settings
    mail_username: str = ""
    mail_password: SecretStr | None = None
    mail_from: EmailStr = "noreply@example.com"
    mail_port: int = 1025
    mail_server: str = "localhost"
    mail_starttls: bool = False
    mail_ssl_tls: bool = False
    mail_from_name: str = "ProjectVote"
    mail_driver: str = "smtp"

    # Application settings
    frontend_url: str = "http://localhost:5173"

    # Database settings
    db_echo: bool = True

    # This assumes that config.py is in src/lvd_fv_form/backend
    # So the project root is 4 levels up.
    project_root: Path = Path(__file__).resolve().parent.parent.parent.parent

    model_config = SettingsConfigDict(
        env_file=(
            project_root / ".env",
            project_root / ".env.local",
        ),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
