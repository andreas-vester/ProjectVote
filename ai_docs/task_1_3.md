# Task 1.3: Voting Process API

## Goal
Implement backend API endpoints to manage the token-based voting process for board members, including retrieving application details for voting and casting votes.

## Plan
1.  Design API endpoints for vote details retrieval and vote submission.
2.  Implement token validation and security measures.
3.  Handle vote recording and update application status based on voting rules.
4.  Integrate with email simulation for sending voting links.

## Tasks

### Phase 1: Vote Details Retrieval Endpoint
*   [x] Define an API endpoint (e.g., `GET /vote/{token}`) to allow board members to retrieve application details using a unique token.
*   [x] Implement logic to validate the provided token against stored `VoteRecord`s.
*   [x] If the token is valid, retrieve and return the associated application details.
*   [x] Handle cases for invalid, expired, or already-used tokens (e.g., 404 Not Found, 400 Bad Request).

### Phase 2: Vote Submission Endpoint
*   [x] Define an API endpoint (e.g., `POST /vote/{token}`) for board members to submit their vote (approve/reject).
*   [x] Define the Pydantic model for the incoming vote data (e.g., `decision`).
*   [x] Implement logic to validate the token and ensure the vote has not been cast previously.
*   [x] Record the vote in the database, updating the `VoteRecord` status.
*   [x] After a vote is cast, check if all votes for the associated application have been received.
*   [x] If all votes are in, apply the decision logic: simple majority of non-abstaining votes (approve vs. reject). A tie among decisive votes or all abstentions results in rejection. Update the `Application` status accordingly.
*   [x] Handle appropriate success and error responses.

### Phase 3: Email Simulation Integration
*   [x] Implement a function to generate unique tokens for each board member upon application submission.
*   [x] Integrate this function with the application submission process to create `VoteRecord`s.
*   [x] Implement a simulated email sending mechanism to "send" these unique voting links to board members.
*   [x] Implement a simulated email sending mechanism to "send" final decision notifications to applicants and board members.
