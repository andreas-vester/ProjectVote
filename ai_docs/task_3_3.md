# Task 3.3: Board Member Configuration

## Goal
Manage the list of board members through the central configuration system instead of hardcoding it.

## Tasks
*   [x] The list of board member emails is defined by a `BOARD_MEMBERS` variable in the `.env` file.
*   [x] The `get_board_members` dependency function is refactored to source its data from the central configuration module.
*   [ ] The format of the `BOARD_MEMBERS` variable will be updated to support names and emails (e.g., `"Display Name <email@example.com>, ..."`).
