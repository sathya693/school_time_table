import pytest
import json
from app import create_app, db
from app.models import Teacher, Subject, Grade, Section, Classroom, Timeslot, Course

@pytest.fixture(scope='module')
def test_app():
    """Set up a test Flask app for the whole module."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(test_app):
    """A test client for the app."""
    return test_app.test_client()

def test_get_all_data_endpoint(client):
    """Test the GET /api/data endpoint."""
    response = client.get('/api/data')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'teachers' in data
    assert 'subjects' in data
    assert 'grades' in data

def test_create_teacher_endpoint(client):
    """Test the POST /api/data/teacher endpoint for successful creation."""
    payload = {'name': 'Dr. Turing'}
    response = client.post('/api/data/teacher', json=payload)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Teacher created successfully'
    assert Teacher.query.count() == 1
    assert Teacher.query.first().name == 'Dr. Turing'

def test_create_teacher_endpoint_invalid_payload(client):
    """Test the POST /api/data/teacher endpoint with invalid data."""
    payload = {'fullname': 'Dr. Turing'} # Invalid key
    response = client.post('/api/data/teacher', json=payload)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_generate_timetable_endpoint(client, test_app):
    """Test the POST /api/timetable/generate endpoint with data."""
    with test_app.app_context():
        # Setup: Create necessary data in the test database
        teacher = Teacher(name='Test Teacher')
        subject = Subject(name='Test Subject')
        grade = Grade(name='Test Grade')
        section = Section(name='Test Section', grade=grade)
        classroom = Classroom(name='Test Room')
        timeslot = Timeslot(day_of_week='Monday', period_number=1, start_time='09:00', end_time='10:00')
        db.session.add_all([teacher, subject, grade, section, classroom, timeslot])
        db.session.commit()

        course = Course(teacher_id=teacher.id, subject_id=subject.id, section_id=section.id, periods_per_week=1)
        db.session.add(course)
        db.session.commit()

        # Action: Call the endpoint
        response = client.post('/api/timetable/generate')

        # Assert: Check for a successful response and valid schedule
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['course_id'] == course.id
