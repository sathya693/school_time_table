# School Timetable Generator

This is a full-stack web application designed to help schools automatically generate and manually edit their class schedules. It features a hybrid algorithmic approach for schedule generation to handle complex constraints, and provides an intuitive web interface for management.

## Core Features

*   **Automated Timetable Generation:** Uses a sophisticated algorithm to automatically generate a complete, conflict-free timetable.
*   **Comprehensive Setup Wizard:** A step-by-step wizard allows you to input all school data.
*   **Interactive Dashboard:** A central dashboard displays the timetable with dynamic filtering.
*   **Manual Drag-and-Drop Editing:** An "Edit Mode" allows for manual fine-tuning of the schedule.
*   **On-Demand Conflict Validation:** Validate the entire schedule for conflicts at any time.

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
3.  Set up the database schema.
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

## How to Use the Application

For a detailed guide on how to use the web interface, please see the **[USER_MANUAL.md](USER_MANUAL.md)**.
