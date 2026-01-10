# Task 2.7: Display Timestamps in Application Archive

## Goal
Update the frontend application archive to display the `created_at`, `voted_at`, and `concluded_at` timestamps, providing more detailed information about the application lifecycle.

## Plan
1.  Update the backend API to include the new timestamp fields in the data transfer objects (DTOs).
2.  Modify the frontend archive component to display the `created_at` and `concluded_at` timestamps for each application.
3.  Update the expanded view in the archive to show the `voted_at` timestamp for each individual vote.
4.  Format the timestamps for user-friendly display.

## Tasks

### Phase 1: Backend API Update
*   [x] Add `created_at` and `concluded_at` fields to the `ApplicationOut` Pydantic model in `src/projectvote/backend/main.py`.
*   [x] Add `voted_at` field to the `VoteOut` Pydantic model in `src/projectvote/backend/main.py`.
*   [x] Ensure the new fields are correctly populated and returned by the `/applications/archive` endpoint.

### Phase 2: Frontend Archive Component
*   [x] Update the `Archive.tsx` component to fetch the new timestamp fields.
*   [x] Display `created_at` and `concluded_at` for each application in the main archive view.
*   [x] In the expanded section for each application, display the `voted_at` timestamp next to each vote.
*   [x] Implement a function to format the timestamp strings into a more readable format (e.g., "Jan 7, 2026, 10:30 AM").
