# School Timetable Generator

This is a full-stack web application designed to help schools automatically generate and manually edit their class schedules. It features a hybrid algorithmic approach for schedule generation to handle complex constraints, and provides an intuitive web interface for management.

For a guide on how to use the application, see [USER_MANUAL.md](USER_MANUAL.md).
For a technical breakdown of the architecture, see [TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md).
For a high-level summary of the workflow, see [SUMMARY.md](SUMMARY.md).

## Core Features

*   **Dynamic School Configuration:** Configure the number of working days and periods per day for your school. The application's timeslots will dynamically adjust.
*   **Granular Curriculum Mapping:** Define which subjects are taught in each specific section (e.g., Grade 9A takes Physics, but Grade 6A takes General Science).
*   **Flexible Teacher Assignments:** Assign teachers to the specific courses they teach, with per-course control over the number of periods per week.
*   **Constraint-Based Scheduling:** The automated generator respects hard constraints, such as teacher availability and undesirable timeslots.
*   **Analytical Summary:** A dedicated summary page provides insights into teacher workload and subject staffing levels, helping to identify potential resource shortages or surpluses before finalizing the schedule.
*   **Interactive Dashboard:** A central dashboard displays the generated timetable with dynamic filtering by teacher or section.

## Technology Stack

*   **Backend:** Python 3
    *   **Framework:** Flask
    *   **ORM:** Flask-SQLAlchemy
    *   **Database Migrations:** Flask-Migrate
*   **Database:** SQLite
*   **Frontend:** Vanilla JavaScript (ES6), HTML5, CSS3
*   **Testing:** Pytest

## Getting Started: The One-Command Setup

This application is designed to be as simple as possible to run. Assuming you have Python 3.9+ and pip installed, you only need to run one command.

### The Only Step: Run the Application

Navigate to the project's root directory in your terminal and run the following command:

```bash
python school_timetable_app/run.py
```

The first time you run this command, the script will automatically:
1.  Check for required Python packages (like Flask) and install them if they are missing.
2.  Create the SQLite database file (`app-dev.db`).
3.  Set up the database schema by applying all migrations.
4.  Populate the database with a full set of sample data so you can start using the application immediately.

On all subsequent runs, the script will detect that the setup is complete and will simply start the web server.

The application will be running at **http://127.0.0.1:5000**.

### (Optional) Using a Virtual Environment

While not required to run the application, it is highly recommended to use a Python virtual environment to keep your system's global packages clean.

1.  **Create the environment (once):** `python -m venv venv`
2.  **Activate it:**
    -   On macOS/Linux: `source venv/bin/activate`
    -   On Windows: `venv\Scripts\activate.bat`
3.  **Run the application:** `python school_timetable_app/run.py`
