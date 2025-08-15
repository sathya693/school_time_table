import unittest
from app.scheduler.generator import TimetableGenerator
from app.scheduler.rescheduler import TimetableRescheduler

class TestScheduler(unittest.TestCase):

    def setUp(self):
        """Set up mock data for testing the scheduler."""
        self.mock_courses = [
            {'id': 1, 'name': 'Math-9A', 'teacher': 'Mr. A', 'section': '9A', 'periods': 4},
            {'id': 2, 'name': 'Physics-9A', 'teacher': 'Mr. B', 'section': '9A', 'periods': 3},
            {'id': 3, 'name': 'Math-10A', 'teacher': 'Mr. A', 'section': '10A', 'periods': 4},
        ]
        self.mock_timeslots = [
            {'id': 1, 'day': 'Monday', 'period': 1},
            {'id': 2, 'day': 'Monday', 'period': 2},
            {'id': 3, 'day': 'Monday', 'period': 3},
            # ... add many more timeslots for a realistic scenario
        ]
        self.mock_constraints = [
            # Mr. A is unavailable on Monday period 3
            {'teacher': 'Mr. A', 'timeslot_id': 3, 'available': False}
        ]

    def test_timetable_generator_creates_valid_timetable(self):
        """Test that the TimetableGenerator produces a conflict-free timetable."""
        generator = TimetableGenerator(
            self.mock_courses,
            self.mock_timeslots,
            self.mock_constraints
        )
        timetable = generator.generate()

        # Basic validation: ensure all courses are scheduled
        scheduled_periods = sum(len(lessons) for lessons in timetable.values())
        total_required_periods = sum(c['periods'] for c in self.mock_courses)
        self.assertEqual(scheduled_periods, total_required_periods)

        # Check for conflicts (e.g., same teacher in two places at once)
        # This requires a more complex check which we'll flesh out later
        self.assertTrue(self.is_timetable_valid(timetable))

    def test_rescheduler_finds_valid_alternatives(self):
        """Test that the TimetableRescheduler can find solutions for a conflict."""
        # Create a timetable with a known conflict
        conflicting_timetable = {
            # Mr. A is scheduled for Math-9A and Math-10A at the same time
            1: [{'course_id': 1, 'timeslot_id': 1}, {'course_id': 3, 'timeslot_id': 1}]
        }
        conflicting_lesson_id = 1 # Let's say this is the lesson to reschedule

        rescheduler = TimetableRescheduler(conflicting_timetable, self.mock_courses, self.mock_timeslots, self.mock_constraints)
        solutions = rescheduler.find_solutions_for_conflict(conflicting_lesson_id)

        # Expect the rescheduler to find at least one valid alternative slot
        self.assertGreater(len(solutions), 0)
        # Ensure the proposed solutions are not the conflicting slot
        for sol in solutions:
            self.assertNotEqual(sol['timeslot_id'], 1)

    def is_timetable_valid(self, timetable):
        """Helper function to check for basic timetable conflicts."""
        # This is a placeholder for a real validation function
        # A real one would check for teacher, section, and room clashes
        slots_by_teacher = {}
        for lesson_list in timetable.values():
            for lesson in lesson_list:
                teacher = self.get_teacher_for_course(lesson['course_id'])
                timeslot = lesson['timeslot_id']
                if teacher not in slots_by_teacher:
                    slots_by_teacher[teacher] = set()
                if timeslot in slots_by_teacher[teacher]:
                    return False # Conflict!
                slots_by_teacher[teacher].add(timeslot)
        return True

    def get_teacher_for_course(self, course_id):
        """Helper to get teacher from mock data."""
        for course in self.mock_courses:
            if course['id'] == course_id:
                return course['teacher']
        return None
