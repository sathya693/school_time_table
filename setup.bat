@echo off
REM This script automates the setup process for the School Timetable application on Windows.

echo "--- Starting School Timetable Application Setup ---"

REM 1. Create a Python virtual environment
echo "[1/5] Creating Python virtual environment named 'venv'..."
python -m venv venv
IF %ERRORLEVEL% NEQ 0 (
    echo "Failed to create virtual environment. Please ensure Python is installed and in your PATH."
    exit /b %ERRORLEVEL%
)

REM 2. Install dependencies using the venv's pip
echo "[2/5] Installing required packages from requirements.txt..."
call .\venv\Scripts\pip.exe install -r school_timetable_app\requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo "Failed to install dependencies."
    exit /b %ERRORLEVEL%
)

REM 3. Set environment variables for the flask command
echo "[3/5] Setting up environment and initializing the database..."
set FLASK_APP=school_timetable_app\run.py
set PYTHONPATH=.
call .\venv\Scripts\flask.exe db upgrade
IF %ERRORLEVEL% NEQ 0 (
    echo "Failed to initialize the database."
    exit /b %ERRORLEVEL%
)

REM 4. Seed the database with sample data
echo "[4/5] Seeding the database with sample data..."
call .\venv\Scripts\python.exe school_timetable_app\seed.py
IF %ERRORLEVEL% NEQ 0 (
    echo "Failed to seed the database."
    exit /b %ERRORLEVEL%
)

REM 5. Final instructions
echo "[5/5] Setup complete!"
echo.
echo "--- To run the application: ---"
echo "1. Activate the virtual environment: call venv\Scripts\activate.bat"
echo "2. Run the application: python school_timetable_app\run.py"
echo "3. Open your web browser to http://127.0.0.1:5000"
echo.
pause
