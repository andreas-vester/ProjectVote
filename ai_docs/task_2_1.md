# Task 2.1: Application Submission Form

## Goal
Develop a user-friendly frontend form that allows applicants to submit new funding requests to the backend API.

## Plan
1.  Design the form layout and input fields.
2.  Implement client-side validation for form inputs.
3.  Integrate with the backend API for form submission.
4.  Provide user feedback on submission status.

## Tasks

### Phase 1: Form Design and Structure
*   [x] Create the basic HTML structure for the application form.
*   [x] Include input fields for `first_name`, `last_name`, `applicant_email`, `department`, `project_title`, `project_description`, and `costs`.
*   [x] Utilize appropriate input types (e.g., text, email, number, textarea).
*   [x] Implement basic styling for a clean and intuitive user interface.

### Phase 2: Client-Side Validation
*   [x] Add client-side validation rules for each input field (e.g., required fields, email format, numeric costs).
*   [x] Provide immediate visual feedback to the user for invalid inputs.

### Phase 3: Backend API Integration
*   [x] Implement a function to handle form submission, collecting data from all input fields.
*   [x] Use an HTTP client library (e.g., Axios) to send a POST request to the backend's application submission API endpoint.
*   [x] Handle successful API responses (e.g., display a success message, clear the form).
*   [x] Handle API errors (e.g., display error messages for validation failures or server errors).

### Phase 4: User Experience Feedback
*   [x] Implement visual feedback mechanisms (e.g., loading indicators, success/error messages, snackbar notifications) to inform the user about the submission process and its outcome.
