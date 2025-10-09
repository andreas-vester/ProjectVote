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
*   [ ] Add a file input component to the `ApplicationForm.tsx`.
*   [ ] Style the file input to be user-friendly.

### Phase 2: Client-Side Validation
*   [ ] Implement validation to restrict file types (e.g., PDF, XLSX, DOCX).
*   [ ] Add a file size limit to prevent large uploads.
*   [ ] Provide clear error messages for invalid files.

### Phase 3: API Integration
*   [ ] Modify the `submitApplication` function in `apiService.ts` to send `multipart/form-data`.
*   [ ] Update the form submission logic in `ApplicationForm.tsx` to include the file in the request.

### Phase 4: User Feedback
*   [ ] Display the name of the selected file.
*   [ ] Show a progress indicator during file upload.
*   [ ] Provide clear success or error messages related to the file upload.
