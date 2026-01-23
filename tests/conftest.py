"""Configuration and shared fixtures for pytest."""

import shutil
import tempfile
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from projectvote.backend.config import Settings
from projectvote.backend.database import get_db
from projectvote.backend.main import app, get_app_settings, get_board_members
from projectvote.backend.models import Base

# Define a separate set of board members for testing
TEST_BOARD_MEMBERS = [
    "test.member1@example.com",
    "test.member2@example.com",
    "test.member3@example.com",
    "test.member4@example.com",
]
EMAILS_SENT_FOR_FINAL_DECISION = 5

# Setup a test database engine
# Using a single test DB for the whole test suite.
TEST_DB_URL = "sqlite+aiosqlite:///./data/test_applications.db"
test_db_path = Path(TEST_DB_URL.split("///")[-1])
test_db_path.parent.mkdir(parents=True, exist_ok=True)

test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


class _TempUploadsContainer:
    """Container to hold the temporary uploads directory path."""

    path: Path | None = None


@pytest.fixture(scope="session", autouse=True)
def temp_uploads_dir_session() -> Generator[Path, None, None]:
    """Create a temporary directory for test uploads and clean up after session."""
    temp_dir = Path(tempfile.mkdtemp(prefix="projectvote_test_uploads_"))
    _TempUploadsContainer.path = temp_dir
    yield temp_dir
    # Clean up after all tests
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def dispose_test_engine() -> AsyncGenerator[None, None]:
    """Ensure the test database engine is properly disposed after the test session."""
    yield
    await test_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def cleanup_db_file_after_session() -> Generator[None, None, None]:
    """Ensure the test database file is removed after the test session."""
    yield
    if test_db_path.exists():
        test_db_path.unlink()


@pytest_asyncio.fixture(name="session")
async def session_fixture() -> AsyncGenerator[AsyncSession, None]:
    """Yield a test database session and clean up tables after each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSessionLocal() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(name="client")
async def client_fixture(
    request: pytest.FixtureRequest, session: AsyncSession, mocker: MockerFixture
) -> AsyncGenerator[AsyncClient, None]:
    """Yield an AsyncClient for testing the FastAPI app with mocked dependencies."""
    settings_override = None
    marker = request.node.get_closest_marker("settings_override")
    if marker:
        settings_override = marker.args[0]

    async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield session

    def get_test_board_members() -> list[str]:
        return TEST_BOARD_MEMBERS

    def get_overridden_settings() -> Settings:
        settings_data: dict[str, Any] = {
            "board_members": ",".join(TEST_BOARD_MEMBERS),
            "mail_driver": "console",  # Use console driver - no actual email sending
            "mail_password": SecretStr("test-password"),
        }
        if settings_override:
            settings_data.update(settings_override)
        settings = Settings(**settings_data)
        # Override project_root to use temp directory for file uploads
        if _TempUploadsContainer.path:
            settings.project_root = _TempUploadsContainer.path
        return settings

    # Mock the send_email function to prevent actual email sending
    # Patch where it's USED (in main.py), not where it's defined
    mocker.patch("projectvote.backend.main.send_email", new_callable=mocker.AsyncMock)

    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_board_members] = get_test_board_members
    app.dependency_overrides[get_app_settings] = get_overridden_settings

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_settings")
def test_settings_fixture() -> Settings:
    """Provide the test settings with temp directory override."""
    settings = Settings(
        board_members=",".join(TEST_BOARD_MEMBERS),
        mail_driver="console",
        mail_password=SecretStr("test-password"),
    )
    if _TempUploadsContainer.path:
        settings.project_root = _TempUploadsContainer.path
    return settings
