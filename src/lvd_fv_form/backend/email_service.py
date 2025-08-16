"""Email sending service for the application."""

import logging
from typing import Any

from aiosmtplib.errors import SMTPConnectError
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from .config import Settings

logger = logging.getLogger(__name__)


def get_mailer() -> FastMail:
    """Return a FastMail instance based on application settings.

    Returns
    -------
    FastMail
        A FastMail instance.

    Raises
    ------
    ValueError
        If the MAIL_PASSWORD environment variable is not set.
    """
    settings = Settings()
    if settings.mail_password is None:
        raise ValueError("MAIL_PASSWORD environment variable is not set.")

    conf = ConnectionConfig(
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_FROM=settings.mail_from,
        MAIL_PORT=settings.mail_port,
        MAIL_SERVER=settings.mail_server,
        MAIL_STARTTLS=settings.mail_starttls,
        MAIL_SSL_TLS=settings.mail_ssl_tls,
        MAIL_FROM_NAME=settings.mail_from_name,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER="./src/lvd_fv_form/backend/templates/email",
    )
    return FastMail(conf)


async def send_email(
    recipients: list[EmailStr],
    subject: str,
    template_body: dict[str, Any],
    template_name: str,
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
    """
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=template_body,
        subtype=MessageType.html,
    )
    mailer = get_mailer()
    try:
        await mailer.send_message(message, template_name=template_name)
        logger.info("Email sent to %s with subject '%s'", recipients, subject)
    except SMTPConnectError:
        logger.exception("Failed to send email to %s", recipients)
