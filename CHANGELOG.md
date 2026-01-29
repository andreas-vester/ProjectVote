# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fix

- Database migration for fresh deployments ([GH#20](https://github.com/andreas-vester/ProjectVote/issues/20)).

### Added

- Timezone environment variable ([GH#22](https://github.com/andreas-vester/ProjectVote/issues/22)).

## [0.5.0] - 2026-01-23

### Added

- ``send_automatic_confirmation_email`` setting ([GH#16](https://github.com/andreas-vester/ProjectVote/issues/16)).

## [0.4.0] - 2026-01-23

### Added

- Time stamps recording the time of application creation and conclusion and time of individual voting casts ([GH#12](https://github.com/andreas-vester/ProjectVote/issues/12)).

### Changed

- Make email configuration to be service-agnostic

## [0.3.0] - 2025-11-12

### Added

- Applicant receives confirmation email upon application submission ([GH#7](https://github.com/andreas-vester/ProjectVote/issues/7)).
- Email content enriched, now contains all details regarding an application ([GH#8](https://github.com/andreas-vester/ProjectVote/issues/8) and ([GH#9](https://github.com/andreas-vester/ProjectVote/issues/9))).

## [0.2.0] - 2025-11-09

### Added

- Implement early voting conclusion ([GH#1](https://github.com/andreas-vester/ProjectVote/issues/1)).
- Disable automatic rejection emails for personalized feedback ([GH#3](https://github.com/andreas-vester/ProjectVote/issues/3)).

## [0.1.0] - 2025-10-24

### Added

- Initial project setup with core functionalities.
- User-friendly form for submitting new funding requests.
- Secure, unique voting links for board members to review and cast votes.
- Automatic status updates and notifications based on board votes.
- Historical record of all funding applications and their outcomes.
- German localization for the user interface.

[Unreleased]: git@github.com:andreas-vester/ProjectVote/compare/0.5.0...master
[0.5.0]: git@github.com:andreas-vester/ProjectVote/compare/0.4.0...0.5.0
[0.4.0]: git@github.com:andreas-vester/ProjectVote/compare/0.3.0...0.4.0
[0.3.0]: git@github.com:andreas-vester/ProjectVote/compare/0.2.0...0.3.0
[0.2.0]: git@github.com:andreas-vester/ProjectVote/compare/0.1.0...0.2.0
[0.1.0]: git@github.com:andreas-vester/ProjectVote/tree/0.1.0
