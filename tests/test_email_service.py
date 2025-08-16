"""Tests for the email service module."""

import pytest
from pytest_mock import MockerFixture

from lvd_fv_form.backend.email_service import send_email


@pytest.mark.asyncio
async def test_send_email(mocker: MockerFixture) -> None:
    """Test that send_email calls the mailer with the correct parameters."""
    # Arrange
    mock_mailer = mocker.patch("lvd_fv_form.backend.email_service.get_mailer")
    mock_send = mocker.AsyncMock()
    mock_mailer.return_value.send_message = mock_send

    recipients = ["test@example.com"]
    subject = "Test Subject"
    template_body = {"key": "value"}
    template_name = "test_template.html"

    # Act
    await send_email(recipients, subject, template_body, template_name)

    # Assert
    mock_send.assert_called_once()
    call_args = mock_send.call_args[0][0]
    assert call_args.recipients == recipients
    assert call_args.subject == subject
    assert call_args.template_body == template_body
    assert mock_send.call_args[1]["template_name"] == template_name
