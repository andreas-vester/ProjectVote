"""Tests for the email service module."""

import pytest
from pydantic import SecretStr
from pytest_mock import MockerFixture

from projectvote.backend.config import Settings
from projectvote.backend.email_service import get_mailer, send_email


@pytest.mark.asyncio
async def test_send_email(mocker: MockerFixture) -> None:
    """Test that send_email calls the mailer with the correct parameters."""
    # Arrange
    mock_mailer = mocker.patch("projectvote.backend.email_service.get_mailer")
    mock_send = mocker.AsyncMock()
    mock_mailer.return_value.send_message = mock_send

    recipients = ["test@example.com"]
    subject = "Test Subject"
    template_body = {"key": "value"}
    template_name = "test_template.html"
    settings = Settings(board_members="test1@example.com,test2@example.com")

    # Act
    await send_email(recipients, subject, template_body, template_name, settings)

    # Assert
    mock_send.assert_called_once()
    call_args = mock_send.call_args[0][0]
    assert call_args.recipients == recipients
    assert call_args.subject == subject
    assert call_args.template_body == template_body
    assert mock_send.call_args[1]["template_name"] == template_name


def test_get_mailer_with_ds716_local() -> None:
    """Test get_mailer with ds716.local server (another mailhog variant)."""
    settings = Settings(
        board_members="test@example.com",
        mail_server="ds716.local",
        mail_driver="smtp",
    )
    mailer = get_mailer(settings)
    assert mailer is not None


def test_get_mailer_with_password() -> None:
    """Test get_mailer when password is provided."""
    settings = Settings(
        board_members="test@example.com",
        mail_server="smtp.gmail.com",
        mail_driver="smtp",
        mail_password=SecretStr("test_password"),
    )
    mailer = get_mailer(settings)
    assert mailer is not None


def test_get_mailer_without_password_non_mailhog() -> None:
    """Test get_mailer raises ValueError when password is missing."""
    settings = Settings(
        board_members="test@example.com",
        mail_server="smtp.gmail.com",
        mail_driver="smtp",
        mail_password=None,
    )
    with pytest.raises(
        ValueError, match="MAIL_PASSWORD environment variable must be set"
    ):
        get_mailer(settings)


def test_get_mailer_console_driver() -> None:
    """Test get_mailer with console driver (doesn't require password)."""
    settings = Settings(
        board_members="test@example.com",
        mail_server="smtp.example.com",
        mail_driver="console",
        mail_password=None,
    )
    mailer = get_mailer(settings)
    assert mailer is not None


@pytest.mark.asyncio
async def test_send_email_success(mocker: MockerFixture) -> None:
    """Test send_email when email sends successfully."""
    settings = Settings(
        board_members="test@example.com",
        mail_server="localhost",
    )

    # Mock the FastMail instance and its send_message method
    mock_fast_mail = mocker.Mock()
    mock_fast_mail.send_message = mocker.AsyncMock()
    mocker.patch(
        "projectvote.backend.email_service.get_mailer", return_value=mock_fast_mail
    )

    # Mock logger
    mock_logger = mocker.patch("projectvote.backend.email_service.logger")

    await send_email(
        recipients=["test@example.com"],
        subject="Test Subject",
        template_body={"key": "value"},
        template_name="test_template.html",
        settings=settings,
    )

    # Verify send_message was called
    mock_fast_mail.send_message.assert_called_once()

    # Verify logger.info was called
    mock_logger.info.assert_called_once()


@pytest.mark.asyncio
async def test_send_email_failure(mocker: MockerFixture) -> None:
    """Test send_email when email sending fails."""
    settings = Settings(
        board_members="test@example.com",
        mail_server="localhost",
    )

    # Mock the FastMail instance to raise an exception
    mock_fast_mail = mocker.Mock()
    mock_fast_mail.send_message = mocker.AsyncMock(side_effect=Exception("Email error"))
    mocker.patch(
        "projectvote.backend.email_service.get_mailer", return_value=mock_fast_mail
    )

    # Mock logger
    mock_logger = mocker.patch("projectvote.backend.email_service.logger")

    # Call send_email - it should not raise but should log the exception
    await send_email(
        recipients=["test@example.com"],
        subject="Test Subject",
        template_body={"key": "value"},
        template_name="test_template.html",
        settings=settings,
    )

    # Verify logger.exception was called
    mock_logger.exception.assert_called_once()
