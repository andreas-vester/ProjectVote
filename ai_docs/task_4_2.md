# Task 4.2: New Application Notification

## Goal
Integrate the email service to automatically send notifications to all board members upon the successful submission of a new funding application.

## Plan
1.  Integrate the email sending function into the application submission endpoint.
2.  Create an email template for the new application notification.
3.  Ensure all board members receive their unique voting links in the email.

## Tasks

### Phase 1: Email Template
*   [x] Design a clear and informative email template.
*   [x] The template should include:
    *   The project title.
    *   The applicant's name.
    *   The estimated costs.
    *   A direct, unique link to the voting page (e.g., `http://localhost:5173/vote/{token}`).
*   [x] Consider using a simple HTML template for better formatting.

### Phase 2: Integration with Submission Endpoint
*   [x] In the `/applications` endpoint in `main.py`, after a new application is successfully created and vote records are generated, call the `send_email` function.
*   [x] Loop through each board member and send them a personalized email.

### Phase 3: Verification
*   [x] During development, use a tool like MailHog or a similar local SMTP server to capture and inspect outgoing emails.
*   [x] Verify that each board member receives an email with the correct, unique voting link.
*   [x] Confirm that the email content accurately reflects the submitted application details.
