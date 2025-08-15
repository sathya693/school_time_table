import os
from app import create_app, db
from app.models import * # Import all models
from flask_migrate import Migrate, upgrade
from seed import seed_data

def setup_database(app):
    """
    Checks if the database needs to be initialized. If the db file doesn't exist,
    it runs the migrations and seeds the database with initial data.
    """
    with app.app_context():
        # The path to the database file is taken from the app's configuration
        db_path_str = app.config.get('SQLALCHEMY_DATABASE_URI').replace('sqlite:///', '')
        db_path = os.path.join(os.path.dirname(app.root_path), db_path_str)

        if not os.path.exists(db_path):
            print("--- First time setup: Initializing database. ---")
            # Create the database tables
            upgrade()
            # Populate with seed data
            seed_data()
            print("--- Database setup complete. ---")
        else:
            print("Database already exists. Skipping setup.")


# --- Application Factory ---
config_name = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(config_name)
migrate = Migrate(app, db)

# --- Shell Context for 'flask shell' ---
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Teacher=Teacher, Subject=Subject, Classroom=Classroom,
                Grade=Grade, Section=Section, Timeslot=Timeslot,
                Constraint=Constraint, Course=Course, Lesson=Lesson, Configuration=Configuration)


# --- Main Execution ---
if __name__ == '__main__':
    # Ensure the database is set up before running the app
    setup_database(app)

    # The app.run() command is suitable for development.
    # For production, a proper WSGI server like Gunicorn or uWSGI should be used.
    app.run(debug=True, use_reloader=False) # Disabling reloader to prevent setup from running twice
