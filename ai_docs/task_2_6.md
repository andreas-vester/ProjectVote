# Task 2.6: File Upload in Submission Form

## Goal
Update the frontend application submission form to include a file upload feature, allowing users to attach supporting documents.

## Plan
1.  Add a file input field to the application form.
2.  Implement client-side validation for file type and size.
3.  Update the API service to handle file uploads.
4.  Provide user feedback on the upload process.

## Tasks

### Phase 1: Form Modification
*   [x] Add a file input component to the `ApplicationForm.tsx`.
*   [x] Style the file input to be user-friendly.

### Phase 2: Client-Side Validation
*   [x] Implement validation to restrict file types (e.g., PDF, XLSX, DOCX).
*   [x] Add a file size limit to prevent large uploads.
*   [x] Provide clear error messages for invalid files.

### Phase 3: API Integration
*   [x] Modify the `submitApplication` function in `apiService.ts` to send `multipart/form-data`.
*   [x] Update the form submission logic in `ApplicationForm.tsx` to include the file in the request.

### Phase 4: User Feedback
*   [x] Display the name of the selected file.
*   [x] Show a progress indicator during file upload.
*   [x] Provide clear success or error messages related to the file upload.
