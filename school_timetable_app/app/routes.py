from flask import Blueprint, render_template, request, jsonify
from . import db
from .models import Teacher, Subject, Grade, Section, Course, Timeslot, Configuration, Lesson, Preference
from sqlalchemy.exc import IntegrityError
import logging

logging.basicConfig(level=logging.INFO)

main = Blueprint('main', __name__)

def _regenerate_timeslots(work_days_str, periods_per_day_str):
    """
    Wipes and regenerates timeslots based on new configuration.
    This is a destructive operation that also clears lessons and preferences.
    """
    try:
        logging.info(f"Regenerating timeslots with work_days='{work_days_str}' and periods_per_day='{periods_per_day_str}'")
        # This should be a single transaction
        with db.session.begin_nested():
            # 1. Clear dependent data
            Lesson.query.delete()
            Preference.query.delete()

            # 2. Clear all existing timeslots
            Timeslot.query.delete()

            # 3. Create new timeslots
            days = work_days_str.split(',')
            periods_count = int(periods_per_day_str)

            timeslots_to_create = []
            for day in days:
                for i in range(periods_count):
                    period_num = i + 1
                    # Dummy times for dynamic period counts
                    start_time = f"{8+i}:00"
                    end_time = f"{8+i}:45"
                    timeslots_to_create.append(
                        Timeslot(day_of_week=day, period_number=period_num, start_time=start_time, end_time=end_time)
                    )
            db.session.add_all(timeslots_to_create)

        db.session.commit()
        logging.info("Successfully regenerated timeslots.")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to regenerate timeslots: {e}", exc_info=True)
        return False

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

    # Enhance teacher serialization to include workload
    teachers_q = Teacher.query.all()
    teachers = []
    for t in teachers_q:
        workload = sum(c.periods_per_week for c in t.courses)
        teachers.append({
            "id": t.id,
            "name": t.name,
            "workload": workload
        })

    subjects = [serialize(s) for s in Subject.query.all()]
    grades = [serialize(g) for g in Grade.query.all()]
    sections = [serialize(s) for s in Section.query.all()]
    courses = [serialize(c) for c in Course.query.all()]
    timeslots = [serialize(t) for t in Timeslot.query.all()]
    config = {c.key: c.value for c in Configuration.query.all()}


    # Add grade name to sections for easier use in frontend
    grade_map = {g['id']: g['name'] for g in grades}
    for section in sections:
        section['grade_name'] = grade_map.get(section['grade_id'])

    # Fetch section-subject mappings
    sections_q = Section.query.all()
    section_subject_map = {s.id: [subj.id for subj in s.subjects] for s in sections_q}

    response = {
        "teachers": teachers,
        "subjects": subjects,
        "grades": grades,
        "sections": sections,
        "courses": courses,
        "timeslots": timeslots,
        "config": config,
        "section_subject_map": section_subject_map,
    }
    return jsonify(response), 200

