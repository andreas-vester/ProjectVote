"""Tests for the file upload functionality in the ProjectVote application."""

import io
from http import HTTPStatus
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from projectvote.backend.models import Application, Attachment, VoteRecord


@pytest.mark.asyncio
async def test_create_application_with_attachment(
    client: AsyncClient, session: AsyncSession
) -> None:
    """Test creating an application with a file attachment."""
    # Arrange
    application_data = {
        "first_name": "File",
        "last_name": "Uploader",
        "applicant_email": "file.uploader@example.com",
        "department": "IT",
        "project_title": "File Upload Test",
        "project_description": "Testing file uploads.",
        "costs": 50.0,
    }
    file_content = b"This is a test file."
    file_name = "test_attachment.txt"
    files = {"attachment": (file_name, io.BytesIO(file_content), "text/plain")}

    # Act
    response = await client.post("/applications", data=application_data, files=files)

    # Assert
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data["message"] == "Application submitted successfully"
    app_id = response_data["application_id"]

    # Verify application in DB
    application = await session.get(Application, app_id)
    assert application is not None
    assert application.project_title == application_data["project_title"]

    # Verify attachment in DB
    result = await session.execute(
        select(Attachment).where(Attachment.application_id == app_id)
    )
    attachment = result.scalar_one_or_none()
    assert attachment is not None
    assert attachment.filename == file_name
    assert attachment.mime_type == "text/plain"

    # Verify file on disk
    attachment_path = Path(attachment.filepath)
    assert attachment_path.exists()
    assert attachment_path.read_bytes() == file_content

    # Clean up the created file
    attachment_path.unlink()


@pytest.mark.asyncio
async def test_create_application_without_attachment(
    client: AsyncClient, session: AsyncSession
) -> None:
    """Test creating an application without a file attachment."""
    # Arrange
    application_data = {
        "first_name": "NoFile",
        "last_name": "User",
        "applicant_email": "nofile.user@example.com",
        "department": "HR",
        "project_title": "No File Test",
        "project_description": "Testing submissions without files.",
        "costs": 25.0,
    }

    # Act
    response = await client.post("/applications", data=application_data)

    # Assert
    assert response.status_code == HTTPStatus.OK
    app_id = response.json()["application_id"]

    # Verify no attachment was created
    result = await session.execute(
        select(Attachment).where(Attachment.application_id == app_id)
    )
    attachment = result.scalar_one_or_none()
    assert attachment is None


@pytest.mark.asyncio
async def test_get_attachment(client: AsyncClient, session: AsyncSession) -> None:
    """Test downloading an attachment using a valid vote token."""
    # Arrange: Create an application with an attachment
    application_data = {
        "first_name": "File",
        "last_name": "Downloader",
        "applicant_email": "file.downloader@example.com",
        "department": "IT",
        "project_title": "File Download Test",
        "project_description": "Testing file downloads.",
        "costs": 60.0,
    }
    file_content = b"Test content for download."
    file_name = "download_me.txt"
    files = {"attachment": (file_name, io.BytesIO(file_content), "text/plain")}

    post_response = await client.post(
        "/applications", data=application_data, files=files
    )
    app_id = post_response.json()["application_id"]

    # Get the vote token and attachment ID
    vote_result = await session.execute(
        select(VoteRecord).where(VoteRecord.application_id == app_id)
    )
    vote_record = vote_result.scalars().first()
    assert vote_record is not None
    token = vote_record.token

    attachment_result = await session.execute(
        select(Attachment).where(Attachment.application_id == app_id)
    )
    attachment = attachment_result.scalar_one_or_none()
    assert attachment is not None
    attachment_id = attachment.id

    # Act
    response = await client.get(f"/vote/{token}/attachments/{attachment_id}")

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.content == file_content
    assert response.headers["content-type"] == "text/plain; charset=utf-8"

    # Clean up the created file
    attachment_path = Path(attachment.filepath)
    if attachment_path.exists():
        attachment_path.unlink()


@pytest.mark.asyncio
async def test_get_attachment_invalid_token(
    client: AsyncClient, session: AsyncSession
) -> None:
    """Test that getting an attachment with an invalid token fails."""
    # Arrange: Create an application with an attachment
    application_data = {
        "first_name": "a",
        "last_name": "b",
        "applicant_email": "c@d.com",
        "department": "d",
        "project_title": "e",
        "project_description": "f",
        "costs": 1,
    }
    files = {"attachment": ("file.txt", io.BytesIO(b"content"), "text/plain")}
    post_response = await client.post(
        "/applications", data=application_data, files=files
    )
    app_id = post_response.json()["application_id"]
    attachment_result = await session.execute(
        select(Attachment).where(Attachment.application_id == app_id)
    )
    attachment = attachment_result.scalar_one()

    # Act
    response = await client.get(f"/vote/invalid-token/attachments/{attachment.id}")

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND

    # Clean up
    attachment_path = Path(attachment.filepath)
    if attachment_path.exists():
        attachment_path.unlink()


