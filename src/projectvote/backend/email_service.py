"""Email sending service for the application."""

import logging
from pathlib import Path
from typing import Any

from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema,
    MessageType,
    NameEmail,
)
from pydantic import EmailStr, SecretStr

from .config import Settings

logger = logging.getLogger(__name__)


def get_mailer(settings: Settings) -> FastMail:
    """Return a FastMail instance based on application settings.

    Returns
    -------
    FastMail
        A FastMail instance.

    Raises
    ------
    ValueError
        If the MAIL_PASSWORD environment variable is not set for SMTP driver.

    """
    if settings.mail_driver == "smtp" and not settings.mail_password:
        raise ValueError(
            "MAIL_PASSWORD environment variable must be set for smtp driver."
        )

    password = ""
    if settings.mail_password:
        password = settings.mail_password.get_secret_value()

    conf = ConnectionConfig(
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=SecretStr(password),
        MAIL_FROM=settings.mail_from,
        MAIL_PORT=settings.mail_port,
        MAIL_SERVER=settings.mail_server,
        MAIL_STARTTLS=settings.mail_starttls,
        MAIL_SSL_TLS=settings.mail_ssl_tls,
        MAIL_FROM_NAME=settings.mail_from_name,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER=Path("./src/projectvote/backend/templates/email"),
    )
    return FastMail(conf)


async def send_email(
    recipients: list[EmailStr],
    subject: str,
    template_body: dict[str, Any],
    template_name: str,
    settings: Settings,
) -> None:
    """Send an email to a list of recipients.

    Parameters
    ----------
    recipients : list[EmailStr]
        A list of email addresses.
    subject : str
        The subject of the email.
    template_body : dict[str, Any]
        A dictionary with the template variables.
    template_name : str
        The name of the HTML template to use.
    settings : Settings
        The application settings.
    """
    message = MessageSchema(
        subject=subject,
        recipients=[NameEmail(name=r, email=r) for r in recipients],
        template_body=template_body,
        subtype=MessageType.html,
    )
    mailer = get_mailer(settings)
    try:
        await mailer.send_message(message, template_name=template_name)
        logger.info("Email sent to %s with subject '%s'", recipients, subject)
    except Exception:
        logger.exception(
            "An unexpected error occurred while sending email to %s", recipients
        )
