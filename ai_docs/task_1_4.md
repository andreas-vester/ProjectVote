# Task 1.4: File Upload Handling

## Goal
Implement backend support for handling file uploads with application submissions, including file storage and linking to the application.

## Plan
1.  Update the database schema to store file information.
2.  Modify the application submission endpoint to accept file uploads.
3.  Implement file storage logic.
4.  Ensure uploaded files are accessible for review.

## Tasks

### Phase 1: Database Schema Update
*   [ ] Add a new table `Attachment` to store file metadata (e.g., filename, path, mime_type).
*   [ ] Establish a relationship between the `Application` and `Attachment` models.

### Phase 2: API Endpoint Modification
*   [ ] Update the `/applications` endpoint to handle `multipart/form-data` requests.
*   [ ] Modify the `ApplicationCreate` model to include an optional field for the uploaded file.
*   [ ] Implement logic to process and save the uploaded file.

### Phase 3: File Storage
*   [ ] Use the local filesystem for storing uploaded files.
*   [ ] Create a dedicated directory (e.g., `uploads/`) within the project's `data` directory.
*   [ ] This directory will be mapped as a Docker volume to ensure persistence.
*   [ ] Implement a service to save files to this directory, ensuring that filenames are sanitized and stored securely to prevent conflicts.

### Phase 4: File Access
*   [ ] Create a new API endpoint (e.g., `/attachments/{attachment_id}`) to serve uploaded files securely.
*   [ ] Ensure that only authorized users (e.g., board members) can access the files.
