# Task 4.4: Configurable Rejection Emails

## Goal
Provide an option to disable the automatic sending of rejection emails to applicants, allowing the board to send personalized feedback instead.

## Plan
1.  Add a new environment variable to control the behavior.
2.  Update the configuration module to load the new variable.
3.  Modify the email sending logic to respect the new setting.
4.  Update documentation and tests.

## Tasks

### Phase 1: Configuration
- [x] Add `SEND_AUTOMATIC_REJECTION_EMAIL` to `.env.example` with a default value of `true`.
- [x] Add `send_automatic_rejection_email: bool` to the `Settings` class in `src/projectvote/backend/config.py`.

### Phase 2: Backend Logic
- [x] In `src/projectvote/backend/main.py`, modify the `send_final_decision_emails` function.
- [x] Add a condition to check `settings.send_automatic_rejection_email` before sending the email to the applicant if the status is `REJECTED`.
- [x] Ensure that emails to the board and for `APPROVED` applications are unaffected.

### Phase 3: Verification
- [x] Update existing tests or add new ones to verify the conditional email logic.
- [x] Test the scenario where the flag is `true` and `false`.
