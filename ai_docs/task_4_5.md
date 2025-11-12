# Task 4.5: Application Confirmation Notification

## Goal
Implement an automated confirmation email to the applicant upon successful submission of a new funding application, ensuring they have a record of their submission.

## Plan
1.  Create a new, dedicated email template for the applicant confirmation.
2.  Integrate the email sending logic into the application submission endpoint.
3.  Ensure all submitted data is included in the email for the applicant's reference.
4.  Verify the functionality through testing and local email inspection.

## Tasks

### Phase 1: Email Template Creation
*   [x] Create a new HTML email template named `application_confirmation.html` in `src/projectvote/backend/templates/email/`.
*   [ ] The template should be designed to clearly display all key application details:
    *   Applicant's Full Name
    *   Applicant's Email
    *   Department
    *   Project Title
    *   Project Description
    *   Estimated Costs
*   [x] The template should also acknowledge if a file was attached (e.g., "Your attachment '[filename]' was successfully uploaded.").
*   [x] The template should contain a link to the archive of the web app.

### Phase 2: Backend Integration
*   [x] Modify the `submit_application` function in `src/projectvote/backend/main.py`.
*   [x] After successfully saving the application and any attachments, call the `send_email` function.
*   [x] The recipient for this email should be the `applicant_email` from the submitted data.
*   [x] Pass all necessary application data (including details of the attachment, if any) to the `application_confirmation.html` template.

### Phase 3: Verification
*   [x] Add a unit test to verify that the email sending function is called with the correct parameters (recipient, subject, template) upon a successful application submission.
*   [x] Use MailHog during local development to visually inspect the email and confirm its content, formatting, and accuracy.
