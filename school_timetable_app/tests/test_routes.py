import unittest
import json
from app import create_app, db
from app.models import Teacher

class TestRoutes(unittest.TestCase):

    def setUp(self):
        """Set up a test environment."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        """Tear down the test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_all_data_endpoint(self):
        """Test the GET /api/data endpoint."""
        response = self.client.get('/api/data')
        self.assertEqual(response.status_code, 200)
        # We expect an empty data structure initially
        data = json.loads(response.data)
        self.assertIn('teachers', data)
        self.assertIn('subjects', data)
        self.assertIn('grades', data)

    def test_create_teacher_endpoint(self):
        """Test the POST /api/data/teacher endpoint for successful creation."""
        payload = {'name': 'Dr. Turing'}
        response = self.client.post(
            '/api/data/teacher',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201) # 201 Created
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Teacher created successfully')
        self.assertEqual(Teacher.query.count(), 1)
        self.assertEqual(Teacher.query.first().name, 'Dr. Turing')

    def test_create_teacher_endpoint_invalid_payload(self):
        """Test the POST /api/data/teacher endpoint with invalid data."""
        payload = {'fullname': 'Dr. Turing'} # Invalid key
        response = self.client.post(
            '/api/data/teacher',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400) # 400 Bad Request
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_generate_timetable_endpoint(self):
        """Test the POST /api/timetable/generate endpoint."""
        response = self.client.post('/api/timetable/generate')
        # This might be an async task, so we check for a success-like response
        self.assertIn(response.status_code, [200, 202]) # 200 OK or 202 Accepted
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Timetable generation started.')
