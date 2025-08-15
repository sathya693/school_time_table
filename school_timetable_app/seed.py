from app import create_app, db
from app.models import Teacher, Subject, Grade, Section, Timeslot, Preference, Course, Configuration

def seed_data():
    """Populates the database with a realistic set of sample data."""
    app = create_app('development')
    with app.app_context():
        print("Starting database seed...")

        # Clear existing data in the correct order
        print("Clearing old data...")
        Course.query.delete()
        Preference.query.delete()
        Timeslot.query.delete()
        Section.query.delete()
        Grade.query.delete()
        Subject.query.delete()
        Teacher.query.delete()
        Configuration.query.delete()
        db.session.commit()

        # --- Create Default Configuration ---
        print("Creating default configuration...")
        config_items = [
            Configuration(key='periods_per_day', value='9'),
            Configuration(key='work_days', value='Monday,Tuesday,Wednesday,Thursday,Friday'),
            Configuration(key='lunch_break_period', value='5')
        ]
        db.session.add_all(config_items)
        db.session.commit()

        # --- Create Timeslots ---
        print("Creating timeslots...")
        # Fetch config values to ensure they are available
        periods_per_day_config = Configuration.query.filter_by(key='periods_per_day').first()
        work_days_config = Configuration.query.filter_by(key='work_days').first()

        days = work_days_config.value.split(',')
        periods_count = int(periods_per_day_config.value)
        # Dummy times for dynamic period counts
        periods = [(f"{8+i}:00", f"{8+i}:45") for i in range(periods_count)]

        timeslots = []
        for day in days:
            for i, (start, end) in enumerate(periods):
                timeslots.append(Timeslot(day_of_week=day, period_number=i+1, start_time=start, end_time=end))
        db.session.add_all(timeslots)
        db.session.commit()

        # --- Create Master Data ---
        print("Creating master data (teachers, subjects)...")
        teachers = [Teacher(name=n) for n in ['Mr. Smith', 'Ms. Jones', 'Mr. Davis', 'Ms. Rodriguez', 'Mr. Chen', 'Ms. Williams', 'Mr. Brown', 'Ms. Patel', 'Mr. Wilson', 'Ms. Taylor', 'Mr. Lee', 'Ms. Garcia', 'Mr. Martinez', 'Ms. Nguyen', 'Mr. Kim']]
        subjects = [Subject(name=n) for n in ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'History', 'Geography', 'Art']]
        db.session.add_all(teachers)
        db.session.add_all(subjects)
        db.session.commit()

        # --- Create Grades and Sections ---
        print("Creating grades and sections...")
        grades = [Grade(name=f"Grade {g}") for g in range(6, 11)]
        db.session.add_all(grades)
        db.session.commit()

        sections = []
        for grade in Grade.query.all():
            for s in ['A', 'B', 'C']:
                sections.append(Section(name=f"Section {s}", grade_id=grade.id))
        db.session.add_all(sections)
        db.session.commit()

        # --- Create Courses (Link everything together) ---
        print("Creating courses...")
        # This is a simplified mapping. A real scenario would be more complex.
        courses_to_create = []
        all_sections = Section.query.all()
        teacher_cycle = 0
        for section in all_sections:
            for subject in Subject.query.all():
                # Simple round-robin assignment for demonstration
                teacher = teachers[teacher_cycle % len(teachers)]
                teacher_cycle += 1

                periods_per_week = 4 if subject.name in ['Mathematics', 'English'] else 3

                courses_to_create.append(Course(
                    subject_id=subject.id,
                    teacher_id=teacher.id,
                    section_id=section.id,
                    periods_per_week=periods_per_week
                ))
        db.session.add_all(courses_to_create)
        db.session.commit()

        # --- Create Preferences ---
        print("Creating preferences...")
        # Make Mr. Smith unavailable on Monday morning
        mr_smith = Teacher.query.filter_by(name='Mr. Smith').first()
        monday_morning_slots = Timeslot.query.filter(Timeslot.day_of_week == 'Monday', Timeslot.period_number <= 4).all()
        preferences = [Preference(teacher_id=mr_smith.id, timeslot_id=slot.id, preference_type='unavailable') for slot in monday_morning_slots]
        db.session.add_all(preferences)
        db.session.commit()

        print("Database seed completed successfully!")

if __name__ == '__main__':
    seed_data()
