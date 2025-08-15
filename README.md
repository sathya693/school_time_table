# School Timetable Generator

This is a full-stack web application designed to help schools automatically generate and manually edit their class schedules. It features a hybrid algorithmic approach for schedule generation to handle complex constraints, and provides an intuitive web interface for management.

The application is built with a Python/Flask backend, a SQLite database for offline-first data storage, and a vanilla JavaScript frontend.

## Core Features

*   **Automated Timetable Generation:** Uses a sophisticated algorithm to automatically generate a complete, conflict-free timetable based on your school's unique data.
*   **Comprehensive Setup Wizard:** A step-by-step wizard allows you to input all necessary school data.
*   **Interactive Dashboard:** A central dashboard displays the generated timetable in a clear grid format with dynamic filtering.
*   **Manual Drag-and-Drop Editing:** An "Edit Mode" allows you to manually fine-tune the schedule.
*   **On-Demand Conflict Validation:** At any time, you can validate the entire schedule for conflicts.

## Getting Started

The application includes a fully automated setup process to make getting started as simple as possible.

### Step 1: Initial Setup (Run this only once)

First, run the setup script for your operating system. This will create a virtual environment, install all required dependencies, and prepare the application.

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

### Step 2: Activate the Environment

Before running the app, you must activate the virtual environment created by the setup script.

-   **On macOS or Linux:**
    ```bash
    source venv/bin/activate
    ```

-   **On Windows:**
    ```bat
    venv\Scripts\activate.bat
    ```

### Step 3: Run the Application

Now, you can run the application. The first time you run this command, it will **automatically create and seed the database for you.**

```bash
# Set the required SECRET_KEY
# (On Linux/macOS)
export SECRET_KEY='a-very-secret-and-strong-key-that-you-generate'
# (On Windows)
# set SECRET_KEY='a-very-secret-and-strong-key-that-you-generate'

# Run the app
python school_timetable_app/run.py
```

The application will now be running at **http://127.0.0.1:5000**.

For all subsequent runs, you only need to repeat **Step 2** and **Step 3**.

## How to Use the Application

For a detailed guide on how to use the web interface to add data, generate timetables, and use the editor, please see the **[USER_MANUAL.md](USER_MANUAL.md)**.
