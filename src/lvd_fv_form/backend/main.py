import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException

from sqlalchemy.orm import Session, selectinload
from lvd_fv_form.backend.database import engine, get_db
from lvd_fv_form.backend.models import (
    Application,
    VoteRecord,
    VoteOption,
    ApplicationStatus,
    Base,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown (if needed)


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",  # React app (Vite default port)
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In a real application, these would be stored in a database
BOARD_MEMBERS = [
    "board.member1@example.com",
    "board.member2@example.com",
    "board.member3@example.com",
]


async def send_voting_links(application: Application):
    """Simulates sending emails to board members with voting links."""
    print("\n--- Simulating Email Notifications ---")
    for member_email in BOARD_MEMBERS:
        # In a real app, you'd use a library like `smtplib` to send actual emails
        vote_url = f"/applications/{application.id}/vote"
        print(f"To: {member_email}")
        print(f"Subject: New Funding Application: {application.project_title}")
        print(
            f"A new application has been submitted. Please cast your vote here: {vote_url}"
        )
        print("---")
    print("--- End of Simulation ---\n")


@app.get("/", response_model=dict)
async def read_root():
    return {"message": "Welcome to the Funding Application API"}


class ApplicationCreate(BaseModel):
    first_name: str
    last_name: str
    applicant_email: str
    department: str
    project_title: str
    project_description: str
    costs: float


class VoteCreate(BaseModel):
    voter_email: str
    decision: VoteOption


@app.post("/applications", response_model=dict)
async def submit_application(
    application_data: ApplicationCreate, db: Session = Depends(get_db)
):
    new_application = Application(
        first_name=application_data.first_name,
        last_name=application_data.last_name,
        applicant_email=application_data.applicant_email,
        department=application_data.department,
        project_title=application_data.project_title,
        project_description=application_data.project_description,
        costs=application_data.costs,
        status=ApplicationStatus.PENDING,
    )
    db.add(new_application)
    await db.commit()
    await db.refresh(new_application)

    # Run email simulation in the background
    # asyncio.create_task(send_voting_links(new_application, request)) # Request object is no longer available here
    # For now, we'll just print the simulated email links to console
    print("\n--- Simulating Email Notifications ---")
    for member_email in BOARD_MEMBERS:
        print(f"To: {member_email}")
        print(f"Subject: New Funding Application: {new_application.project_title}")
        print(
            f"A new application has been submitted. Please cast your vote here: /applications/{new_application.id}/vote"
        )
        print("---")
    print("--- End of Simulation ---\n")

    return {
        "message": "Application submitted successfully",
        "application_id": new_application.id,
    }


@app.get("/applications/{application_id}", response_model=dict)
async def get_application_details(application_id: int, db: Session = Depends(get_db)):
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Prepare data for JSON response
    application_data = {
        "id": application.id,
        "first_name": application.first_name,
        "last_name": application.last_name,
        "applicant_email": application.applicant_email,
        "department": application.department,
        "project_title": application.project_title,
        "project_description": application.project_description,
        "costs": application.costs,
        "status": application.status.value,
    }
    vote_options = [option.value for option in VoteOption]

    return {"application": application_data, "vote_options": vote_options}


async def send_final_decision_emails(application: Application):
    """Simulates sending final decision emails to the applicant and board members."""
    print("\n--- Simulating Final Decision Emails ---")
    # Notification to Applicant
    print(f"To: {application.applicant_email}")
    print(f"Subject: Decision on your application: {application.project_title}")
    print(f"Dear {application.first_name} {application.last_name},\n")
    print(
        f"A decision has been reached for your funding application. The project has been {application.status.value.upper()}."
    )
    print("---")

    # Notification to Board Members
    for member_email in BOARD_MEMBERS:
        print(f"To: {member_email}")
        print(f"Subject: Voting concluded for: {application.project_title}")
        print(f"The application was {application.status.value.upper()}.")
        print("---")
    print("--- End of Simulation ---\n")


@app.post("/applications/{application_id}/vote", response_model=dict)
async def cast_vote(
    application_id: int, vote_data: VoteCreate, db: Session = Depends(get_db)
):
    # Check for the application
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Check if this member has already voted
    result = await db.execute(
        select(VoteRecord).where(
            VoteRecord.application_id == application_id,
            VoteRecord.voter_email == vote_data.voter_email,
        )
    )
    existing_vote = result.scalar_one_or_none()

    if existing_vote:
        raise HTTPException(
            status_code=400,
            detail=f"Voter {vote_data.voter_email} has already voted on this application.",
        )

    new_vote = VoteRecord(
        application_id=application_id,
        voter_email=vote_data.voter_email,
        vote=vote_data.decision,
    )
    db.add(new_vote)
    await db.commit()

    # --- Start of new logic: Check if voting is complete ---
    # Get all votes for this application
    result = await db.execute(
        select(VoteRecord).where(VoteRecord.application_id == application_id)
    )
    all_votes = result.scalars().all()

    if len(all_votes) >= len(BOARD_MEMBERS):
        # Count votes
        approvals = sum(1 for vote in all_votes if vote.vote == VoteOption.APPROVE)
        # Simple majority decides
        if approvals > len(BOARD_MEMBERS) / 2:
            application.status = ApplicationStatus.APPROVED
        else:
            application.status = ApplicationStatus.REJECTED

        await db.commit()

        # Send final notifications
        asyncio.create_task(send_final_decision_emails(application))

    return {"message": "Vote cast successfully"}


@app.get(
    "/applications", response_model=list
)  # Changed from /archive to /applications for consistency
async def view_applications(db: Session = Depends(get_db)):
    result = await db.execute(
        select(Application)
        .options(selectinload(Application.votes))
        .order_by(Application.id.desc())
    )
    applications = result.scalars().all()

    # Convert applications and their votes to a serializable format
    applications_data = []
    for app in applications:
        app_data = {
            "id": app.id,
            "first_name": app.first_name,
            "last_name": app.last_name,
            "applicant_email": app.applicant_email,
            "department": app.department,
            "project_title": app.project_title,
            "project_description": app.project_description,
            "costs": app.costs,
            "status": app.status.value,
            "votes": [],
        }
        for vote in app.votes:
            app_data["votes"].append(
                {"voter_email": vote.voter_email, "decision": vote.vote.value}
            )
        applications_data.append(app_data)

    return applications_data
