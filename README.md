# School Timetable Generator

This is a full-stack web application designed to help schools automatically generate and manually edit their class schedules. It features a hybrid algorithmic approach for schedule generation to handle complex constraints, and provides an intuitive web interface for management.

The application is built with a Python/Flask backend, a SQLite database for offline-first data storage, and a vanilla JavaScript frontend.

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
