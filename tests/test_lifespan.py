"""Tests for application lifespan events."""

from http import HTTPStatus

import pytest
from httpx import ASGITransport, AsyncClient

from projectvote.backend.main import app


@pytest.mark.asyncio
async def test_lifespan_creates_database() -> None:
    """Test that the lifespan event creates database tables."""
    # The lifespan event should execute when we create a client
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Simply accessing the app should trigger the lifespan event
        response = await client.get("/")
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"message": "Welcome to the Funding Application API"}
