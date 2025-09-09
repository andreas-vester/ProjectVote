# Task 3.5: Organization Name Configuration

## Goal
Make the organization's name configurable via an environment variable and integrate it into relevant parts of the application, such as email templates and the frontend display.

## Plan
1.  Define a new environment variable (e.g., `ORGANIZATION_NAME`) in `.env.example`.
2.  Load this variable into the central configuration module (`config.py`).
3.  Update email templates (e.g., `final_decision_applicant.html`, `new_application.html`, `final_decision_board.html`) to use this configurable name.
4.  Update the frontend (e.g., `App.tsx`) to display this configurable name.
5.  Ensure the name is accessible and used consistently across the application.

## Tasks

### Phase 1: Environment Variable and Configuration
*   [ ] Add `ORGANIZATION_NAME` to `.env.example` with a default value (e.g., "Your Organization Name").
*   [ ] Add `organization_name: str` to the `Settings` class in `src/projectvote/backend/config.py`, loading it from the environment.

### Phase 2: Integration into Templates and Frontend
*   [ ] Modify `src/projectvote/backend/templates/email/final_decision_applicant.html` to use `{{ organization_name }}` instead of hardcoded "ProjectVote".
*   [ ] Modify `src/projectvote/backend/templates/email/final_decision_board.html` to use `{{ organization_name }}`.
*   [ ] Modify `src/projectvote/backend/templates/email/new_application.html` to use `{{ organization_name }}`.
*   [ ] Update the backend logic (e.g., in `main.py` where emails are sent) to pass `organization_name` to the email templates.
*   [ ] Update `src/projectvote/frontend/src/App.tsx` to fetch and display the `ORGANIZATION_NAME` from the backend or directly from a frontend environment variable if preferred for display purposes.

### Phase 3: Verification
*   [ ] Run tests to ensure the new configuration is loaded correctly.
*   [ ] Verify that the organization name appears correctly in emails and on the frontend.
