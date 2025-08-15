#!/bin/bash

# This script automates the setup process for the School Timetable application.

echo "--- Starting School Timetable Application Setup ---"

# Exit immediately if a command exits with a non-zero status.
set -e

# 1. Create a Python virtual environment
echo "[1/5] Creating Python virtual environment named 'venv'..."
python3 -m venv venv

# 2. Install dependencies using the venv's pip
echo "[2/5] Installing required packages from requirements.txt..."
./venv/bin/pip install -r school_timetable_app/requirements.txt

# 3. Set environment variables for the flask command
export FLASK_APP=school_timetable_app/run.py
export PYTHONPATH=.

# 4. Initialize the database
echo "[3/5] Initializing the database..."
./venv/bin/flask db upgrade

# 5. Seed the database with sample data
echo "[4/5] Seeding the database with sample data..."
./venv/bin/python school_timetable_app/seed.py

# 6. Final instructions
echo "[5/5] Setup complete!"
echo ""
echo "--- To run the application: ---"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python school_timetable_app/run.py"
echo "3. Open your web browser to http://127.0.0.1:5000"
echo ""
