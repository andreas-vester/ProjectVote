import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from pathlib import Path  # Import Path

from lvd_fv_form.backend.main import app, BOARD_MEMBERS
from lvd_fv_form.backend.database import get_db, DATABASE_URL
from lvd_fv_form.backend.models import (
    Base,
    Application,
    ApplicationStatus,
    VoteOption,
    VoteRecord,
    VoteStatus,
)

# Setup a test database engine
test_db_filename = DATABASE_URL.split("///")[-1].replace(
    ".db", "_test.db"
)  # Extract only the filename
test_db_path = Path(test_db_filename)  # Use Path
test_engine = create_async_engine(
    f"sqlite+aiosqlite:///./{test_db_filename}", echo=False
)
TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(name="session")
async def session_fixture():
    """Yields a test database session and cleans up after each test."""
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
async def client_fixture(session: AsyncSession):
    """Yields an AsyncClient for testing the FastAPI app."""

    async def get_test_db():
        yield session

    app.dependency_overrides[get_db] = get_test_db

    from httpx import ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_read_root(client: AsyncClient):
    """Test that the root endpoint returns a welcome message."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Funding Application API"}


@pytest.mark.asyncio
async def test_create_application(client: AsyncClient, session: AsyncSession):
    """Test creating a new application and associated vote records."""
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
    assert response.status_code == 200
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
    assert len(vote_records) == len(BOARD_MEMBERS)
    for record in vote_records:
        assert record.token is not None
        assert record.vote_status == VoteStatus.PENDING


@pytest.mark.asyncio
async def test_get_vote_details(client: AsyncClient, session: AsyncSession):
    """Test fetching application details using a valid token."""
    # Create an application and vote records via the API
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

    # Get a token from the created vote records
    result = await session.execute(
        select(VoteRecord).where(VoteRecord.application_id == app_id)
    )
    vote_record = result.scalars().first()
    assert vote_record is not None

    response = await client.get(f"/vote/{vote_record.token}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["voter_email"] == vote_record.voter_email
    assert response_data["application"]["project_title"] == app_data["project_title"]


@pytest.mark.asyncio
async def test_get_vote_details_invalid_token(client: AsyncClient):
    """Test fetching details with an invalid token."""
    response = await client.get("/vote/invalid-token-123")
    assert response.status_code == 404
    assert response.json() == {"detail": "Invalid or expired token."}


@pytest.mark.asyncio
async def test_cast_vote_success(client: AsyncClient, session: AsyncSession):
    """Test casting a vote successfully using a token."""
    # Create an application and vote records via the API
    app_data = {
        "first_name": "Vote",
        "last_name": "Success",
        "applicant_email": "vote.success@example.com",
        "department": "HR",
        "project_title": "Team Building",
        "project_description": "Annual event",
        "costs": 200.00,
    }
    create_response = await client.post("/applications", json=app_data)
    app_id = create_response.json()["application_id"]

    # Get a token for a board member
    result = await session.execute(
        select(VoteRecord).where(
            VoteRecord.application_id == app_id,
            VoteRecord.voter_email == BOARD_MEMBERS[0],
        )
    )
    vote_record = result.scalars().first()
    assert vote_record is not None

    vote_data = {"decision": VoteOption.APPROVE.value}
    response = await client.post(f"/vote/{vote_record.token}", json=vote_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Vote cast successfully"}

    # Verify vote record was updated
    await session.refresh(vote_record)
    assert vote_record.vote == VoteOption.APPROVE
    assert vote_record.vote_status == VoteStatus.CAST


@pytest.mark.asyncio
async def test_cast_vote_already_cast(client: AsyncClient, session: AsyncSession):
    """Test that a vote cannot be cast twice with the same token."""
    # Create an application and vote records via the API
    app_data = {
        "first_name": "Double",
        "last_name": "Vote",
        "applicant_email": "double.vote@example.com",
        "department": "Finance",
        "project_title": "Budget Review",
        "project_description": "Quarterly review",
        "costs": 50.00,
    }
    create_response = await client.post("/applications", json=app_data)
    app_id = create_response.json()["application_id"]

    # Get a token
    result = await session.execute(
        select(VoteRecord).where(
            VoteRecord.application_id == app_id,
            VoteRecord.voter_email == BOARD_MEMBERS[0],
        )
    )
    vote_record = result.scalars().first()
    assert vote_record is not None

    # Cast first vote
    vote_data = {"decision": VoteOption.REJECT.value}
    response1 = await client.post(f"/vote/{vote_record.token}", json=vote_data)
    assert response1.status_code == 200

    # Try to cast again with the same token
    response2 = await client.post(f"/vote/{vote_record.token}", json=vote_data)
    assert response2.status_code == 400
    assert response2.json() == {"detail": "Vote has already been cast."}


@pytest.mark.asyncio
async def test_voting_conclusion_approve(client: AsyncClient, session: AsyncSession):
    """Test that voting concludes and the application status is set to APPROVED."""
    # Create an application and vote records via the API
    app_data = {
        "first_name": "Approve",
        "last_name": "Conclusion",
        "applicant_email": "approve.con@example.com",
        "department": "Legal",
        "project_title": "Contract Review",
        "project_description": "New contract",
        "costs": 300.00,
    }
    create_response = await client.post("/applications", json=app_data)
    app_id = create_response.json()["application_id"]

    # Get all vote records for this application
    result = await session.execute(
        select(VoteRecord)
        .where(VoteRecord.application_id == app_id)
        .order_by(VoteRecord.voter_email)
    )
    vote_records = result.scalars().all()
    assert len(vote_records) == len(BOARD_MEMBERS)

    # Cast votes (majority approve)
    await client.post(
        f"/vote/{vote_records[0].token}", json={"decision": VoteOption.APPROVE.value}
    )
    await client.post(
        f"/vote/{vote_records[1].token}", json={"decision": VoteOption.APPROVE.value}
    )
    await client.post(
        f"/vote/{vote_records[2].token}", json={"decision": VoteOption.REJECT.value}
    )

    # Verify the application status
    updated_app = await session.get(Application, app_id)
    assert updated_app.status == ApplicationStatus.APPROVED


@pytest.mark.asyncio
async def test_voting_conclusion_reject(client: AsyncClient, session: AsyncSession):
    """Test that voting concludes and the application status is set to REJECTED."""
    # Create an application and vote records via the API
    app_data = {
        "first_name": "Reject",
        "last_name": "Conclusion",
        "applicant_email": "reject.con@example.com",
        "department": "Sales",
        "project_title": "New Strategy",
        "project_description": "Sales strategy",
        "costs": 400.00,
    }
    create_response = await client.post("/applications", json=app_data)
    app_id = create_response.json()["application_id"]

    # Get all vote records for this application
    result = await session.execute(
        select(VoteRecord)
        .where(VoteRecord.application_id == app_id)
        .order_by(VoteRecord.voter_email)
    )
    vote_records = result.scalars().all()
    assert len(vote_records) == len(BOARD_MEMBERS)

    # Cast votes (majority reject)
    await client.post(
        f"/vote/{vote_records[0].token}", json={"decision": VoteOption.REJECT.value}
    )
    await client.post(
        f"/vote/{vote_records[1].token}", json={"decision": VoteOption.REJECT.value}
    )
    await client.post(
        f"/vote/{vote_records[2].token}", json={"decision": VoteOption.APPROVE.value}
    )

    # Verify the application status
    updated_app = await session.get(Application, app_id)
    assert updated_app.status == ApplicationStatus.REJECTED
