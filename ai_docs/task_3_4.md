# Task 3.4: Personalized Board Member Emails

## Goal
Extend the board member configuration to include names, allowing for personalized email communication.

## Plan
1.  Update the database schema to store board member names.
2.  Modify the configuration to support names alongside email addresses.
3.  Adjust the backend logic to parse the new configuration and use the names in email templates.
4.  Update the email templates to include personalized greetings.

## Tasks

### Phase 1: Database and Configuration
*   [ ] Add a `first_name` and `last_name` field to the `BoardMember` model in `models.py`.
*   [ ] Add `status` field to the `BoardMember` model in `models.py`. It could hold the values `active` or `retired`.
*   [ ] Update the `BOARD_MEMBERS` environment variable format in `.env.example` to `"Display Name <email@example.com>, ..."`. Take also care about the `status` field.
*   [ ] Modify the `get_board_members` function in `main.py` to parse the new format and return a list of objects with `name` and `email`.

### Phase 2: Backend Logic and Templates
*   [ ] Update the `send_voting_links` function in `main.py` to pass the board member's name to the email template.
*   [ ] Update the `send_final_decision_emails` function in `main.py` to pass the board member's name to the email template.
*   [ ] Modify the `new_application.html` and `final_decision_board.html` templates to use the board member's name.

### Phase 3: Verification
*   [ ] Run tests to ensure the new configuration is parsed correctly.
*   [ ] Use a local email testing tool to verify that board members receive personalized emails.
