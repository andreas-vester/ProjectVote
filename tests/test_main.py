"""Tests for the ProjectVote application."""

from http import HTTPStatus

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from projectvote.backend.config import Settings
from projectvote.backend.main import get_board_members
from projectvote.backend.models import (
    Application,
    ApplicationStatus,
    VoteOption,
    VoteRecord,
    VoteStatus,
)

from .conftest import EMAILS_SENT_FOR_FINAL_DECISION, TEST_BOARD_MEMBERS


@pytest.mark.asyncio
async def test_read_root(client: AsyncClient) -> None:
    """Test that the root endpoint returns a welcome message."""
    response = await client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Welcome to the Funding Application API"}


@pytest.mark.asyncio
async def test_create_application(
    client: AsyncClient, session: AsyncSession, mocker: MockerFixture
) -> None:
    """Test creating a new application and associated vote records."""
    send_email_mock = mocker.patch(
        "projectvote.backend.main.send_email", new_callable=mocker.AsyncMock
    )
    application_data = {
        "first_name": "Test",
        "last_name": "User",
        "applicant_email": "test.user@example.com",
        "department": "Test Department",
        "project_title": "Test Project",
        "project_description": "A test project description.",
        "costs": 123.45,
    }
    response = await client.post("/applications", data=application_data)
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data["message"] == "Application submitted successfully"
    assert "application_id" in response_data

    # Verify vote records were created by the API endpoint
    result = await session.execute(
        select(VoteRecord).where(
            VoteRecord.application_id == response_data["application_id"]
        )
    )
    vote_records = result.scalars().all()
    assert len(vote_records) == len(TEST_BOARD_MEMBERS)
    for record in vote_records:
        assert record.token is not None
        actual_status = getattr(record, "vote_status", None)
        if actual_status is not None and hasattr(actual_status, "value"):
            actual_status = actual_status.value
        assert actual_status == VoteStatus.PENDING.value

    # Verify that email sending was triggered
    assert send_email_mock.call_count == len(TEST_BOARD_MEMBERS)

    # Verify that the email body contains the correct data
    first_call_args = send_email_mock.call_args_list[0]
    template_body = first_call_args.kwargs["template_body"]
    assert template_body["first_name"] == application_data["first_name"]
    assert template_body["last_name"] == application_data["last_name"]
    assert template_body["project_title"] == application_data["project_title"]
    assert template_body["costs"] == application_data["costs"]
    assert "vote_url" in template_body


