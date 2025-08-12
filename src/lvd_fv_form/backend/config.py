"""Configuration for the application, loaded from environment variables."""

from pydantic import EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Board members - comma-separated string
    board_members: str | None = None

    # Mail settings
    mail_username: str = ""
    mail_password: SecretStr | None = None
    mail_from: EmailStr = "noreply@example.com"
    mail_port: int = 587
    mail_server: str = "smtp.example.com"
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    mail_from_name: str = "LVD-FV Funding Portal"
    mail_driver: str = "console"

    # Database settings
    db_echo: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
