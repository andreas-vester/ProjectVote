# Task 1.2: Application Submission API

## Goal
Develop a backend API endpoint that allows users to submit new funding applications, including all necessary data validation and initial processing.

## Plan
1.  Define the API endpoint path and HTTP method.
2.  Specify the request body structure for application data.
3.  Implement data validation for incoming application data.
4.  Handle the storage of new application data in the database.
5.  Define the API response structure for successful submissions.

## Tasks

### Phase 1: API Endpoint Definition
*   [x] Choose an appropriate HTTP method (e.g., POST) and path (e.g., `/applications`) for the submission endpoint.
*   [x] Define the Pydantic model for the incoming application data, including fields like `first_name`, `last_name`, `applicant_email`, `department`, `project_title`, `project_description`, and `costs`. Ensure proper data types and validation rules (e.g., email format, non-empty strings, positive costs).

### Phase 2: Application Data Processing
*   [x] Implement the API endpoint function in the backend framework (e.g., FastAPI).
*   [x] Receive and validate the incoming application data using the defined Pydantic model.
*   [x] Create a new `Application` record in the database using the ORM, setting its initial status (e.g., `PENDING`).
*   [x] Handle potential database errors during the creation process.

### Phase 3: Response and Error Handling
*   [x] Define a success response structure, including a confirmation message and a unique identifier for the submitted application.
*   [x] Implement appropriate error handling for validation failures (e.g., 422 Unprocessable Entity) and internal server errors (e.g., 500 Internal Server Error).
