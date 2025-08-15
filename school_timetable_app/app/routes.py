from flask import Blueprint, render_template, request, jsonify
from . import db
from .models import Teacher, Subject, Classroom, Grade, Section, Course, Constraint, Timeslot, Configuration
from sqlalchemy.exc import IntegrityError
import logging

logging.basicConfig(level=logging.INFO)

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
    config = {c.key: c.value for c in Configuration.query.all()}


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
        "config": config,
    }
    return jsonify(response), 200

@main.route('/api/data/setting', methods=['POST'])
def update_setting():
    """Endpoint to update a configuration setting (upsert)."""
    data = request.get_json()
    logging.info(f"Received POST for setting with data: {data}")
    if not data or 'key' not in data or 'value' not in data:
        return jsonify({"error": "Invalid payload. 'key' and 'value' are required."}), 400

    key = data['key']
    value = data['value']

    try:
        setting = Configuration.query.filter_by(key=key).first()
        if setting:
            logging.info(f"Updating setting '{key}' from '{setting.value}' to '{value}'")
            setting.value = value
        else:
            logging.info(f"Creating new setting '{key}' with value '{value}'")
            setting = Configuration(key=key, value=value)
            db.session.add(setting)

        db.session.commit()
        return jsonify({"message": "Setting updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating setting '{key}': {e}", exc_info=True)
        return jsonify({"error": "Failed to update setting."}), 500

def handle_post(model, required_fields):
    """Generic handler for creating a new model instance."""
    data = request.get_json()
    logging.info(f"Received POST request for {model.__name__} with data: {data}")
    if not data or not all(field in data for field in required_fields):
        logging.warning(f"Invalid payload for {model.__name__}: {data}")
        return jsonify({"error": f"Invalid payload. Required fields: {required_fields}"}), 400

    try:
        instance = model(**data)
        db.session.add(instance)
        db.session.commit()
        logging.info(f"Successfully created {model.__name__} with id {instance.id}")
        return jsonify({"message": f"{model.__name__} created successfully", "id": instance.id}), 201
    except IntegrityError as e:
        db.session.rollback()
        logging.warning(f"IntegrityError on {model.__name__} creation: {e.orig}")
        return jsonify({"error": "Item already exists.", "details": "An item with these details (e.g., name) already exists."}), 409
    except Exception as e:
        db.session.rollback()
        logging.error(f"Generic exception on {model.__name__} creation: {e}", exc_info=True)
        return jsonify({"error": "Failed to create item due to a server error.", "details": str(e)}), 500

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

# --- API Routes for Timetable Generation & Editing ---

@main.route('/api/timetable/validate', methods=['GET'])
def validate_timetable():
    """Validates the current timetable for teacher, section, and classroom conflicts."""
    try:
        lessons = Lesson.query.all()
        conflicts = []
        schedule_map = {}

        for lesson in lessons:
            ts_id = lesson.timeslot_id
            if ts_id not in schedule_map:
                schedule_map[ts_id] = {'teachers': set(), 'sections': set(), 'classrooms': set()}

            teacher_id = lesson.course.teacher_id
            section_id = lesson.course.section_id
            classroom_id = lesson.classroom_id

            if teacher_id in schedule_map[ts_id]['teachers']:
                conflicts.append(f"Teacher Conflict: Teacher ID {teacher_id} is double-booked at timeslot {ts_id}.")
            if section_id in schedule_map[ts_id]['sections']:
                conflicts.append(f"Section Conflict: Section ID {section_id} is double-booked at timeslot {ts_id}.")
            if classroom_id in schedule_map[ts_id]['classrooms']:
                conflicts.append(f"Classroom Conflict: Classroom ID {classroom_id} is double-booked at timeslot {ts_id}.")

            schedule_map[ts_id]['teachers'].add(teacher_id)
            schedule_map[ts_id]['sections'].add(section_id)
            schedule_map[ts_id]['classrooms'].add(classroom_id)

        logging.info(f"Validation complete. Found {len(conflicts)} conflicts.")
        return jsonify({"conflicts": conflicts}), 200
    except Exception as e:
        logging.error(f"Error during validation: {e}", exc_info=True)
        return jsonify({"error": "Failed to validate timetable."}), 500


@main.route('/api/lesson/update', methods=['POST'])
def update_lesson():
    """
    Updates a lesson's timeslot, performing validation first.
    """
    data = request.get_json()
    if not data or 'lesson_id' not in data or 'new_timeslot_id' not in data:
        return jsonify({"error": "Invalid payload. 'lesson_id' and 'new_timeslot_id' are required."}), 400

    lesson_id = data['lesson_id']
    new_timeslot_id = data['new_timeslot_id']

    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found."}), 404

    # Basic validation: Check for teacher/section clashes at the new timeslot
    teacher_clash = Lesson.query.filter(
        Lesson.course.has(teacher_id=lesson.course.teacher_id),
        Lesson.timeslot_id == new_timeslot_id
    ).first()
    section_clash = Lesson.query.filter(
        Lesson.course.has(section_id=lesson.course.section_id),
        Lesson.timeslot_id == new_timeslot_id
    ).first()

    if teacher_clash:
        return jsonify({"error": "Validation failed: Teacher is already scheduled at this time."}), 409
    if section_clash:
        return jsonify({"error": "Validation failed: Section is already scheduled at this time."}), 409

    # All good, update the lesson
    try:
        lesson.timeslot_id = new_timeslot_id
        db.session.commit()
        logging.info(f"Successfully moved lesson {lesson_id} to timeslot {new_timeslot_id}.")
        return jsonify({"message": "Lesson updated successfully."}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating lesson {lesson_id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to update lesson."}), 500


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


@main.route('/api/timetable', methods=['GET'])
def get_timetable():
    """
    Fetches the currently committed schedule from the database.
    """
    try:
        lessons_q = Lesson.query.all()
        schedule = [
            {
                'lesson_id': l.id,
                'course_id': l.course_id,
                'timeslot_id': l.timeslot_id,
                'classroom_id': l.classroom_id,
            } for l in lessons_q
        ]
        return jsonify(schedule), 200
    except Exception as e:
        logging.error(f"Error fetching timetable: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch timetable."}), 500

@main.route('/api/timetable/commit', methods=['POST'])
def commit_timetable():
    """Receives a generated schedule and commits it to the database transactionally."""
    schedule = request.get_json()
    if not isinstance(schedule, list):
        return jsonify({"error": "Invalid payload. Expected a list of lessons."}), 400

    try:
        # Using a nested transaction ensures that if any part of this fails,
        # the outer session is not tainted and the whole block is rolled back.
        with db.session.begin_nested():
            Lesson.query.delete()
            new_lessons = []
            for lesson_data in schedule:
                # Ensure all required keys are present
                if not all(k in lesson_data for k in ['course_id', 'timeslot_id', 'classroom_id']):
                    raise ValueError("Invalid lesson data received.")
                new_lessons.append(Lesson(**lesson_data))
            db.session.add_all(new_lessons)
        db.session.commit()
        logging.info(f"Successfully committed {len(new_lessons)} lessons to the database.")
        return jsonify({"message": "Timetable committed successfully."}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error committing timetable: {e}", exc_info=True)
        return jsonify({"error": "Failed to commit timetable to database."}), 500

@main.route('/api/timetable/generate', methods=['POST'])
def generate_timetable():
    """Triggers the timetable generation process and returns the result."""
    try:
        courses_q = Course.query.all()
        timeslots_q = Timeslot.query.all()
        classrooms_q = Classroom.query.all()
        constraints_q = Constraint.query.all()

        courses = [{'id': c.id, 'teacher_id': c.teacher_id, 'section_id': c.section_id, 'periods_per_week': c.periods_per_week} for c in courses_q]
        timeslots = [{'id': t.id, 'day': t.day_of_week, 'period': t.period_number} for t in timeslots_q]
        classrooms = [{'id': c.id, 'name': c.name} for c in classrooms_q]
        constraints = [{'teacher_id': c.teacher_id, 'timeslot_id': c.timeslot_id} for c in constraints_q]

        generator = TimetableGenerator(courses, timeslots, classrooms, constraints)
        schedule = generator.generate()

        if schedule is None:
            logging.warning("Timetable generation failed, returning unsolvable error.")
            return jsonify({
                "error": "Failed to generate timetable.",
                "details": "The problem is likely unsolvable with the given constraints. Please ensure teachers have enough available slots for their assigned courses."
            }), 422 # Unprocessable Entity

        return jsonify(schedule), 200
    except Exception as e:
        logging.error(f"An unexpected error occurred during timetable generation: {e}", exc_info=True)
        return jsonify({"error": "An unexpected server error occurred."}), 500
