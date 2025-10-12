"""Tests for database.py."""

import contextlib

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from projectvote.backend.database import get_db


@pytest.mark.asyncio
async def test_get_db() -> None:
    """Test that get_db yields a database session."""
    db_gen = get_db()
    db_session = await anext(db_gen)

    assert isinstance(db_session, AsyncSession)

    # Clean up the generator
    with contextlib.suppress(StopAsyncIteration):
        await anext(db_gen)
