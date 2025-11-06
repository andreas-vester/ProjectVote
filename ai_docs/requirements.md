# Project Requirements: ProjectVote

This document outlines the core functional requirements for the web application designed to manage funding applications for associations.

## 1. Application Submission

*   **Purpose:** Allow individuals to submit new funding requests.
*   **Features:**
    *   A user-friendly form for entering project details (title, description, costs, department).
    *   Collection of applicant's contact information (name, email).
    *   Optional file upload for supporting documents (PDF, XLSX, DOCX, etc.).

## 2. Token-Based Board Voting

*   **Purpose:** Enable board members to securely review and vote on submitted applications.
*   **Features:**
    *   Upon application submission, unique, secure voting links are generated for each board member.
    *   Board members receive email notifications with their individual voting links.
    *   Access to application details via the unique voting link.
    *   Ability to cast a vote (approve, reject, or abstain) through a dedicated form.
    *   Prevention of multiple votes from the same token.
    *   However, it should be possible to change vote until the voting closes.

## 3. Automated Decision Processing

*   **Purpose:** Automatically determine the application status based on board votes.
*   **Features:**
    *   The application status is automatically updated as soon as a definitive decision has been reached, even if not all board members have voted.
    *   Decision logic: A simple majority of cast votes determines the outcome. The voting closes as soon as an irreversible majority is reached. In case of a tie, the application is rejected.
    *   Email notifications are sent to the applicant and all board members once a final decision is reached.

## 4. Application Archive

*   **Purpose:** Provide a historical record of all funding applications and their outcomes.
*   **Features:**
    *   A view displaying all submitted applications.
    *   For each application, display key details like applicant name, project title, department, costs, and status (pending, approved, rejected).
    *   Ability to view expanded details for each application, including the full project description and individual vote decisions from board members.
