"""FastAPI application for ProjectVote."""

import os
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import aiofiles
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .config import Settings
from .database import DATABASE_URL, engine, get_db
from .email_service import send_email
from .models import (
    Application,
    ApplicationStatus,
    Attachment,
    Base,
    VoteOption,
    VoteRecord,
    VoteStatus,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events."""
    # Ensure the data directory exists before creating tables.
    # This is placed here to run once on application startup.
    db_path_str = DATABASE_URL.split("///", 1)[1]
    db_dir = Path(db_path_str).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    # Database table creation
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(lifespan=lifespan)

# CORS middleware setup
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_app_settings() -> Settings:
    """
    Return application settings.

    This function loads the correct .env file based on the APP_ENV
    environment variable.
    """
    app_env = os.getenv("APP_ENV", "production")

    if app_env == "development":
        dotenv_path = (
            Path(__file__).resolve().parent.parent.parent.parent / ".env.local"
        )
        if dotenv_path.exists():
            load_dotenv(dotenv_path=dotenv_path, override=True)
    elif app_env == "testing":
        dotenv_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
        if dotenv_path.exists():
            load_dotenv(dotenv_path=dotenv_path, override=True)

    return Settings()


def get_board_members(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> list[str]:
    """Provide the list of board members from settings."""
    assert settings.board_members is not None  # Type narrowing for static analysis
    return [email.strip() for email in settings.board_members.split(",")]


# --- Pydantic Models for API data validation ---


class ApplicationCreate(BaseModel):
    """Schema for creating a new application."""

    first_name: str
    last_name: str
    applicant_email: str
    department: str
    project_title: str
    project_description: str
    costs: float


class VoteCreate(BaseModel):
    """Schema for casting a vote."""

    decision: VoteOption


class VoteOut(BaseModel):
    """Schema for displaying a vote."""

    model_config = ConfigDict(from_attributes=True)

    voter_email: str
    decision: VoteOption | None = Field(validation_alias="vote")


class AttachmentOut(BaseModel):
    """Schema for displaying an attachment."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str


class ApplicationOut(BaseModel):
    """Schema for displaying an application in the archive."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    applicant_email: str
    department: str
    project_title: str
    project_description: str
    costs: float
    status: ApplicationStatus
    votes: list[VoteOut]
    attachments: list[AttachmentOut] = []


# --- Email Sending Functions ---


async def send_voting_links(
    application: Application,
    db: AsyncSession,
    board_members: list[str],
    settings: Settings,
) -> None:
    """Generate vote records and sends emails with unique links."""
    for member_email in board_members:
        vote_record = VoteRecord(
            application_id=application.id, voter_email=member_email
        )
        db.add(vote_record)
        await db.flush()
        await db.refresh(vote_record)

        vote_url = f"{settings.frontend_url}/vote/{vote_record.token}"
        await send_email(
            recipients=[member_email],
            subject=f"Neuer Förderantrag: {application.project_title}",
            template_body={
                "first_name": application.first_name,
                "last_name": application.last_name,
                "project_title": application.project_title,
                "costs": application.costs,
                "vote_url": vote_url,
                "token": vote_record.token,
                "frontend_url": settings.frontend_url,
                "backend_url": settings.backend_url,
                "attachments": [
                    {
                        "id": att.id,
                        "filename": att.filename,
                        "url": f"{settings.frontend_url}/api/vote/{vote_record.token}/"
                        f"attachments/{att.id}",
                    }
                    for att in application.attachments
                ],
            },
            template_name="new_application.html",
            settings=settings,
        )


async def send_final_decision_emails(
    application: Application, board_members: list[str], settings: Settings
) -> None:
    """Send final decision emails to the applicant and board members."""
    status_translations = {
        ApplicationStatus.APPROVED.value: "genehmigt",
        ApplicationStatus.REJECTED.value: "abgelehnt",
    }
    # Get the raw status string from the application object
    status_str = (
        application.status.value
        if isinstance(application.status, ApplicationStatus)
        else str(application.status)
    )

    # Get the German translation, defaulting to the original status if not found
    german_status = status_translations.get(status_str, status_str.upper())

    # Notification to Applicant
    await send_email(
        recipients=[application.applicant_email],  # type: ignore[arg-type]
        subject=f"Entscheidung über Ihren Antrag: {application.project_title}",
        template_body={
            "first_name": application.first_name,
            "last_name": application.last_name,
            "project_title": application.project_title,
            "status": german_status,
        },
        template_name="final_decision_applicant.html",
        settings=settings,
    )

    # Notification to Board Members
    for member_email in board_members:
        await send_email(
            recipients=[member_email],
            subject=f"Abstimmung abgeschlossen für: {application.project_title}",
            template_body={
                "project_title": application.project_title,
                "status": german_status,
            },
            template_name="final_decision_board.html",
            settings=settings,
        )


async def _check_and_finalize_voting(
    application_id: int,
    db: AsyncSession,
    board_members: list[str],
    settings: Settings,
) -> None:
    """Check if all votes are cast and finalize the application status."""
    application_result = await db.execute(
        select(Application)
        .where(Application.id == application_id)
        .options(selectinload(Application.votes)),
    )
    application = application_result.scalar_one()

    cast_votes = [v for v in application.votes if v.vote_status == VoteStatus.CAST]

    # If all board members have voted, determine the outcome.
    if len(cast_votes) >= len(board_members):
        approvals = sum(1 for v in cast_votes if v.vote == VoteOption.APPROVE)
        if approvals > len(board_members) / 2:
            application.status = ApplicationStatus.APPROVED.value  # type: ignore[attr-defined]
        else:
            application.status = ApplicationStatus.REJECTED.value  # type: ignore[attr-defined]

        await db.commit()
        await send_final_decision_emails(application, board_members, settings)


# --- API Endpoints ---


@app.get("/")
async def read_root() -> dict:
    """Return a welcome message."""
    return {"message": "Welcome to the Funding Application API"}


@app.post("/applications")
async def submit_application(
    db: Annotated[AsyncSession, Depends(get_db)],
    board_members: Annotated[list[str], Depends(get_board_members)],
    settings: Annotated[Settings, Depends(get_app_settings)],
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    applicant_email: Annotated[str, Form()],
    department: Annotated[str, Form()],
    project_title: Annotated[str, Form()],
    project_description: Annotated[str, Form()],
    costs: Annotated[float, Form()],
    attachment: Annotated[UploadFile | None, File()] = None,
) -> dict:
    """Create a new application and trigger the voting process."""
    application_data = {
        "first_name": first_name,
        "last_name": last_name,
        "applicant_email": applicant_email,
        "department": department,
        "project_title": project_title,
        "project_description": project_description,
        "costs": costs,
    }
    new_application = Application(
        **application_data,
        status=ApplicationStatus.PENDING.value,
    )
    db.add(new_application)
    await db.flush()  # Flush to get the application ID

    if attachment and attachment.filename:
        # Ensure the uploads directory exists
        uploads_dir = settings.project_root / "data" / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename and create a unique path
        file_extension = Path(attachment.filename).suffix
        saved_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = uploads_dir / saved_filename

        # Save the file asynchronously
        contents = await attachment.read()
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(contents)

        # Create the attachment record
        new_attachment = Attachment(
            application_id=new_application.id,
            filename=attachment.filename,
            filepath=str(file_path.relative_to(settings.project_root)),
            mime_type=attachment.content_type or "application/octet-stream",
        )
        db.add(new_attachment)

    # Refresh the application with attachments relationship loaded
    await db.refresh(new_application, attribute_names=["attachments"])

    # Generate vote records and send links
    await send_voting_links(new_application, db, board_members, settings)
    await db.commit()  # Commit all changes (application, attachment, and vote records)

    return {
        "message": "Application submitted successfully",
        "application_id": new_application.id,
    }


@app.get("/vote/{token}")
async def get_vote_details(
    token: str, db: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
    """Fetch application details using a secure token."""
    result = await db.execute(
        select(VoteRecord)
        .where(VoteRecord.token == token)
        .options(
            selectinload(VoteRecord.application).selectinload(Application.attachments)
        ),
    )
    vote_record = result.scalar_one_or_none()

    if not vote_record:
        raise HTTPException(status_code=404, detail="Invalid or expired token.")

    if vote_record.vote_status == VoteStatus.CAST.value:  # type: ignore[truthy-bool]
        raise HTTPException(status_code=400, detail="This vote has already been cast.")

    app = vote_record.application
    application_data = {
        "id": app.id,
        "project_title": app.project_title,
        "project_description": app.project_description,
        "costs": app.costs,
        "department": app.department,
        "attachments": [AttachmentOut.model_validate(att) for att in app.attachments],
    }

    return {
        "voter_email": vote_record.voter_email,
        "application": application_data,
        "vote_options": [option.value for option in VoteOption],
    }


@app.post("/vote/{token}")
async def cast_vote(
    token: str,
    vote_data: VoteCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    board_members: Annotated[list[str], Depends(get_board_members)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> dict:
    """Cast a vote using a secure token and checks if voting is complete."""
    result = await db.execute(select(VoteRecord).where(VoteRecord.token == token))
    vote_record = result.scalar_one_or_none()

    if not vote_record:
        raise HTTPException(status_code=404, detail="Invalid or expired token.")

    if vote_record.vote_status == VoteStatus.CAST.value:  # type: ignore[truthy-bool]
        raise HTTPException(status_code=400, detail="Vote has already been cast.")

    # Update vote record
    vote_record.vote = vote_data.decision.value  # type: ignore[attr-defined]
    vote_record.vote_status = VoteStatus.CAST.value  # type: ignore[attr-defined]
    await db.commit()

    # After a vote is cast, check if the voting process is complete.
    await _check_and_finalize_voting(
        int(vote_record.application_id),  # type: ignore[arg-type]
        db,
        board_members,
        settings,
    )

    return {"message": "Vote cast successfully"}


@app.get("/vote/{token}/attachments/{attachment_id}")
async def get_attachment(
    token: str,
    attachment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> FileResponse:
    """Get an attachment associated with a vote token."""
    # Validate token
    result = await db.execute(
        select(VoteRecord)
        .where(VoteRecord.token == token)
        .options(
            selectinload(VoteRecord.application).selectinload(Application.attachments)
        )
    )
    vote_record = result.scalar_one_or_none()

    if not vote_record:
        raise HTTPException(status_code=404, detail="Invalid or expired token.")

    # Find the requested attachment in the application's attachments
    attachment = None
    for att in vote_record.application.attachments:
        if att.id == attachment_id:
            attachment = att
            break

    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found.")

    # Construct the full file path
    file_path = settings.project_root / attachment.filepath

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found on disk.")

    return FileResponse(
        path=file_path,
        filename=attachment.filename,
        media_type=attachment.mime_type,
    )


@app.get("/attachments/{attachment_id}")
async def get_attachment_public(
    attachment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> FileResponse:
    """Get an attachment by ID (public access for archive)."""
    result = await db.execute(select(Attachment).where(Attachment.id == attachment_id))
    attachment = result.scalar_one_or_none()

    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found.")

    # Construct the full file path
    file_path = settings.project_root / attachment.filepath

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found on disk.")

    return FileResponse(
        path=file_path,
        filename=attachment.filename,
        media_type=attachment.mime_type,
    )


@app.get("/applications/archive")
async def get_applications_archive(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ApplicationOut]:
    """Return a list of all applications with their current status and votes."""
    result = await db.execute(
        select(Application)
        .options(selectinload(Application.votes), selectinload(Application.attachments))
        .order_by(Application.id.desc()),
    )
    applications = result.scalars().unique().all()

    return [ApplicationOut.model_validate(app) for app in applications]
