import asyncio
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, get_db
from models import Application, VoteRecord, VoteOption, ApplicationStatus, Base

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# In a real application, these would be stored in a database
BOARD_MEMBERS = ["board.member1@example.com", "board.member2@example.com", "board.member3@example.com"]

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def send_voting_links(application: Application, request: Request):
    """Simulates sending emails to board members with voting links."""
    print("\n--- Simulating Email Notifications ---")
    for member_email in BOARD_MEMBERS:
        # In a real app, you'd use a library like `smtplib` to send actual emails
        vote_url = request.url_for('render_vote_form', application_id=application.id)
        print(f"To: {member_email}")
        print(f"Subject: New Funding Application: {application.project_title}")
        print(f"A new application has been submitted. Please cast your vote here: {vote_url}")
        print("---")
    print("--- End of Simulation ---\n")


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit", response_class=HTMLResponse)
async def submit_form(
    request: Request,
    db: Session = Depends(get_db),
    first_name: str = Form(...),
    last_name: str = Form(...),
    applicant_email: str = Form(...),
    department: str = Form(...),
    project_title: str = Form(...),
    project_description: str = Form(...),
    costs: float = Form(...)
):
    new_application = Application(
        first_name=first_name,
        last_name=last_name,
        applicant_email=applicant_email,
        department=department,
        project_title=project_title,
        project_description=project_description,
        costs=costs,
        status=ApplicationStatus.PENDING
    )
    db.add(new_application)
    await db.commit()
    await db.refresh(new_application)

    # Run email simulation in the background
    asyncio.create_task(send_voting_links(new_application, request))

    return templates.TemplateResponse("submission_success.html", {"request": request, "application": new_application})


from sqlalchemy import select

@app.get("/vote/{application_id}", response_class=HTMLResponse)
async def render_vote_form(request: Request, application_id: int, db: Session = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == application_id))
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return templates.TemplateResponse("vote.html", {
        "request": request,
        "application": application,
        "vote_options": [option.value for option in VoteOption]
    })

async def send_final_decision_emails(application: Application):
    """Simulates sending final decision emails to the applicant and board members."""
    print("\n--- Simulating Final Decision Emails ---")
    # Notification to Applicant
    print(f"To: {application.applicant_email}")
    print(f"Subject: Decision on your application: {application.project_title}")
    print(f"Dear {application.first_name} {application.last_name},")
    print(f"A decision has been reached for your funding application. The project has been {application.status.value.upper()}.")
    print("---")

    # Notification to Board Members
    for member_email in BOARD_MEMBERS:
        print(f"To: {member_email}")
        print(f"Subject: Voting concluded for: {application.project_title}")
        print(f"The application was {application.status.value.upper()}.")
        print("---")
    print("--- End of Simulation ---\n")

@app.post("/vote/{application_id}")
async def cast_vote(
    request: Request,
    application_id: int,
    voter_email: str = Form(...),
    decision: VoteOption = Form(...),
    db: Session = Depends(get_db)
):
    # Check for the application
    result = await db.execute(select(Application).where(Application.id == application_id))
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Check if this member has already voted
    result = await db.execute(
        select(VoteRecord).where(
            VoteRecord.application_id == application_id,
            VoteRecord.voter_email == voter_email
        )
    )
    existing_vote = result.scalar_one_or_none()

    if existing_vote:
        raise HTTPException(status_code=400, detail=f"Voter {voter_email} has already voted on this application.")

    new_vote = VoteRecord(
        application_id=application_id,
        voter_email=voter_email,
        vote=decision
    )
    db.add(new_vote)
    await db.commit()

    # --- Start of new logic: Check if voting is complete ---
    # Get all votes for this application
    result = await db.execute(select(VoteRecord).where(VoteRecord.application_id == application_id))
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

    return RedirectResponse(url=f"/vote/{application_id}/success", status_code=303)


from sqlalchemy.orm import Session, selectinload

@app.get("/archive", response_class=HTMLResponse)
async def view_archive(request: Request, db: Session = Depends(get_db)):
    result = await db.execute(
        select(Application).options(selectinload(Application.votes)).order_by(Application.id.desc())
    )
    applications = result.scalars().all()
    return templates.TemplateResponse("archive.html", {"request": request, "applications": applications})


@app.get("/vote/{application_id}/success", response_class=HTMLResponse)
async def vote_success(request: Request, application_id: int):
    return templates.TemplateResponse("vote_success.html", {"request": request, "application_id": application_id})
