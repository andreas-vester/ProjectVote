# Task 4.3: Final Decision Notification

## Goal
Automate the sending of final decision emails to both the applicant and all board members once voting on an application is complete.

## Plan
1.  Integrate the email sending function into the voting completion logic.
2.  Create separate email templates for the applicant and board members.
3.  Ensure the final status (approved or rejected) is clearly communicated.

## Tasks

### Phase 1: Integration with Voting Logic
*   [x] In the `/vote/{token}` endpoint, after the final vote is cast and the application status is updated, trigger the email notification process.
*   [x] Call the `send_email` function to notify the applicant and all board members. (Note: Sending rejection emails to applicants will be made configurable in Task 4.4).

### Phase 2: Applicant Email Template
*   [x] Design an email template for the applicant.
*   [x] The template should:
    *   [x] Clearly state the final decision (approved or rejected).
    *   [x] It should contain:
        *   [x] Applicant's Full Name
        *   [x] Applicant's Email
        *   [x] Department
        *   [x] Project Title
        *   [x] Project Description
        *   [x] Estimated Costs
        *   [x] A link to the archive of the web app.
        *   [x] Thank the applicant for their submission.

### Phase 3: Board Member Email Template
*   [x] Design an email template for the board members.
*   [x] The template should:
    *   [x] Announce that voting is complete for a specific application.
    *   [x] State the final outcome.
    *   [x] It should contain:
        *   [x] Applicant's Full Name
        *   [x] Applicant's Email
        *   [x] Department
        *   [x] Project Title
        *   [x] Project Description
        *   [x] Estimated Costs
        *   [x] A link to the archive of the web app.

### Phase 4: Verification
*   [x] Use a local email testing tool to verify that both the applicant and all board members receive the correct notification.
*   [x] Test both "approved" and "rejected" scenarios to ensure the email content is accurate.
