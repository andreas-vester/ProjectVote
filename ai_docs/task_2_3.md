# Task 2.3: Application Archive View

## Goal
Develop a frontend component that displays a comprehensive archive of all funding applications, including their current status and individual vote details.

## Plan
1.  Design the layout for displaying a list of applications.
2.  Integrate with the backend API to fetch all application data.
3.  Implement features to display vote details for each application.
4.  Handle empty states and loading indicators.

## Tasks

### Phase 1: Component Structure and Data Display
*   [ ] Create a new React component for the application archive.
*   [ ] Design a tabular or list-based layout to display key application details (e.g., project title, applicant, department, costs, status).
*   [ ] Implement a mechanism to expand/collapse rows or sections to reveal detailed vote records for each application.

### Phase 2: Fetching Archive Data
*   [ ] Implement a function to make a GET request to the backend's application archive API endpoint.
*   [ ] Handle loading states while data is being fetched.
*   [ ] Display a clear message or visual indicator when no applications are available (empty state).

### Phase 3: Displaying Vote Details
*   [ ] Within the expanded view for each application, display the `voter_email` and `decision` for each `VoteRecord`.
*   [ ] Format the vote decisions (e.g., "Approved", "Rejected") for user readability.

### Phase 4: User Experience and Interactivity
*   [ ] Ensure smooth transitions for expanding/collapsing vote details.
*   [ ] Implement basic styling for readability and visual appeal.
*   [ ] Consider adding filtering or sorting options if the archive is expected to grow large.
