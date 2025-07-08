import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from lvd_fv_form.backend.main import app, BOARD_MEMBERS
from lvd_fv_form.backend.database import get_db, DATABASE_URL
from lvd_fv_form.backend.models import Base, Application, ApplicationStatus, VoteOption

# Setup a test database engine
test_engine = create_async_engine(DATABASE_URL.replace(".db", "_test.db"), echo=False)
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
async def test_create_application(client: AsyncClient):
    """Test creating a new application."""
    application_data = {
        "first_name": "Test",
        "last_name": "User",
        "applicant_email": "test.user@example.com",
        "department": "Test Department",
        "project_title": "Test Project",
        "project_description": "A test project description.",
        "costs": 123.45
    }
    response = await client.post("/applications", json=application_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Application submitted successfully"
    assert "application_id" in response_data

@pytest.mark.asyncio
async def test_get_application(client: AsyncClient, session: AsyncSession):
    """Test getting a specific application."""
    # First, create an application to fetch
    new_app = Application(
        first_name="Jane",
        last_name="Doe",
        applicant_email="jane.doe@example.com",
        department="Science",
        project_title="Microscope",
        project_description="A new microscope for the lab.",
        costs=500.00
    )
    session.add(new_app)
    await session.commit()
    await session.refresh(new_app)

    response = await client.get(f"/applications/{new_app.id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["application"]["project_title"] == "Microscope"
    assert response_data["application"]["id"] == new_app.id

@pytest.mark.asyncio
async def test_get_nonexistent_application(client: AsyncClient):
    """Test getting an application that does not exist."""
    response = await client.get("/applications/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Application not found"}

@pytest.mark.asyncio
async def test_cast_vote(client: AsyncClient, session: AsyncSession):
    """Test casting a vote on an application."""
    new_app = Application(
        first_name="Vote",
        last_name="Test",
        applicant_email="vote.test@example.com",
        department="Voting Dept",
        project_title="Voting System",
        project_description="A test of the voting system.",
        costs=10.00
    )
    session.add(new_app)
    await session.commit()
    await session.refresh(new_app)

    vote_data = {"voter_email": BOARD_MEMBERS[0], "decision": VoteOption.APPROVE.value}
    response = await client.post(f"/applications/{new_app.id}/vote", json=vote_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Vote cast successfully"}

@pytest.mark.asyncio
async def test_duplicate_vote(client: AsyncClient, session: AsyncSession):
    """Test that a user cannot vote twice on the same application."""
    new_app = Application(
        first_name="Duplicate",
        last_name="Vote",
        applicant_email="duplicate.vote@example.com",
        department="Duplicate Dept",
        project_title="Duplicate Vote Test",
        project_description="A test for duplicate votes.",
        costs=20.00
    )
    session.add(new_app)
    await session.commit()
    await session.refresh(new_app)

    vote_data = {"voter_email": BOARD_MEMBERS[0], "decision": VoteOption.APPROVE.value}
    # First vote
    response1 = await client.post(f"/applications/{new_app.id}/vote", json=vote_data)
    assert response1.status_code == 200

    # Second vote (should fail)
    response2 = await client.post(f"/applications/{new_app.id}/vote", json=vote_data)
    assert response2.status_code == 400
    assert f"Voter {BOARD_MEMBERS[0]} has already voted" in response2.json()["detail"]

@pytest.mark.asyncio
async def test_voting_conclusion_approve(client: AsyncClient, session: AsyncSession):
    """Test that voting concludes and the application status is set to APPROVED."""
    new_app = Application(
        first_name="Conclusion",
        last_name="Test",
        applicant_email="conclusion.test@example.com",
        department="Conclusion Dept",
        project_title="Conclusion Test",
        project_description="A test for voting conclusion.",
        costs=30.00
    )
    session.add(new_app)
    await session.commit()
    await session.refresh(new_app)

    # Cast votes (majority approve)
    await client.post(f"/applications/{new_app.id}/vote", json={"voter_email": BOARD_MEMBERS[0], "decision": VoteOption.APPROVE.value})
    await client.post(f"/applications/{new_app.id}/vote", json={"voter_email": BOARD_MEMBERS[1], "decision": VoteOption.APPROVE.value})
    await client.post(f"/applications/{new_app.id}/vote", json={"voter_email": BOARD_MEMBERS[2], "decision": VoteOption.REJECT.value})

    # Verify the application status
    await session.refresh(new_app)
    assert new_app.status == ApplicationStatus.APPROVED

@pytest.mark.asyncio
async def test_voting_conclusion_reject(client: AsyncClient, session: AsyncSession):
    """Test that voting concludes and the application status is set to REJECTED."""
    new_app = Application(
        first_name="Reject",
        last_name="Test",
        applicant_email="reject.test@example.com",
        department="Reject Dept",
        project_title="Reject Test",
        project_description="A test for voting rejection.",
        costs=40.00
    )
    session.add(new_app)
    await session.commit()
    await session.refresh(new_app)

    # Cast votes (majority reject)
    await client.post(f"/applications/{new_app.id}/vote", json={"voter_email": BOARD_MEMBERS[0], "decision": VoteOption.REJECT.value})
    await client.post(f"/applications/{new_app.id}/vote", json={"voter_email": BOARD_MEMBERS[1], "decision": VoteOption.REJECT.value})
    await client.post(f"/applications/{new_app.id}/vote", json={"voter_email": BOARD_MEMBERS[2], "decision": VoteOption.APPROVE.value})

    # Verify the application status
    await session.refresh(new_app)
    assert new_app.status == ApplicationStatus.REJECTED