# Task 1.4: Application Archive API

## Goal
Create a backend API endpoint that provides access to a historical archive of all funding applications, including their final status and individual vote records.

## Plan
1.  Define the API endpoint for retrieving archived applications.
2.  Implement data retrieval from the database, including related vote records.
3.  Structure the API response for easy consumption by the frontend.

## Tasks

### Phase 1: API Endpoint Definition
*   [x] Choose an appropriate HTTP method (e.g., GET) and path (e.g., `/applications/archive` or `/applications`) for retrieving archived applications.
*   [ ] Consider pagination or filtering parameters if the number of applications is expected to be large.

### Phase 2: Data Retrieval and Aggregation
*   [x] Implement the API endpoint function in the backend framework.
*   [x] Query the database to retrieve all `Application` records.
*   [x] For each application, retrieve all associated `VoteRecord`s.
*   [x] Ensure efficient data retrieval, potentially using ORM eager loading to minimize database queries.

### Phase 3: Response Structuring
*   [x] Define the Pydantic model for the API response, ensuring it includes:
    *   All `Application` details (e.g., project title, description, costs, final status).
    *   A list of associated `VoteRecord`s, each containing voter identification and their decision.
*   [x] Format the retrieved data into the defined response structure.
*   [x] Implement appropriate error handling for cases where no applications are found.
