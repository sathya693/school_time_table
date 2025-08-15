# Technical Design Document: School Timetable Generator

This document provides a detailed technical overview of the School Timetable Generator application, including its architecture, data models, API endpoints, and core logic.

## 1. High-Level Architecture

The application is a **monolithic web application** built using the **Flask** web framework for Python. It serves a dynamic frontend built with **vanilla JavaScript**, HTML, and CSS.

-   **Backend:** The Flask backend handles all business logic, data persistence, and API requests. It follows a standard structure with models, views (routes), and a scheduler engine separated into different modules.
-   **Frontend:** The frontend is not a single-page application (SPA) but consists of distinct HTML pages rendered by Flask's templating engine. These pages are then made interactive and dynamic by a single comprehensive JavaScript file (`main.js`). The frontend communicates with the backend via RESTful API calls.
-   **Database:** The application uses an **SQLite** database for data storage, managed via the **Flask-SQLAlchemy** ORM extension. Database schema changes are handled by **Flask-Migrate**.

## 2. Data Models (`models.py`)

The application's data structure is defined by the following SQLAlchemy models:

| Model         | Description                                                                                             | Key Relationships                                                                    |
| :------------ | :------------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------------------- |
| `Teacher`     | Represents a teacher in the school.                                                                     | One-to-Many with `Course`, `Preference`.                                             |
| `Subject`     | Represents a subject offered by the school (e.g., Math, Physics).                                       | One-to-Many with `Course`. Many-to-Many with `Section`.                              |
| `Grade`       | Represents a grade level (e.g., Grade 9).                                                               | One-to-Many with `Section`.                                                          |
| `Section`     | Represents a specific class of students within a grade (e.g., Section A).                               | Many-to-One with `Grade`. One-to-Many with `Course`. Many-to-Many with `Subject`.      |
| `Course`      | The core unit of assignment, linking a Teacher, Subject, and Section for a set number of periods.       | Many-to-One with `Teacher`, `Subject`, `Section`. One-to-Many with `Lesson`.         |
| `Timeslot`    | Represents a specific period at a specific day of the week (e.g., Monday, Period 1).                    | One-to-Many with `Lesson`, `Preference`.                                             |
| `Lesson`      | The final scheduled entity, representing a `Course` placed in a specific `Timeslot`.                      | Many-to-One with `Course`, `Timeslot`.                                               |
| `Preference`  | Represents a teacher's preference for a timeslot (e.g., undesirable).                                   | Many-to-One with `Teacher`, `Timeslot`.                                              |
| `Configuration` | A generic key-value store for application settings (e.g., `work_days`, `periods_per_day`).              | -                                                                                    |

### Many-to-Many Relationship: `section_subjects`

An association table, `section_subjects`, links `sections` and `subjects` to define which subjects are offered by each section. This is crucial for constraining the available choices when creating courses.

## 3. API Endpoints (`routes.py`)

The application exposes a RESTful API for all frontend-backend communication.

| Endpoint                                  | Method | Description                                                                                                   |
| :---------------------------------------- | :----- | :------------------------------------------------------------------------------------------------------------ |
| `/api/data`                               | `GET`  | Fetches all initial data needed by the frontend (teachers, subjects, sections, config, mappings, etc.).        |
| `/api/settings`                           | `POST` | Updates core settings (`work_days`, `periods_per_day`) and triggers a regeneration of all `Timeslot` records. |
| `/api/data/<entity>`                      | `POST` | Generic endpoint to create a new master data record (e.g., `teacher`, `subject`, `grade`).                    |
| `/api/section/<id>/subjects`              | `GET`  | Fetches the list of subject IDs assigned to a specific section.                                               |
| `/api/section/<id>/subjects`              | `POST` | Updates the list of subjects assigned to a specific section.                                                  |
| `/api/teacher/<id>/assignments`           | `GET`  | Fetches a flat list of all courses assigned to a specific teacher.                                            |
| `/api/teacher/<id>/assignments`           | `POST` | Updates the courses and preferences for a specific teacher.                                                   |
| `/api/timetable/generate`                 | `POST` | Triggers the backend scheduler to generate a new timetable based on all current data.                         |
| `/api/timetable/commit`                   | `POST` | Commits a generated schedule to the `lessons` table in the database.                                          |
| `/api/timetable`                          | `GET`  | Fetches the currently committed timetable (`Lesson` records).                                                 |
| `/api/analytics/summary`                  | `GET`  | Fetches all analytical data for the "Summary" tab.                                                            |

## 4. Core Logic

### Scheduler (`generator.py`)

The core scheduling logic resides in the `TimetableGenerator` class.
-   It uses a **constructive heuristic** to build an initial, valid solution.
-   The algorithm first creates a list of all individual lessons that need to be scheduled (e.g., 5 math lessons for Section A).
-   It then shuffles both the lessons and the available timeslots to ensure a random, unbiased placement.
-   For each lesson, it iterates through the shuffled timeslots and places the lesson in the first slot that does not violate any **hard constraints**.
-   **Hard constraints** include: teacher clashes, section clashes, and teacher "undesirable" preferences.

### Analytics Engine (`analytics.py`)

The `analytics.py` module provides functions to calculate summary statistics.
-   `get_teacher_workload`: Calculates total weekly periods for each teacher.
-   `get_subject_demand_and_supply`: Calculates total periods required per subject and the number of unique teachers available for each.
-   `analyze_teacher_sufficiency`: Compares demand vs. supply to determine if there is a "Shortage", "Adequate" supply, or "Surplus" of teachers for each subject.
-   `generate_summary_data`: A top-level function that calls all other functions and aggregates the data for the API endpoint.
