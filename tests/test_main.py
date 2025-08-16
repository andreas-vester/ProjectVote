"""Tests for the LVD-FV form submission and voting system."""

from collections.abc import AsyncGenerator
from http import HTTPStatus
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from lvd_fv_form.backend.config import Settings
from lvd_fv_form.backend.database import DATABASE_URL, get_db
from lvd_fv_form.backend.main import app, get_board_members
from lvd_fv_form.backend.models import (
    Application,
    ApplicationStatus,
    Base,
    VoteOption,
    VoteRecord,
    VoteStatus,
)

# Define a separate set of board members for testing
TEST_BOARD_MEMBERS = [
    "test.member1@example.com",
    "test.member2@example.com",
    "test.member3@example.com",
    "test.member4@example.com",
]
EMAILS_SENT_FOR_FINAL_DECISION = 2

# Setup a test database engine
test_db_filename = DATABASE_URL.split("///")[-1].replace(
    ".db", "_test.db"
)  # Extract only the filename
test_db_path = Path(test_db_filename)
test_db_path.parent.mkdir(parents=True, exist_ok=True)
test_engine = create_async_engine(
    f"sqlite+aiosqlite:///./{test_db_filename}", echo=False
)
TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(name="session")
async def session_fixture() -> AsyncGenerator[AsyncSession, None]:
    """Yield a test database session and clean up after each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Explicitly close the engine and remove the database file using pathlib
    await test_engine.dispose()
    if test_db_path.exists():
        test_db_path.unlink()


@pytest_asyncio.fixture(name="client")
async def client_fixture(
    session: AsyncSession, mocker: MockerFixture
) -> AsyncGenerator[AsyncClient, None]:
    """Yield an AsyncClient for testing the FastAPI app."""

    async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield session

    def get_test_board_members() -> list[str]:
        return TEST_BOARD_MEMBERS

    # Mock the send_email function to prevent real emails from being sent
    mocker.patch("lvd_fv_form.backend.main.send_email", new_callable=mocker.AsyncMock)

    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_board_members] = get_test_board_members

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


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
        "lvd_fv_form.backend.main.send_email", new_callable=mocker.AsyncMock
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
    response = await client.post("/applications", json=application_data)
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
        assert record.vote_status == VoteStatus.PENDING

    # Verify that email sending was triggered
    assert send_email_mock.call_count == len(TEST_BOARD_MEMBERS)


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
    create_response = await client.post("/applications", json=app_data)
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
    create_response = await client.post("/applications", json=app_data)
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
        assert vote_record.vote == vote_decision
        assert vote_record.vote_status == VoteStatus.CAST
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
        "lvd_fv_form.backend.main.send_email", new_callable=mocker.AsyncMock
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
    create_response = await client.post("/applications", json=app_data)
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
    assert updated_app.status == expected_status

    # Verify that final decision emails were sent
    assert send_email_mock.call_count == EMAILS_SENT_FOR_FINAL_DECISION


@pytest.mark.asyncio
async def test_get_applications_archive(client: AsyncClient) -> None:
    """Test that the /applications/archive GET endpoint returns all applications."""
    # 1. Create an application to ensure there's data to retrieve
    app_data = {
        "first_name": "View",
        "last_name": "Test",
        "applicant_email": "view.test@example.com",
        "department": "QA",
        "project_title": "Viewing Test",
        "project_description": "A test for the view applications endpoint.",
        "costs": 99.99,
    }
    await client.post("/applications", json=app_data)

    # 2. Call the endpoint to view applications
    response = await client.get("/applications/archive")
    assert response.status_code == HTTPStatus.OK

    # 3. Verify the response
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 1

    retrieved_app = response_data[0]
    assert retrieved_app["project_title"] == app_data["project_title"]
    assert retrieved_app["status"] == ApplicationStatus.PENDING.value
    assert "votes" in retrieved_app
    assert isinstance(retrieved_app["votes"], list)
    assert len(retrieved_app["votes"]) == len(TEST_BOARD_MEMBERS)
    assert retrieved_app["votes"][0]["voter_email"] == TEST_BOARD_MEMBERS[0]


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
        "lvd_fv_form.backend.main.get_app_settings",
        return_value=mock_settings_instance,
    )

    # Act
    # get_board_members will now receive the mock_settings_instance
    # via Depends(get_app_settings)
    actual_list = get_board_members(mock_settings_instance)

    # Assert
    assert actual_list == expected_list
