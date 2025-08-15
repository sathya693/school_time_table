from flask import Blueprint, render_template, request, jsonify
from . import db
from .models import Teacher, Subject, Classroom, Grade, Section, Course, Constraint, Timeslot

main = Blueprint('main', __name__)

# Page-rendering routes
@main.route('/')
def index():
    return render_template('dashboard.html')

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main.route('/setup')
def setup():
    return render_template('setup.html')

# --- API Routes for Data Management ---

@main.route('/api/data', methods=['GET'])
def get_all_data():
    """Endpoint to fetch all initial data for the setup wizard and dashboard rendering."""
    def serialize(model_instance):
        """Simple serializer for our models."""
        if not model_instance: return None
        return {c.name: getattr(model_instance, c.name) for c in model_instance.__table__.columns}

    teachers = [serialize(t) for t in Teacher.query.all()]
    subjects = [serialize(s) for s in Subject.query.all()]
    classrooms = [serialize(c) for c in Classroom.query.all()]
    grades = [serialize(g) for g in Grade.query.all()]
    sections = [serialize(s) for s in Section.query.all()]
    courses = [serialize(c) for c in Course.query.all()]
    timeslots = [serialize(t) for t in Timeslot.query.all()]

    # Add grade name to sections for easier use in frontend
    grade_map = {g['id']: g['name'] for g in grades}
    for section in sections:
        section['grade_name'] = grade_map.get(section['grade_id'])

    response = {
        "teachers": teachers,
        "subjects": subjects,
        "classrooms": classrooms,
        "grades": grades,
        "sections": sections,
        "courses": courses,
        "timeslots": timeslots,
    }
    return jsonify(response), 200

def handle_post(model, required_fields):
    """Generic handler for creating a new model instance."""
    data = request.get_json()
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": f"Invalid payload. Required fields: {required_fields}"}), 400

    try:
        instance = model(**data)
        db.session.add(instance)
        db.session.commit()
        return jsonify({"message": f"{model.__name__} created successfully", "id": instance.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create item.", "details": str(e)}), 500

@main.route('/api/data/teacher', methods=['POST'])
def create_teacher():
    return handle_post(Teacher, ['name'])

@main.route('/api/data/subject', methods=['POST'])
def create_subject():
    return handle_post(Subject, ['name'])

@main.route('/api/data/classroom', methods=['POST'])
def create_classroom():
    return handle_post(Classroom, ['name'])

@main.route('/api/data/grade', methods=['POST'])
def create_grade():
    return handle_post(Grade, ['name'])

@main.route('/api/data/section', methods=['POST'])
def create_section():
    return handle_post(Section, ['name', 'grade_id'])

@main.route('/api/data/course', methods=['POST'])
def create_course():
    return handle_post(Course, ['subject_id', 'teacher_id', 'section_id', 'periods_per_week'])

@main.route('/api/data/constraint', methods=['POST'])
def create_constraint():
    return handle_post(Constraint, ['teacher_id', 'timeslot_id'])

from .scheduler.generator import TimetableGenerator
from .scheduler.rescheduler import TimetableRescheduler

# --- API Routes for Timetable Generation & Rescheduling ---

@main.route('/api/lesson/<int:course_id>/reschedule', methods=['GET'])
def reschedule_lesson(course_id):
    """
    Finds alternative slots for a given lesson (identified by its course_id).
    NOTE: This is a simplified implementation. It regenerates a temporary
    schedule to find conflicts, rather than operating on a saved state.
    """
    try:
        # Fetch all data needed for generation
        courses_q = Course.query.all()
        timeslots_q = Timeslot.query.all()
        classrooms_q = Classroom.query.all()
        constraints_q = Constraint.query.all()

        courses = [{'id': c.id, 'teacher_id': c.teacher_id, 'section_id': c.section_id, 'periods_per_week': c.periods_per_week} for c in courses_q]
        timeslots = [{'id': t.id, 'day': t.day_of_week, 'period': t.period_number} for t in timeslots_q]
        classrooms = [{'id': c.id, 'name': c.name} for c in classrooms_q]
        constraints = [{'teacher_id': c.teacher_id, 'timeslot_id': c.timeslot_id} for c in constraints_q]

        # Generate a temporary schedule to work with
        temp_generator = TimetableGenerator(courses, timeslots, classrooms, constraints)
        schedule = temp_generator.generate()
        if schedule is None:
            return jsonify({"error": "Could not generate a base schedule to find solutions."}), 500

        # Use the rescheduler to find solutions
        rescheduler = TimetableRescheduler(schedule, courses, timeslots, constraints)
        solutions = rescheduler.find_solutions_for_conflict(course_id)

        return jsonify(solutions), 200

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred during rescheduling."}), 500


@main.route('/api/timetable/generate', methods=['POST'])
def generate_timetable():
    """
    Triggers the timetable generation process and returns the result.
    """
    try:
        # 1. Fetch all necessary data from the database
        courses_q = Course.query.all()
        timeslots_q = Timeslot.query.all()
        classrooms_q = Classroom.query.all()
        constraints_q = Constraint.query.all()

        # 2. Format data for the generator
        courses = [{'id': c.id, 'teacher_id': c.teacher_id, 'section_id': c.section_id, 'periods_per_week': c.periods_per_week} for c in courses_q]
        timeslots = [{'id': t.id, 'day': t.day_of_week, 'period': t.period_number} for t in timeslots_q]
        classrooms = [{'id': c.id, 'name': c.name} for c in classrooms_q]
        constraints = [{'teacher_id': c.teacher_id, 'timeslot_id': c.timeslot_id} for c in constraints_q]

        # 3. Instantiate and run the generator
        generator = TimetableGenerator(courses, timeslots, classrooms, constraints)
        schedule = generator.generate()

        if schedule is None:
            return jsonify({"error": "Failed to generate timetable. The problem might be unsolvable with the given constraints."}), 500

        # 4. Return the generated schedule
        return jsonify(schedule), 200

    except Exception as e:
        # Log the exception e
        return jsonify({"error": "An unexpected error occurred during timetable generation."}), 500
