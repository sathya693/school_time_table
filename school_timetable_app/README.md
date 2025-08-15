# School Timetable Generator

This is a full-stack web application designed to help schools automatically generate and manually edit their class schedules. It features a hybrid algorithmic approach for schedule generation to handle complex constraints, and provides an intuitive web interface for management.

The application is built with a Python/Flask backend, a SQLite database for offline-first data storage, and a vanilla JavaScript frontend.

## Prerequisites

- Python 3.9+
- `pip` for package installation

## How to Run

Follow these steps to set up and run the application on your local machine.

### 1. Setup the Environment

First, clone the repository and navigate into the project directory.

It is highly recommended to use a Python virtual environment to manage dependencies.

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
# venv\\Scripts\\activate
# On macOS/Linux:
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 2. Initialize the Database

The application uses Flask-Migrate to manage the database schema. To create the database and apply the initial schema, run the following commands.

*Note: You may need to set the `PYTHONPATH` and `FLASK_APP` environment variables for the `flask` command to work correctly.*

```bash
# For macOS/Linux:
export FLASK_APP=run.py
export PYTHONPATH=.

# For Windows:
# set FLASK_APP=run.py
# set PYTHONPATH=.

# Initialize the database migrations (only needs to be run once)
# flask db init

# Create the initial migration script (only needs to be run once)
# flask db migrate -m "Initial database schema"

# Apply the migrations to create the database and tables
flask db upgrade
```

After running these commands, you should see a file named `app-dev.db` in the root `school_timetable_app` directory.

### 3. Seed the Database with Sample Data

To populate the database with a realistic set of sample data for testing and demonstration, run the seed script:

```bash
python seed.py
```

This will populate the database with teachers, subjects, classrooms, grades, and sections.

### 4. Run the Application

Once the database is set up and seeded, you can start the Flask development server:

```bash
python run.py
```

The application will be available at `http://127.0.0.1:5000` in your web browser.

You can navigate to:
- **`/setup`**: To view the multi-step data setup wizard.
- **`/dashboard`**: To view the main timetabling dashboard.
