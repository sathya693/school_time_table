import sys
import subprocess
import os
import pkg_resources

def check_and_install_dependencies():
    """
    Checks if the required packages are installed and installs them if not.
    """
    print("--- Checking for required packages... ---")
    try:
        requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
        with open(requirements_path, 'r') as f:
            # We need to parse the requirement names from lines like 'Flask>=2.0'
            required = [line.strip().split('==')[0].split('>=')[0].split('<=')[0] for line in f if line.strip() and not line.startswith('#')]

        pkg_resources.require(required)
        print("All packages are already installed.")
    except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict) as e:
        print(f"Required package not found or version mismatch: {e}. Installing...")
        try:
            # Use the same Python executable that is running this script to run pip
            python_executable = sys.executable
            subprocess.check_call([python_executable, '-m', 'pip', 'install', '-r', requirements_path])
            print("--- Packages installed successfully. ---")
        except subprocess.CalledProcessError as err:
            print(f"ERROR: Failed to install packages. Please run 'pip install -r requirements.txt' manually. Error: {err}")
            sys.exit(1)

# Run dependency check first
check_and_install_dependencies()

# Now, import the application modules
from app import create_app, db
from app.models import *
from flask_migrate import Migrate, upgrade
from seed import seed_data

def setup_database(app):
    """
    Initializes and seeds the database if it doesn't exist.
    """
    with app.app_context():
        db_path_str = app.config.get('SQLALCHEMY_DATABASE_URI').replace('sqlite:///', '')
        db_path = os.path.join(os.path.dirname(app.root_path), db_path_str)
        if not os.path.exists(db_path):
            print("--- First time setup: Initializing database. ---")
            upgrade()
            seed_data()
            print("--- Database setup complete. ---")
        else:
            print("Database already exists. Skipping setup.")

# --- Application Factory & Main Execution ---
if __name__ == '__main__':
    config_name = os.getenv('FLASK_CONFIG') or 'default'
    app = create_app(config_name)
    migrate = Migrate(app, db)

    setup_database(app)

    print("--- Starting Flask Server ---")
    app.run(debug=True, use_reloader=False)