@pytest.mark.parametrize(
    ("scenario", "token_to_use", "expected_status_code", "expected_detail"),
    [
        (
            "Success",
            "VALID_TOKEN",
            HTTPStatus.OK,
            None,
        ),
        (
            "Invalid Token",
            "invalid-token-123",
            HTTPStatus.NOT_FOUND,
            "Invalid or expired token.",
        ),
        (
            "Vote Already Cast",
            "ALREADY_CAST_TOKEN",
            HTTPStatus.BAD_REQUEST,
            "This vote has already been cast.",
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_vote_details_scenarios(
    client: AsyncClient,
    session: AsyncSession,
    scenario: str,  # noqa: ARG001
    token_to_use: str,
    expected_status_code: int,
    expected_detail: str | None,
) -> None:
    """Test fetching vote details under different scenarios."""
    # --- Setup: Create a base application and a valid token ---
    app_data = {
        "first_name": "Token",
        "last_name": "Test",
        "applicant_email": "token.test@example.com",
        "department": "IT",
        "project_title": "Secure Voting",
        "project_description": "Test token-based voting",
        "costs": 100.00,
    }
    create_response = await client.post("/applications", data=app_data)
    app_id = create_response.json()["application_id"]

    result = await session.execute(
        select(VoteRecord).where(VoteRecord.application_id == app_id)
    )
    vote_record = result.scalars().first()
    assert vote_record is not None
    valid_token = vote_record.token

    # -- Scenario-specific setup ---
    final_token_to_use = valid_token
    invalid_token = "invalid-token-123"  # noqa: S105
    already_cast_token = "ALREADY_CAST_TOKEN"  # noqa: S105

    if token_to_use == invalid_token:
        final_token_to_use = token_to_use
    elif token_to_use == already_cast_token:
        # Cast the vote first to trigger the "already cast" error
        await client.post(f"/vote/{valid_token}", json={"decision": "approve"})
        final_token_to_use = valid_token

    # --- Act: Perform the request ---
    response = await client.get(f"/vote/{final_token_to_use}")

    # --- Assert: Check the outcome ---
    assert response.status_code == expected_status_code
    if expected_detail:
        assert response.json() == {"detail": expected_detail}
    else:
        # Additional checks for the success case
        response_data = response.json()
        assert response_data["voter_email"] == vote_record.voter_email
        assert (
            response_data["application"]["project_title"] == app_data["project_title"]
        )


@pytest.mark.parametrize(
    (
        "scenario",
        "token_type",
        "vote_decision",
        "expected_status_code",
        "expected_message",
    ),
    [
        (
            "Success",
            "VALID_TOKEN",
            VoteOption.APPROVE,
            HTTPStatus.OK,
            "Vote cast successfully",
        ),
        (
            "Already Cast",
            "ALREADY_CAST_TOKEN",
            VoteOption.REJECT,
            HTTPStatus.BAD_REQUEST,
            "Vote has already been cast.",
        ),
        (
            "Invalid Token",
            "INVALID_TOKEN",
            VoteOption.APPROVE,
            HTTPStatus.NOT_FOUND,
            "Invalid or expired token.",
        ),
    ],
)
@pytest.mark.asyncio
async def test_cast_vote_scenarios(
    client: AsyncClient,
    session: AsyncSession,
    scenario: str,
    token_type: str,
    vote_decision: VoteOption,
    expected_status_code: int,
    expected_message: str,
) -> None:
    """Test casting a vote under different scenarios."""
    # --- Setup: Create a base application and a valid token ---
    app_data = {
        "first_name": "Vote",
        "last_name": "Scenario",
        "applicant_email": "vote.scenario@example.com",
        "department": "Testing",
        "project_title": f"Test for {scenario}",
        "project_description": "A test for casting votes.",
        "costs": 150.00,
    }
    create_response = await client.post("/applications", data=app_data)
    app_id = create_response.json()["application_id"]

    result = await session.execute(
        select(VoteRecord).where(
            VoteRecord.application_id == app_id,
            VoteRecord.voter_email == TEST_BOARD_MEMBERS[0],
        )
    )
    vote_record = result.scalars().first()
    assert vote_record is not None
    valid_token = vote_record.token

    # -- Scenario-specific setup ---
    final_token_to_use = valid_token
    invalid_token = "invalid-token-123"  # noqa: S105
    already_cast_token = "ALREADY_CAST_TOKEN"  # noqa: S105

    if token_type == "INVALID_TOKEN":  # noqa: S105
        final_token_to_use = invalid_token
    elif token_type == already_cast_token:
        # Cast the vote first to trigger the "already cast" error
        await client.post(
            f"/vote/{valid_token}", json={"decision": VoteOption.APPROVE.value}
        )
        final_token_to_use = valid_token

    # --- Act: Perform the request ---
    response = await client.post(
        f"/vote/{final_token_to_use}", json={"decision": vote_decision.value}
    )

    # --- Assert: Check the outcome ---
    assert response.status_code == expected_status_code
    if expected_status_code == HTTPStatus.OK:
        assert response.json() == {"message": expected_message}
        # Verify vote record was updated for success case
        await session.refresh(vote_record)
        actual_vote = getattr(vote_record, "vote", None)
        if actual_vote is not None and hasattr(actual_vote, "value"):
            actual_vote = actual_vote.value
        assert actual_vote == vote_decision.value

        actual_vote_status = getattr(vote_record, "vote_status", None)
        if actual_vote_status is not None and hasattr(actual_vote_status, "value"):
            actual_vote_status = actual_vote_status.value
        assert actual_vote_status == VoteStatus.CAST.value
    else:
        assert response.json() == {"detail": expected_message}


@pytest.mark.parametrize(
    ("scenario", "votes", "expected_status"),
    [
        (
            "3/4 Approve -> APPROVED",
            [
                VoteOption.APPROVE,
                VoteOption.APPROVE,
                VoteOption.APPROVE,
                VoteOption.REJECT,
            ],
            ApplicationStatus.APPROVED,
        ),
        (
            "2/4 Approve (Tie) -> REJECTED",
            [
                VoteOption.APPROVE,
                VoteOption.APPROVE,
                VoteOption.REJECT,
                VoteOption.REJECT,
            ],
            ApplicationStatus.REJECTED,
        ),
        (
            "1/4 Approve -> REJECTED",
            [
                VoteOption.APPROVE,
                VoteOption.REJECT,
                VoteOption.REJECT,
                VoteOption.REJECT,
            ],
            ApplicationStatus.REJECTED,
        ),
    ],
)
@pytest.mark.asyncio
async def test_voting_conclusion(
    client: AsyncClient,
    session: AsyncSession,
    mocker: MockerFixture,
    scenario: str,
    votes: list[VoteOption],
    expected_status: ApplicationStatus,
) -> None:
    """Test voting conclusion with different vote combinations."""
    send_email_mock = mocker.patch(
        "projectvote.backend.main.send_email", new_callable=mocker.AsyncMock
    )
    # Create an application and vote records via the API
    app_data = {
        "first_name": "Scenario",
        "last_name": "Test",
        "applicant_email": "scenario.test@example.com",
        "department": "Scenarios",
        "project_title": f"Test for {scenario}",
        "project_description": "A test for a specific voting scenario.",
        "costs": 500.00,
    }
    create_response = await client.post("/applications", data=app_data)
    app_id = create_response.json()["application_id"]

    send_email_mock.reset_mock()

    # Get all vote records for this application
    result = await session.execute(
        select(VoteRecord)
        .where(VoteRecord.application_id == app_id)
        .order_by(VoteRecord.voter_email)
    )
    vote_records = result.scalars().all()
    assert len(vote_records) == len(TEST_BOARD_MEMBERS)

    # Cast votes according to the scenario
    for i, vote_decision in enumerate(votes):
        await client.post(
            f"/vote/{vote_records[i].token}", json={"decision": vote_decision.value}
        )

    # Verify the application status
    updated_app = await session.get(Application, app_id)
    assert updated_app is not None
    actual_status = getattr(updated_app, "status", None)
    if actual_status is not None and hasattr(actual_status, "value"):
        actual_status = actual_status.value
    assert actual_status == expected_status.value

    # Verify that final decision emails were sent
    assert send_email_mock.call_count == EMAILS_SENT_FOR_FINAL_DECISION


@pytest.mark.parametrize(
    ("scenario", "votes", "expected_status"),
    [
        (
            "Approved",
            [
                VoteOption.APPROVE,
                VoteOption.APPROVE,
                VoteOption.APPROVE,
                VoteOption.REJECT,
            ],
            ApplicationStatus.APPROVED,
        ),
        (
            "Rejected",
            [
                VoteOption.APPROVE,
                VoteOption.REJECT,
                VoteOption.REJECT,
                VoteOption.REJECT,
            ],
            ApplicationStatus.REJECTED,
        ),
    ],
)
@pytest.mark.asyncio
async def test_final_decision_email_content(
    client: AsyncClient,
    session: AsyncSession,
    mocker: MockerFixture,
    scenario: str,
    votes: list[VoteOption],
    expected_status: ApplicationStatus,
) -> None:
    """Test the content of the final decision emails."""
    send_email_mock = mocker.patch(
        "projectvote.backend.main.send_email", new_callable=mocker.AsyncMock
    )
    app_data = {
        "first_name": "Email",
        "last_name": "Test",
        "applicant_email": "email.test@example.com",
        "department": "Email Content",
        "project_title": f"Test for {scenario} Email",
        "project_description": "A test for email content.",
        "costs": 200.00,
    }
    create_response = await client.post("/applications", data=app_data)
    app_id = create_response.json()["application_id"]

    send_email_mock.reset_mock()

    result = await session.execute(
        select(VoteRecord)
        .where(VoteRecord.application_id == app_id)
        .order_by(VoteRecord.voter_email)
    )
    vote_records = result.scalars().all()

    for i, vote_decision in enumerate(votes):
        await client.post(
            f"/vote/{vote_records[i].token}", json={"decision": vote_decision.value}
        )

    assert send_email_mock.call_count == EMAILS_SENT_FOR_FINAL_DECISION

    # Define the expected German translations
    status_translations = {
        ApplicationStatus.APPROVED.value: "genehmigt",
        ApplicationStatus.REJECTED.value: "abgelehnt",
    }
    expected_german_status = status_translations.get(expected_status.value)

    # Check applicant email
    applicant_email_call = next(
        call
        for call in send_email_mock.call_args_list
        if call.kwargs["recipients"] == [app_data["applicant_email"]]
    )
    assert (
        applicant_email_call.kwargs["subject"]
        == f"Entscheidung über Ihren Antrag: {app_data['project_title']}"
    )
    assert (
        applicant_email_call.kwargs["template_name"] == "final_decision_applicant.html"
    )
    assert (
        applicant_email_call.kwargs["template_body"]["first_name"]
        == app_data["first_name"]
    )
    assert (
        applicant_email_call.kwargs["template_body"]["last_name"]
        == app_data["last_name"]
    )
    assert (
        applicant_email_call.kwargs["template_body"]["project_title"]
        == app_data["project_title"]
    )
    assert (
        applicant_email_call.kwargs["template_body"]["status"] == expected_german_status
    )

    # Check board member emails
    board_member_email_calls = [
        call
        for call in send_email_mock.call_args_list
        if call.kwargs["recipients"] != [app_data["applicant_email"]]
    ]
    assert len(board_member_email_calls) == len(TEST_BOARD_MEMBERS)
    for call in board_member_email_calls:
        assert (
            call.kwargs["subject"]
            == f"Abstimmung abgeschlossen für: {app_data['project_title']}"
        )
        assert call.kwargs["template_name"] == "final_decision_board.html"
        assert (
            call.kwargs["template_body"]["project_title"] == app_data["project_title"]
        )
        assert call.kwargs["template_body"]["status"] == expected_german_status


@pytest.mark.asyncio
async def test_get_applications_archive(client: AsyncClient) -> None:
    """Test that the /applications/archive GET endpoint returns all applications."""
    # 1. Create an application with an attachment to ensure there's data to retrieve
    app_data = {
        "first_name": "View",
        "last_name": "Test",
        "applicant_email": "view.test@example.com",
        "department": "QA",
        "project_title": "Viewing Test",
        "project_description": "A test for the view applications endpoint.",
        "costs": "99.99",
    }
    files = {
        "attachment": ("test_attachment.txt", b"This is a test file.", "text/plain")
    }
    await client.post("/applications", data=app_data, files=files)

    # 2. Call the endpoint to view applications
    response = await client.get("/applications/archive")
    assert response.status_code == HTTPStatus.OK

    # 3. Verify the response
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) >= 1

    retrieved_app = response_data[0]
    assert retrieved_app["project_title"] == app_data["project_title"]
    assert retrieved_app["status"] == ApplicationStatus.PENDING.value
    assert "votes" in retrieved_app
    assert isinstance(retrieved_app["votes"], list)
    assert len(retrieved_app["votes"]) == len(TEST_BOARD_MEMBERS)
    assert retrieved_app["votes"][0]["voter_email"] == TEST_BOARD_MEMBERS[0]
    assert "attachments" in retrieved_app
    assert isinstance(retrieved_app["attachments"], list)
    assert len(retrieved_app["attachments"]) == 1
    assert retrieved_app["attachments"][0]["filename"] == "test_attachment.txt"


def test_get_board_members_from_config(mocker: MockerFixture) -> None:
    """Test that get_board_members correctly parses the config string."""
    # Arrange
    test_emails = "board1@test.com,board2@test.com,board3@test.com"
    expected_list = ["board1@test.com", "board2@test.com", "board3@test.com"]

    # Create a mock instance of Settings
    mock_settings_instance = mocker.MagicMock(spec=Settings)
    mock_settings_instance.board_members = test_emails

    # Patch the get_app_settings dependency to return our mock settings
    mocker.patch(
        "projectvote.backend.main.get_app_settings",
        return_value=mock_settings_instance,
    )

    # Act
    # get_board_members will now receive the mock_settings_instance
    # via Depends(get_app_settings)
    actual_list = get_board_members(mock_settings_instance)

    # Assert
    assert actual_list == expected_list


@pytest.mark.asyncio
async def test_get_attachment_with_token(
    client: AsyncClient, session: AsyncSession
) -> None:
    """Test retrieving an attachment using a valid vote token."""
    # Create application with attachment
    app_data = {
        "first_name": "Attachment",
        "last_name": "Test",
        "applicant_email": "attachment.test@example.com",
        "department": "IT",
        "project_title": "Attachment Test",
        "project_description": "Test attachment retrieval",
        "costs": "100.00",
    }
    files = {
        "attachment": ("test_document.pdf", b"PDF content here", "application/pdf")
    }
    response = await client.post("/applications", data=app_data, files=files)
    app_id = response.json()["application_id"]

    # Get a vote token
    result = await session.execute(
        select(VoteRecord).where(VoteRecord.application_id == app_id)
    )
    vote_record = result.scalars().first()
    assert vote_record is not None

    # Get attachment ID
    app_result = await session.execute(
        select(Application)
        .where(Application.id == app_id)
        .options(selectinload(Application.attachments))
    )
    application = app_result.scalar_one()
    assert len(application.attachments) == 1
    attachment_id = application.attachments[0].id

    # Test retrieving the attachment with valid token
    response = await client.get(
        f"/vote/{vote_record.token}/attachments/{attachment_id}"
    )
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/pdf"
    assert response.content == b"PDF content here"


@pytest.mark.asyncio
async def test_get_attachment_with_invalid_token(client: AsyncClient) -> None:
    """Test retrieving an attachment with an invalid token."""
    response = await client.get("/vote/invalid-token-123/attachments/1")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Invalid or expired token."}


@pytest.mark.asyncio
async def test_get_attachment_with_wrong_attachment_id(
    client: AsyncClient, session: AsyncSession
) -> None:
    """Test retrieving an attachment that doesn't belong to the application."""
    # Create application with attachment
    app_data = {
        "first_name": "Wrong",
        "last_name": "Attachment",
        "applicant_email": "wrong.attachment@example.com",
        "department": "IT",
        "project_title": "Wrong Attachment Test",
        "project_description": "Test wrong attachment ID",
        "costs": "100.00",
    }
    files = {
        "attachment": ("test.txt", b"Test content", "text/plain")
    }
    response = await client.post("/applications", data=app_data, files=files)
    app_id = response.json()["application_id"]

    # Get a vote token
    result = await session.execute(
        select(VoteRecord).where(VoteRecord.application_id == app_id)
    )
    vote_record = result.scalars().first()
    assert vote_record is not None

    # Try to access a non-existent attachment ID
    response = await client.get(f"/vote/{vote_record.token}/attachments/99999")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Attachment not found."}


@pytest.mark.asyncio
async def test_get_attachment_public(
    client: AsyncClient, mocker: MockerFixture
) -> None:
    """Test retrieving an attachment using the public endpoint."""
    mocker.patch(
        "projectvote.backend.main.send_email", new_callable=mocker.AsyncMock
    )

    # Create application with attachment
    app_data = {
        "first_name": "Public",
        "last_name": "Attachment",
        "applicant_email": "public.attachment@example.com",
        "department": "IT",
        "project_title": "Public Attachment Test",
        "project_description": "Test public attachment retrieval",
        "costs": "150.00",
    }
    files = {
        "attachment": (
            "public_doc.txt",
            b"Public document content",
            "text/plain",
        )
    }
    response = await client.post("/applications", data=app_data, files=files)
    assert response.status_code == HTTPStatus.OK

    # Get the attachment ID from the archive
    archive_response = await client.get("/applications/archive")
    applications = archive_response.json()
    latest_app = applications[0]
    attachment_id = latest_app["attachments"][0]["id"]

    # Test retrieving the attachment via public endpoint
    response = await client.get(f"/attachments/{attachment_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert response.content == b"Public document content"


@pytest.mark.asyncio
async def test_get_attachment_public_not_found(client: AsyncClient) -> None:
    """Test retrieving a non-existent attachment via public endpoint."""
    response = await client.get("/attachments/99999")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Attachment not found."}


@pytest.mark.asyncio
async def test_submit_application_without_attachment(
    client: AsyncClient, session: AsyncSession, mocker: MockerFixture
) -> None:
    """Test creating an application without an attachment."""
    mocker.patch(
        "projectvote.backend.main.send_email", new_callable=mocker.AsyncMock
    )

    application_data = {
        "first_name": "No",
        "last_name": "Attachment",
        "applicant_email": "no.attachment@example.com",
        "department": "Admin",
        "project_title": "No Attachment Project",
        "project_description": "A project without attachments.",
        "costs": 50.00,
    }
    response = await client.post("/applications", data=application_data)
    assert response.status_code == HTTPStatus.OK
    app_id = response.json()["application_id"]

    # Verify no attachments were created
    result = await session.execute(
        select(Application)
        .where(Application.id == app_id)
        .options(selectinload(Application.attachments))
    )
    application = result.scalar_one()
    assert len(application.attachments) == 0


@pytest.mark.asyncio
async def test_submit_application_with_large_file(
    client: AsyncClient, session: AsyncSession, mocker: MockerFixture
) -> None:
    """Test creating an application with a larger file."""
    mocker.patch(
        "projectvote.backend.main.send_email", new_callable=mocker.AsyncMock
    )

    application_data = {
        "first_name": "Large",
        "last_name": "File",
        "applicant_email": "large.file@example.com",
        "department": "Admin",
        "project_title": "Large File Project",
        "project_description": "A project with a larger file.",
        "costs": 75.00,
    }
    # Create a larger file (10KB)
    large_content = b"x" * 10240
    files = {"attachment": ("large_doc.txt", large_content, "text/plain")}
    response = await client.post("/applications", data=application_data, files=files)
    assert response.status_code == HTTPStatus.OK
    app_id = response.json()["application_id"]

    # Verify attachment was created
    result = await session.execute(
        select(Application)
        .where(Application.id == app_id)
        .options(selectinload(Application.attachments))
    )
    application = result.scalar_one()
    assert len(application.attachments) == 1
    assert application.attachments[0].filename == "large_doc.txt"


@pytest.mark.asyncio
async def test_all_votes_approve(
    client: AsyncClient, session: AsyncSession, mocker: MockerFixture
) -> None:
    """Test voting conclusion when all board members approve."""
    send_email_mock = mocker.patch(
        "projectvote.backend.main.send_email", new_callable=mocker.AsyncMock
    )

    app_data = {
        "first_name": "All",
        "last_name": "Approve",
        "applicant_email": "all.approve@example.com",
        "department": "Testing",
        "project_title": "All Approve Test",
        "project_description": "Test when all board members approve.",
        "costs": 300.00,
    }
    create_response = await client.post("/applications", data=app_data)
    app_id = create_response.json()["application_id"]

    send_email_mock.reset_mock()

    # Get all vote records
    result = await session.execute(
        select(VoteRecord)
        .where(VoteRecord.application_id == app_id)
        .order_by(VoteRecord.voter_email)
    )
    vote_records = result.scalars().all()
    assert len(vote_records) == len(TEST_BOARD_MEMBERS)

    # Cast all approve votes
    for vote_record in vote_records:
        await client.post(
            f"/vote/{vote_record.token}",
            json={"decision": VoteOption.APPROVE.value},
        )

    # Verify application was approved
    updated_app = await session.get(Application, app_id)
    assert updated_app is not None
    actual_status = getattr(updated_app, "status", None)
    if actual_status is not None and hasattr(actual_status, "value"):
        actual_status = actual_status.value
    assert actual_status == ApplicationStatus.APPROVED.value

    # Verify that final decision emails were sent
    assert send_email_mock.call_count == EMAILS_SENT_FOR_FINAL_DECISION


@pytest.mark.asyncio
async def test_get_vote_details_with_attachments(
    client: AsyncClient, session: AsyncSession
) -> None:
    """Test that get_vote_details includes attachment information."""
    # Create application with attachment
    app_data = {
        "first_name": "Vote",
        "last_name": "Details",
        "applicant_email": "vote.details@example.com",
        "department": "IT",
        "project_title": "Vote Details Test",
        "project_description": "Test vote details with attachments",
        "costs": "200.00",
    }
    files = {
        "attachment": ("project_plan.pdf", b"Plan content", "application/pdf")
    }
    response = await client.post("/applications", data=app_data, files=files)
    app_id = response.json()["application_id"]

    # Get a vote token
    result = await session.execute(
        select(VoteRecord).where(VoteRecord.application_id == app_id)
    )
    vote_record = result.scalars().first()
    assert vote_record is not None

    # Get vote details
    response = await client.get(f"/vote/{vote_record.token}")
    assert response.status_code == HTTPStatus.OK

    response_data = response.json()
    assert "application" in response_data
    assert "attachments" in response_data["application"]
    assert len(response_data["application"]["attachments"]) == 1
    assert response_data["application"]["attachments"][0]["filename"] == "project_plan.pdf"


@pytest.mark.asyncio
async def test_archive_shows_multiple_applications(
    client: AsyncClient, mocker: MockerFixture
) -> None:
    """Test that archive endpoint returns multiple applications in order."""
    mocker.patch(
        "projectvote.backend.main.send_email", new_callable=mocker.AsyncMock
    )

    # Create multiple applications
    for i in range(3):
        app_data = {
            "first_name": f"User{i}",
            "last_name": "Test",
            "applicant_email": f"user{i}@example.com",
            "department": "Testing",
            "project_title": f"Project {i}",
            "project_description": f"Description for project {i}",
            "costs": 100.00 * (i + 1),
        }
        await client.post("/applications", data=app_data)

    # Get archive
    response = await client.get("/applications/archive")
    assert response.status_code == HTTPStatus.OK

    applications = response.json()
    assert len(applications) >= 3

    # Verify applications are in descending order by ID (newest first)
    assert applications[0]["project_title"] == "Project 2"
    assert applications[1]["project_title"] == "Project 1"
    assert applications[2]["project_title"] == "Project 0"


@pytest.mark.asyncio
async def test_all_votes_reject(
    client: AsyncClient, session: AsyncSession, mocker: MockerFixture
) -> None:
    """Test voting conclusion when all board members reject."""
    send_email_mock = mocker.patch(
        "projectvote.backend.main.send_email", new_callable=mocker.AsyncMock
    )

    app_data = {
        "first_name": "All",
        "last_name": "Reject",
        "applicant_email": "all.reject@example.com",
        "department": "Testing",
        "project_title": "All Reject Test",
        "project_description": "Test when all board members reject.",
        "costs": 400.00,
    }
    create_response = await client.post("/applications", data=app_data)
    app_id = create_response.json()["application_id"]

    send_email_mock.reset_mock()

    # Get all vote records
    result = await session.execute(
        select(VoteRecord)
        .where(VoteRecord.application_id == app_id)
        .order_by(VoteRecord.voter_email)
    )
    vote_records = result.scalars().all()

    # Cast all reject votes
    for vote_record in vote_records:
        await client.post(
            f"/vote/{vote_record.token}",
            json={"decision": VoteOption.REJECT.value},
        )

    # Verify application was rejected
    updated_app = await session.get(Application, app_id)
    assert updated_app is not None
    actual_status = getattr(updated_app, "status", None)
    if actual_status is not None and hasattr(actual_status, "value"):
        actual_status = actual_status.value
    assert actual_status == ApplicationStatus.REJECTED.value

    # Verify that final decision emails were sent
    assert send_email_mock.call_count == EMAILS_SENT_FOR_FINAL_DECISION


@pytest.mark.asyncio
async def test_board_members_with_whitespace(mocker: MockerFixture) -> None:
    """Test that board member emails with whitespace are properly trimmed."""
    from projectvote.backend.main import get_board_members

    # Test with whitespace around emails
    test_emails = " board1@test.com , board2@test.com , board3@test.com "
    expected_list = ["board1@test.com", "board2@test.com", "board3@test.com"]

    mock_settings_instance = mocker.MagicMock(spec=Settings)
    mock_settings_instance.board_members = test_emails

    actual_list = get_board_members(mock_settings_instance)

    assert actual_list == expected_list
    # Verify no leading/trailing whitespace
    for email in actual_list:
        assert email == email.strip()


@pytest.mark.asyncio
async def test_submit_application_with_various_file_extensions(
    client: AsyncClient, session: AsyncSession, mocker: MockerFixture
) -> None:
    """Test that various file extensions are handled correctly."""
    mocker.patch(
        "projectvote.backend.main.send_email", new_callable=mocker.AsyncMock
    )

    file_types = [
        ("document.pdf", b"PDF content", "application/pdf"),
        ("spreadsheet.xlsx", b"Excel content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("image.png", b"PNG content", "image/png"),
    ]

    for filename, content, mime_type in file_types:
        app_data = {
            "first_name": "Extension",
            "last_name": "Test",
            "applicant_email": f"ext.test.{filename}@example.com",
            "department": "IT",
            "project_title": f"Test {filename}",
            "project_description": "Test various file extensions",
            "costs": "100.00",
        }
        files = {"attachment": (filename, content, mime_type)}
        response = await client.post("/applications", data=app_data, files=files)
        assert response.status_code == HTTPStatus.OK

        app_id = response.json()["application_id"]

        # Verify attachment was created with correct mime type
        result = await session.execute(
            select(Application)
            .where(Application.id == app_id)
            .options(selectinload(Application.attachments))
        )
        application = result.scalar_one()
        assert len(application.attachments) == 1
        assert application.attachments[0].filename == filename
        assert application.attachments[0].mime_type == mime_type


@pytest.mark.asyncio
async def test_vote_options_in_get_vote_details(
    client: AsyncClient, session: AsyncSession
) -> None:
    """Test that vote options are returned in get_vote_details response."""
    app_data = {
        "first_name": "Options",
        "last_name": "Test",
        "applicant_email": "options.test@example.com",
        "department": "IT",
        "project_title": "Vote Options Test",
        "project_description": "Test vote options in response",
        "costs": "150.00",
    }
    response = await client.post("/applications", data=app_data)
    app_id = response.json()["application_id"]

    # Get a vote token
    result = await session.execute(
        select(VoteRecord).where(VoteRecord.application_id == app_id)
    )
    vote_record = result.scalars().first()
    assert vote_record is not None

    # Get vote details
    response = await client.get(f"/vote/{vote_record.token}")
    assert response.status_code == HTTPStatus.OK

    response_data = response.json()
    assert "vote_options" in response_data
    assert VoteOption.APPROVE.value in response_data["vote_options"]
    assert VoteOption.REJECT.value in response_data["vote_options"]


@pytest.mark.asyncio
async def test_partial_voting_does_not_finalize(
    client: AsyncClient, session: AsyncSession, mocker: MockerFixture
) -> None:
    """Test that application status doesn't change until all votes are cast."""
    send_email_mock = mocker.patch(
        "projectvote.backend.main.send_email", new_callable=mocker.AsyncMock
    )

    app_data = {
        "first_name": "Partial",
        "last_name": "Vote",
        "applicant_email": "partial.vote@example.com",
        "department": "Testing",
        "project_title": "Partial Voting Test",
        "project_description": "Test that partial votes don't finalize.",
        "costs": 250.00,
    }
    create_response = await client.post("/applications", data=app_data)
    app_id = create_response.json()["application_id"]

    send_email_mock.reset_mock()

    # Get all vote records
    result = await session.execute(
        select(VoteRecord)
        .where(VoteRecord.application_id == app_id)
        .order_by(VoteRecord.voter_email)
    )
    vote_records = result.scalars().all()
    assert len(vote_records) == len(TEST_BOARD_MEMBERS)

    # Cast only 3 out of 4 votes
    for i in range(3):
        await client.post(
            f"/vote/{vote_records[i].token}",
            json={"decision": VoteOption.APPROVE.value},
        )

    # Verify application is still pending
    updated_app = await session.get(Application, app_id)
    assert updated_app is not None
    actual_status = getattr(updated_app, "status", None)
    if actual_status is not None and hasattr(actual_status, "value"):
        actual_status = actual_status.value
    assert actual_status == ApplicationStatus.PENDING.value

    # Verify that NO final decision emails were sent yet
    assert send_email_mock.call_count == 0
