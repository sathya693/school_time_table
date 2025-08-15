import unittest
from app import create_app, db
from app.models import Teacher, Subject, Grade, Section, Course

class TestModels(unittest.TestCase):

    def setUp(self):
        """Set up a test environment."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Tear down the test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_teacher(self):
        """Test creating a teacher."""
        teacher = Teacher(name='Mr. Smith')
        db.session.add(teacher)
        db.session.commit()
        self.assertEqual(Teacher.query.count(), 1)
        self.assertEqual(Teacher.query.first().name, 'Mr. Smith')

    def test_create_subject(self):
        """Test creating a subject."""
        subject = Subject(name='Mathematics')
        db.session.add(subject)
        db.session.commit()
        self.assertEqual(Subject.query.count(), 1)
        self.assertEqual(Subject.query.first().name, 'Mathematics')

    def test_grade_and_section_relationship(self):
        """Test the relationship between Grade and Section."""
        grade = Grade(name='Grade 10')
        db.session.add(grade)
        db.session.commit()

        section = Section(name='Section A', grade_id=grade.id)
        db.session.add(section)
        db.session.commit()

        self.assertEqual(Section.query.count(), 1)
        self.assertEqual(Grade.query.count(), 1)
        self.assertEqual(Section.query.first().grade, grade)
        self.assertIn(section, Grade.query.first().sections)

    def test_create_course(self):
        """Test creating a course that links teacher, subject, and section."""
        # Create dependencies
        teacher = Teacher(name='Ms. Davis')
        subject = Subject(name='Physics')
        grade = Grade(name='Grade 11')
        section = Section(name='Section B', grade=grade)
        db.session.add_all([teacher, subject, grade, section])
        db.session.commit()

        # Create Course
        course = Course(
            teacher_id=teacher.id,
            subject_id=subject.id,
            section_id=section.id,
            periods_per_week=4
        )
        db.session.add(course)
        db.session.commit()

        self.assertEqual(Course.query.count(), 1)
        queried_course = Course.query.first()
        self.assertEqual(queried_course.teacher, teacher)
        self.assertEqual(queried_course.subject, subject)
        self.assertEqual(queried_course.section, section)
        self.assertEqual(queried_course.periods_per_week, 4)