@pytest.mark.asyncio
async def test_get_attachment_wrong_application(
    client: AsyncClient, session: AsyncSession
) -> None:
    """Test getting an attachment that does not belong to the vote token."""
    # Arrange: Create two applications, one with an attachment
    app1_data = {
        "first_name": "App1",
        "last_name": "User",
        "applicant_email": "a1@b.com",
        "department": "d",
        "project_title": "t1",
        "project_description": "d1",
        "costs": 1,
    }
    app2_data = {
        "first_name": "App2",
        "last_name": "User",
        "applicant_email": "a2@b.com",
        "department": "d",
        "project_title": "t2",
        "project_description": "d2",
        "costs": 2,
    }
    files = {"attachment": ("file.txt", io.BytesIO(b"content"), "text/plain")}

    app1_response = await client.post("/applications", data=app1_data, files=files)
    app1_id = app1_response.json()["application_id"]
    app2_response = await client.post("/applications", data=app2_data)
    app2_id = app2_response.json()["application_id"]

    # Get token from app2 and attachment from app1
    vote_result = await session.execute(
        select(VoteRecord).where(VoteRecord.application_id == app2_id)
    )
    vote_record_app2 = vote_result.scalars().first()
    assert vote_record_app2 is not None
    token_app2 = vote_record_app2.token

    attachment_result = await session.execute(
        select(Attachment).where(Attachment.application_id == app1_id)
    )
    attachment_app1 = attachment_result.scalar_one()

    # Act: Try to get attachment from app1 using token from app2
    response = await client.get(f"/vote/{token_app2}/attachments/{attachment_app1.id}")

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Attachment not found."

    # Clean up
    attachment_path = Path(attachment_app1.filepath)
    if attachment_path.exists():
        attachment_path.unlink()


@pytest.mark.asyncio
async def test_archive_and_vote_details_include_attachments(
    client: AsyncClient, session: AsyncSession
) -> None:
    """Test that archive and vote details endpoints include attachment info."""
    # Arrange: Create an application with an attachment
    application_data = {
        "first_name": "Attachment",
        "last_name": "Info",
        "applicant_email": "attachment.info@example.com",
        "department": "Finance",
        "project_title": "Attachment Info Test",
        "project_description": "Testing attachment info in API responses.",
        "costs": 70.0,
    }
    file_name = "info.txt"
    files = {"attachment": (file_name, io.BytesIO(b"info"), "text/plain")}
    post_response = await client.post(
        "/applications", data=application_data, files=files
    )
    app_id = post_response.json()["application_id"]

    # --- Test /applications/archive ---
    archive_response = await client.get("/applications/archive")
    assert archive_response.status_code == HTTPStatus.OK
    archive_data = archive_response.json()
    assert len(archive_data) > 0
    app_in_archive = next((app for app in archive_data if app["id"] == app_id), None)
    assert app_in_archive is not None
    assert "attachments" in app_in_archive
    assert len(app_in_archive["attachments"]) == 1
    assert app_in_archive["attachments"][0]["filename"] == file_name
    attachment_id = app_in_archive["attachments"][0]["id"]

    # --- Test /vote/{token} ---
    vote_result = await session.execute(
        select(VoteRecord).where(VoteRecord.application_id == app_id)
    )
    vote_record = vote_result.scalars().first()
    assert vote_record is not None
    token = vote_record.token
    vote_details_response = await client.get(f"/vote/{token}")
    assert vote_details_response.status_code == HTTPStatus.OK
    vote_data = vote_details_response.json()
    assert "application" in vote_data
    assert "attachments" in vote_data["application"]
    assert len(vote_data["application"]["attachments"]) == 1
    assert vote_data["application"]["attachments"][0]["filename"] == file_name

    # --- Cleanup ---
    attachment_result = await session.execute(
        select(Attachment).where(Attachment.id == attachment_id)
    )
    attachment = attachment_result.scalar_one()
    attachment_path = Path(attachment.filepath)
    if attachment_path.exists():
        attachment_path.unlink()
