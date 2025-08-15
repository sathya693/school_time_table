import os
from app import create_app, db
from app.models import Teacher, Subject, Classroom, Grade, Section, Timeslot, Constraint, Course, Lesson
from flask_migrate import Migrate

# Get the configuration name from the environment or use default
config_name = os.getenv('FLASK_CONFIG') or 'default'

# Create the application instance
app = create_app(config_name)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """
    Makes additional variables available in the Flask shell context.
    This is useful for testing and debugging.
    """
    return dict(
        db=db,
        Teacher=Teacher,
        Subject=Subject,
        Classroom=Classroom,
        Grade=Grade,
        Section=Section,
        Timeslot=Timeslot,
        Constraint=Constraint,
        Course=Course,
        Lesson=Lesson
    )

if __name__ == '__main__':
    # The app.run() command is suitable for development.
    # For production, a proper WSGI server like Gunicorn or uWSGI should be used.
    app.run(debug=True)
