import unittest
from app.scheduler.generator import TimetableGenerator
from app.scheduler.rescheduler import TimetableRescheduler

class TestScheduler(unittest.TestCase):

    def setUp(self):
        """Set up mock data for testing the scheduler."""
        self.mock_courses = [
            # Reduced periods for teacher 1 to make the schedule possible
            {'id': 1, 'teacher_id': 1, 'section_id': 1, 'periods_per_week': 2},
            {'id': 2, 'teacher_id': 2, 'section_id': 1, 'periods_per_week': 3},
            {'id': 3, 'teacher_id': 1, 'section_id': 2, 'periods_per_week': 2},
        ]
        # A more realistic set of timeslots for a 2-day week, 4 periods per day
        self.mock_timeslots = [
            {'id': i, 'day': day, 'period': p}
            for i, (day, p) in enumerate([
                ('Mon', 1), ('Mon', 2), ('Mon', 3), ('Mon', 4),
                ('Tue', 1), ('Tue', 2), ('Tue', 3), ('Tue', 4)
            ])
        ]
        self.mock_classrooms = [
            {'id': 101, 'name': 'Room 101'},
            {'id': 102, 'name': 'Room 102'},
            {'id': 103, 'name': 'Room 103'},
            {'id': 104, 'name': 'Room 104'},
        ]
        self.mock_constraints = [
            # Mr. A is unavailable on Monday period 3
            {'teacher_id': 1, 'timeslot_id': 3} # Assuming Mr. A has id 1
        ]

    def test_timetable_generator_creates_valid_timetable(self):
        """Test that the TimetableGenerator produces a conflict-free timetable."""
        generator = TimetableGenerator(
            self.mock_courses,
            self.mock_timeslots,
            self.mock_classrooms,
            self.mock_constraints
        )
        timetable = generator.generate()

        # Basic validation: ensure all courses are scheduled
        total_required_periods = sum(c['periods_per_week'] for c in self.mock_courses)
        self.assertEqual(len(timetable), total_required_periods)

        # Check for conflicts (e.g., same teacher in two places at once)
        self.assertTrue(self.is_timetable_valid(timetable))

    def test_rescheduler_finds_valid_alternatives(self):
        """Test that the TimetableRescheduler can find solutions for a conflict."""
        # Create a timetable with a known conflict
        conflicting_timetable = [
            {'course_id': 1, 'teacher_id': 1, 'section_id': 1, 'timeslot_id': 1},
            {'course_id': 3, 'teacher_id': 1, 'section_id': 2, 'timeslot_id': 1}
        ]
        conflicting_lesson_id = 1 # This ID is not used by the rescheduler yet

        rescheduler = TimetableRescheduler(conflicting_timetable, self.mock_courses, self.mock_timeslots, self.mock_constraints)
        solutions = rescheduler.find_solutions_for_conflict(conflicting_lesson_id)

        # Expect the rescheduler to find at least one valid alternative slot
        self.assertGreater(len(solutions), 0)
        # Ensure the proposed solutions are not the conflicting slot
        for sol in solutions:
            self.assertNotEqual(sol['id'], 1)

    def is_timetable_valid(self, schedule):
        """Helper function to check for basic timetable conflicts in a list of lessons."""
        slots_by_teacher = {}
        slots_by_section = {}
        for lesson in schedule:
            teacher_id = lesson['teacher_id']
            section_id = lesson['section_id']
            timeslot_id = lesson['timeslot_id']

            # Check teacher conflicts
            if teacher_id not in slots_by_teacher:
                slots_by_teacher[teacher_id] = set()
            if timeslot_id in slots_by_teacher[teacher_id]:
                return False # Conflict! Teacher scheduled for two lessons at once.
            slots_by_teacher[teacher_id].add(timeslot_id)

            # Check section conflicts
            if section_id not in slots_by_section:
                slots_by_section[section_id] = set()
            if timeslot_id in slots_by_section[section_id]:
                return False # Conflict! Section scheduled for two lessons at once.
            slots_by_section[section_id].add(timeslot_id)

        return True
