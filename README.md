# School Timetable Generator

This is a full-stack web application designed to help schools automatically generate and manually edit their class schedules. It features a hybrid algorithmic approach for schedule generation to handle complex constraints, and provides an intuitive web interface for management.

The application is built with a Python/Flask backend, a SQLite database for offline-first data storage, and a vanilla JavaScript frontend.

## Core Features

*   **Automated Timetable Generation:** Uses a sophisticated algorithm to automatically generate a complete, conflict-free timetable based on your school's unique data.
*   **Comprehensive Setup Wizard:** A step-by-step wizard allows you to input all necessary school data:
    -   School-wide settings (e.g., periods per day)
    -   Teachers
    -   Subjects
    -   Classrooms
    -   Grades and their respective Sections
    -   Courses (linking teachers, subjects, and sections)
    -   Teacher unavailability constraints
*   **Interactive Dashboard:** A central dashboard displays the generated timetable in a clear grid format.
*   **Dynamic View Filtering:** Instantly filter the timetable to view the schedule for a specific teacher, section, or classroom using intuitive dropdown menus.
*   **Manual Drag-and-Drop Editing:** An "Edit Mode" allows you to manually fine-tune the schedule by simply dragging and dropping lessons into new timeslots. The system validates each move to prevent you from creating new conflicts.
*   **On-Demand Conflict Validation:** At any time, you can ask the system to validate the entire schedule. It will provide a clear list of any existing conflicts (e.g., a teacher being double-booked).

## Quickstart: Automated Setup

For the easiest setup, use the automated scripts. They will create a virtual environment, install dependencies, and set up the database for you.

-   **On macOS or Linux:**
    ```bash
    # Make the script executable
    chmod +x setup.sh
    # Run the setup script
    ./setup.sh
    ```

-   **On Windows:**
    ```bat
    # Run the setup batch file
    .\setup.bat
    ```

After the setup is complete, follow the final instructions printed in the terminal to run the application.

## Manual Setup Instructions

If you prefer to set up the application manually, follow these steps. All commands should be run from the project's root directory (the one containing this README).

### 1. Setup the Environment

It is highly recommended to use a Python virtual environment.

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate.bat

# Install the required packages
pip install -r school_timetable_app/requirements.txt
```

### 2. Initialize the Database

The application uses Flask-Migrate to manage the database schema.

```bash
# Set environment variables for Flask
# On macOS/Linux:
export FLASK_APP=school_timetable_app/run.py
export PYTHONPATH=.
# On Windows:
set FLASK_APP=school_timetable_app\run.py
set PYTHONPATH=.

# Apply the migrations to create the database and tables
flask db upgrade
```

### 3. Seed the Database with Sample Data

To populate the database with sample data, run the seed script:

```bash
python school_timetable_app/seed.py
```

### 4. Run the Application

Start the Flask development server:

```bash
python school_timetable_app/run.py
```

The application will be available at `http://127.0.0.1:5000`.

## How to Use the Application

For a detailed guide on how to use the web interface to add data and generate timetables, please see the **[USER_MANUAL.md](USER_MANUAL.md)**.
