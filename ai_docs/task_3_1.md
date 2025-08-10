# Task 3.1: Email Service Configuration

## Goal
Configure a reliable email service to handle all outgoing email notifications from the application, ensuring a clear separation of configuration for different environments.

## Plan
1.  Select an appropriate email sending service.
2.  Implement a configuration module for email settings.
3.  Create a reusable email sending function.
4.  Ensure the service is easily mockable for testing.

## Tasks

### Phase 1: Service Selection and Setup
*   [ ] Research and choose an email service provider (e.g., SendGrid, Mailgun, Amazon SES).
*   [ ] Create an account and obtain API keys for development and production environments.
*   [ ] Store API keys securely using environment variables or a secrets management tool.

### Phase 2: Configuration Module
*   [ ] Create a new module (e.g., `email_service.py`) in the backend.
*   [ ] Implement a function to load email configuration (e.g., API key, sender email) from environment variables.
*   [ ] Use Pydantic for configuration validation.

### Phase 3: Reusable Email Function
*   [ ] Create a generic function (e.g., `send_email`) that takes the recipient, subject, and body as arguments.
*   [ ] This function should use the chosen email service's API to send the email.
*   [ ] Implement basic error handling for email sending failures.

### Phase 4: Testability
*   [ ] Ensure the `send_email` function can be easily mocked in tests to prevent actual emails from being sent during test runs.
*   [ ] Write a unit test for the email sending function using a mock of the email service.
