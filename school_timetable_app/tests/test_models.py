import pytest
from app import create_app, db
from app.models import Teacher, Subject, Grade, Section, Course

@pytest.fixture(scope='module')
def test_app():
    """Set up a test Flask app for the whole module."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app  # a.k.a. "the test runs now"
        db.session.remove()
        db.drop_all()

def test_create_teacher(test_app):
    """Test creating a teacher."""
    teacher = Teacher(name='Mr. Smith')
    db.session.add(teacher)
    db.session.commit()
    assert Teacher.query.count() == 1
    assert Teacher.query.first().name == 'Mr. Smith'

def test_create_subject(test_app):
    """Test creating a subject."""
    subject = Subject(name='Mathematics')
    db.session.add(subject)
    db.session.commit()
    assert Subject.query.count() == 1
    assert Subject.query.first().name == 'Mathematics'

def test_grade_and_section_relationship(test_app):
    """Test the relationship between Grade and Section."""
    grade = Grade(name='Grade 10')
    db.session.add(grade)
    db.session.commit()

    section = Section(name='Section A', grade_id=grade.id)
    db.session.add(section)
    db.session.commit()

    assert Section.query.count() == 1
    assert Grade.query.count() == 1
    assert Section.query.first().grade == grade
    assert section in Grade.query.first().sections

def test_create_course(test_app):
    """Test creating a course that links teacher, subject, and section."""
    teacher = Teacher(name='Ms. Davis')
    subject = Subject(name='Physics')
    grade = Grade(name='Grade 11')
    section = Section(name='Section B', grade=grade)
    db.session.add_all([teacher, subject, grade, section])
    db.session.commit()

    course = Course(
        teacher_id=teacher.id,
        subject_id=subject.id,
        section_id=section.id,
        periods_per_week=4
    )
    db.session.add(course)
    db.session.commit()

    queried_course = Course.query.first()
    assert Course.query.count() == 1
    assert queried_course.teacher == teacher
    assert queried_course.subject == subject
    assert queried_course.section == section
    assert queried_course.periods_per_week == 4
