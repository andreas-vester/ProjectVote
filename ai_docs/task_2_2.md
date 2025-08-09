# Task 2.2: Token-Based Voting Form

## Goal
Develop a frontend component that allows board members to view application details and cast their vote using a unique, token-based URL.

## Plan
1.  Design the layout for displaying application details and voting options.
2.  Implement logic to extract the token from the URL.
3.  Integrate with backend API to fetch application details and submit votes.
4.  Provide clear feedback on voting status and errors.

## Tasks

### Phase 1: Component Structure and Routing
*   [x] Create a new React component for the voting form.
*   [x] Configure frontend routing to handle URLs with a token parameter (e.g., `/vote/:token`).
*   [x] Extract the token from the URL parameters when the component loads.

### Phase 2: Fetching Application Details
*   [x] Use the extracted token to make a GET request to the backend's vote details API endpoint.
*   [x] Display the retrieved application details (project title, description, costs, department) in a clear and readable format.
*   [x] Handle cases where the token is invalid, expired, or already used, displaying appropriate error messages to the user.

### Phase 3: Vote Submission
*   [x] Provide clear voting options (e.g., "Approve", "Reject") using UI components (e.g., radio buttons, buttons).
*   [x] Implement a function to handle vote submission, sending the chosen decision along with the token to the backend's vote submission API endpoint (POST request).
*   [x] Handle successful vote submissions (e.g., display a confirmation message, disable further voting).
*   [x] Handle API errors during vote submission (e.g., network issues, server errors).

### Phase 4: User Feedback and State Management
*   [x] Implement visual feedback (e.g., loading indicators, success/error messages, snackbar notifications) during API calls.
*   [x] Manage the component's state to reflect the current status (e.g., loading, displaying form, vote submitted, error).