@main.route('/api/settings', methods=['POST'])
def update_settings():
    """
    Endpoint to update multiple settings at once and regenerate timeslots.
    """
    data = request.get_json()
    logging.info(f"Received POST for settings with data: {data}")
    if not data or 'work_days' not in data or 'periods_per_day' not in data:
        return jsonify({"error": "Invalid payload. 'work_days' and 'periods_per_day' are required."}), 400

    work_days = data['work_days']
    periods_per_day = data['periods_per_day']

    try:
        # Update configuration table
        settings_map = {'work_days': work_days, 'periods_per_day': periods_per_day}
        for key, value in settings_map.items():
            setting = Configuration.query.filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                setting = Configuration(key=key, value=value)
                db.session.add(setting)

        # Now, regenerate the timeslots which is a destructive operation
        if not _regenerate_timeslots(work_days, periods_per_day):
            # The helper function already logged the error
            return jsonify({"error": "Failed to regenerate timeslots."}), 500

        db.session.commit()
        return jsonify({"message": "Settings updated and timeslots regenerated successfully."}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating settings: {e}", exc_info=True)
        return jsonify({"error": "A server error occurred while updating settings."}), 500

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

@main.route('/api/data/grade', methods=['POST'])
def create_grade():
    return handle_post(Grade, ['name'])

@main.route('/api/data/section', methods=['POST'])
def create_section():
    return handle_post(Section, ['name', 'grade_id'])

@main.route('/api/data/course', methods=['POST'])
def create_course():
    return handle_post(Course, ['subject_id', 'teacher_id', 'section_id', 'periods_per_week'])

# --- API Routes for Section-Subject Assignments ---

@main.route('/api/section/<int:section_id>/subjects', methods=['GET'])
def get_section_subjects(section_id):
    """Fetches the list of subjects assigned to a specific section."""
    section = Section.query.get_or_404(section_id)
    subject_ids = [subject.id for subject in section.subjects]
    return jsonify(subject_ids), 200

@main.route('/api/section/<int:section_id>/subjects', methods=['POST'])
def update_section_subjects(section_id):
    """Updates the subjects assigned to a specific section."""
    section = Section.query.get_or_404(section_id)
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Invalid payload. Expected a list of subject IDs."}), 400

    try:
        # Get all subject objects from the provided IDs
        subjects = Subject.query.filter(Subject.id.in_(data)).all()
        # Ensure all provided IDs were valid subjects
        if len(subjects) != len(data):
            return jsonify({"error": "One or more invalid subject IDs provided."}), 400

        section.subjects = subjects
        db.session.commit()
        return jsonify({"message": f"Subjects for section {section_id} updated successfully."}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating subjects for section {section_id}: {e}", exc_info=True)
        return jsonify({"error": "A server error occurred while updating subjects."}), 500


@main.route('/api/teacher/<int:teacher_id>/assignments', methods=['GET'])
def get_teacher_assignments(teacher_id):
    """
    Fetches all existing course assignments and preferences for a given teacher.
    """
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"error": "Teacher not found."}), 404

    # Fetch courses directly
    courses_q = Course.query.filter_by(teacher_id=teacher_id).all()
    assignments = [
        {
            "id": c.id,
            "subject_id": c.subject_id,
            "section_id": c.section_id,
            "periods_per_week": c.periods_per_week
        } for c in courses_q
    ]

    # Fetch preferences
    preferences_q = Preference.query.filter_by(teacher_id=teacher_id).all()
    preferences = [
        {
            'id': p.id,
            'timeslot_id': p.timeslot_id,
            'preference_type': p.preference_type,
            'subject_id': p.subject_id
        } for p in preferences_q
    ]

    response = {
        "assignments": assignments,
        "preferences": preferences
    }
    return jsonify(response), 200

