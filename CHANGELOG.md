# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Database migration for fresh deployments ([GH#20](https://github.com/andreas-vester/ProjectVote/issues/20)).
- Ensure ownership change runs after migrations so database files created
	during `alembic upgrade head` are owned by `appuser`, preventing
	"readonly database" errors when the app runs as a non-root user ([GH#25](https://github.com/andreas-vester/ProjectVote/issues/25)).
- Standardize all database timestamps to UTC and implement localized display based on the configured timezone ([GH#22](https://github.com/andreas-vester/ProjectVote/issues/22)).
- Allow larger attachment uploads through the frontend nginx proxy by increasing `client_max_body_size`, preventing `413 Request Entity Too Large` failures for PDF attachments.

### Added

- Timezone configuration setting (`TZ`) to support custom organization locations ([GH#22](https://github.com/andreas-vester/ProjectVote/issues/22)).

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
