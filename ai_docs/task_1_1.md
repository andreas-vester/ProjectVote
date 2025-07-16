# Task 1.1: Database Schema Definition

## Goal
Design and implement the initial database schema to support the core entities of the funding application system (Applications, VoteRecords), ensuring it aligns with the project's functional requirements.

## Plan
1.  Identify the core data entities and their attributes required for the application.
2.  Define the relationships between these entities.
3.  Implement the database schema using an Object-Relational Mapper (ORM).
4.  Establish a mechanism for database initialization and table creation.

## Tasks

### Phase 1: Entity and Relationship Design
*   [ ] Identify primary entities: `Application` and `VoteRecord`.
*   [ ] Define essential attributes for the `Application` entity, including:
    *   Applicant details (e.g., first name, last name, email)
    *   Project details (e.g., title, description, costs, department)
    *   Application status (e.g., pending, approved, rejected)
*   [ ] Define essential attributes for the `VoteRecord` entity, including:
    *   Associated application
    *   Voter identification (e.g., email)
    *   Unique voting token
    *   Vote decision (e.g., approve, reject)
    *   Vote status (e.g., pending, cast)
*   [ ] Establish the one-to-many relationship: one `Application` can have multiple `VoteRecord`s.

### Phase 2: ORM Model Implementation
*   [ ] Choose an appropriate ORM (e.g., SQLAlchemy) for Python backend.
*   [ ] Create Python classes (models) representing the `Application` and `VoteRecord` entities, mapping their attributes to database columns.
*   [ ] Define primary keys, foreign keys, data types, and constraints for all columns.
*   [ ] Implement the relationship between the `Application` and `VoteRecord` models within the ORM.

### Phase 3: Database Initialization
*   [ ] Set up the database connection configuration (e.g., SQLite for development).
*   [ ] Implement a function or mechanism to create all defined database tables based on the ORM models upon application startup.
*   [ ] Verify that the database file is created and tables are present after initial application run.