@main.route('/api/teacher/<int:teacher_id>/assignments', methods=['POST'])
def update_teacher_assignments(teacher_id):
    """
    Handles bulk creation/update of a teacher's courses and preferences.
    This is a transactional operation.
    """
    data = request.get_json()
    if not data or 'assignments' not in data or 'preferences' not in data:
        return jsonify({"error": "Invalid payload. 'assignments' and 'preferences' are required."}), 400

    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"error": "Teacher not found."}), 404

    try:
        # Start a transaction
        with db.session.begin_nested():
            # Clear existing courses and preferences for this teacher
            Course.query.filter_by(teacher_id=teacher_id).delete()
            Preference.query.filter_by(teacher_id=teacher_id).delete()

            # Create new courses from the flat list
            new_courses = []
            for assignment in data['assignments']:
                # Basic validation for required keys in each assignment
                if not all(k in assignment for k in ['subject_id', 'section_id', 'periods_per_week']):
                    continue # Or raise an error

                new_course = Course(
                    teacher_id=teacher_id,
                    subject_id=assignment['subject_id'],
                    section_id=assignment['section_id'],
                    periods_per_week=assignment['periods_per_week']
                )
                new_courses.append(new_course)
            db.session.add_all(new_courses)

            # Create new preferences
            new_preferences = []
            for pref in data['preferences']:
                new_preference = Preference(
                    teacher_id=teacher_id,
                    subject_id=pref.get('subject_id'),
                    timeslot_id=pref.get('timeslot_id'),
                    preference_type=pref.get('preference_type')
                )
                new_preferences.append(new_preference)
            db.session.add_all(new_preferences)

        # Commit the transaction
        db.session.commit()

        return jsonify({"message": f"Assignments for teacher {teacher_id} updated successfully."}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating assignments for teacher {teacher_id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to update assignments due to a server error."}), 500

from .scheduler.generator import TimetableGenerator
from .scheduler.rescheduler import TimetableRescheduler
from .analytics import generate_summary_data

# --- API Routes for Analytics ---

@main.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Endpoint to fetch all analytical data for the summary page."""
    try:
        summary_data = generate_summary_data()
        return jsonify(summary_data), 200
    except Exception as e:
        logging.error(f"Error generating analytics summary: {e}", exc_info=True)
        return jsonify({"error": "Failed to generate analytics summary."}), 500

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
                schedule_map[ts_id] = {'teachers': set(), 'sections': set()}

            teacher_id = lesson.course.teacher_id
            section_id = lesson.course.section_id

            if teacher_id in schedule_map[ts_id]['teachers']:
                conflicts.append(f"Teacher Conflict: Teacher ID {teacher_id} is double-booked at timeslot {ts_id}.")
            if section_id in schedule_map[ts_id]['sections']:
                conflicts.append(f"Section Conflict: Section ID {section_id} is double-booked at timeslot {ts_id}.")

            schedule_map[ts_id]['teachers'].add(teacher_id)
            schedule_map[ts_id]['sections'].add(section_id)

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
        preferences_q = Preference.query.all()

        courses = [{'id': c.id, 'teacher_id': c.teacher_id, 'section_id': c.section_id, 'periods_per_week': c.periods_per_week} for c in courses_q]
        timeslots = [{'id': t.id, 'day': t.day_of_week, 'period': t.period_number} for t in timeslots_q]
        preferences = [{'teacher_id': p.teacher_id, 'timeslot_id': p.timeslot_id, 'preference_type': p.preference_type, 'subject_id': p.subject_id} for p in preferences_q]

        config_q = Configuration.query.all()
        config = {c.key: c.value for c in config_q}

        # Generate a temporary schedule to work with
        temp_generator = TimetableGenerator(courses, timeslots, config, preferences)
        schedule = temp_generator.generate()
        if schedule is None:
            return jsonify({"error": "Could not generate a base schedule to find solutions."}), 500

        # Use the rescheduler to find solutions
        rescheduler = TimetableRescheduler(schedule, courses, timeslots, config, preferences)
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
                # The generator's output contains extra keys.
                # We only need the ones that map to the Lesson model's columns.
                new_lesson = Lesson(
                    course_id=lesson_data['course_id'],
                    timeslot_id=lesson_data['timeslot_id']
                )
                new_lessons.append(new_lesson)
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
        preferences_q = Preference.query.all()

        courses = [{'id': c.id, 'teacher_id': c.teacher_id, 'section_id': c.section_id, 'periods_per_week': c.periods_per_week} for c in courses_q]
        timeslots = [{'id': t.id, 'day': t.day_of_week, 'period': t.period_number} for t in timeslots_q]
        preferences = [{'teacher_id': p.teacher_id, 'timeslot_id': p.timeslot_id, 'preference_type': p.preference_type, 'subject_id': p.subject_id} for p in preferences_q]

        config_q = Configuration.query.all()
        config = {c.key: c.value for c in config_q}

        generator = TimetableGenerator(courses, timeslots, config, preferences)
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
