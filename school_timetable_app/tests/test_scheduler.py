import pytest
from app.scheduler.generator import TimetableGenerator
from app.scheduler.rescheduler import TimetableRescheduler

@pytest.fixture(scope='module')
def mock_data():
    """Provides mock data for scheduler tests."""
    mock_courses = [
        {'id': 1, 'teacher_id': 1, 'section_id': 1, 'periods_per_week': 2},
        {'id': 2, 'teacher_id': 2, 'section_id': 1, 'periods_per_week': 3},
        {'id': 3, 'teacher_id': 1, 'section_id': 2, 'periods_per_week': 2},
    ]
    mock_timeslots = [
        {'id': i, 'day': day, 'period': p}
        for i, (day, p) in enumerate([
            ('Mon', 1), ('Mon', 2), ('Mon', 3), ('Mon', 4),
            ('Tue', 1), ('Tue', 2), ('Tue', 3), ('Tue', 4)
        ])
    ]
    mock_classrooms = [{'id': 101 + i, 'name': f'Room {101+i}'} for i in range(4)]
    mock_constraints = [{'teacher_id': 1, 'timeslot_id': 3}]

    return {
        "courses": mock_courses,
        "timeslots": mock_timeslots,
        "classrooms": mock_classrooms,
        "constraints": mock_constraints
    }

def is_timetable_valid(schedule):
    """Helper function to check for basic timetable conflicts."""
    slots_by_teacher = {}
    slots_by_section = {}
    for lesson in schedule:
        teacher_id = lesson['teacher_id']
        section_id = lesson['section_id']
        timeslot_id = lesson['timeslot_id']
        if teacher_id not in slots_by_teacher:
            slots_by_teacher[teacher_id] = set()
        if timeslot_id in slots_by_teacher[teacher_id]: return False
        slots_by_teacher[teacher_id].add(timeslot_id)
        if section_id not in slots_by_section:
            slots_by_section[section_id] = set()
        if timeslot_id in slots_by_section[section_id]: return False
        slots_by_section[section_id].add(timeslot_id)
    return True

def test_timetable_generator_creates_valid_timetable(mock_data):
    """Test that the TimetableGenerator produces a conflict-free timetable."""
    generator = TimetableGenerator(
        mock_data["courses"],
        mock_data["timeslots"],
        mock_data["classrooms"],
        mock_data["constraints"],
        {} # Empty config for this test
    )
    timetable = generator.generate()

    assert timetable is not None
    total_required_periods = sum(c['periods_per_week'] for c in mock_data["courses"])
    assert len(timetable) == total_required_periods
    assert is_timetable_valid(timetable)

def test_rescheduler_finds_valid_alternatives(mock_data):
    """Test that the TimetableRescheduler can find solutions for a conflict."""
    conflicting_timetable = [
        {'course_id': 1, 'teacher_id': 1, 'section_id': 1, 'timeslot_id': 1},
        {'course_id': 3, 'teacher_id': 1, 'section_id': 2, 'timeslot_id': 1}
    ]
    conflicting_lesson_course_id = 1

    rescheduler = TimetableRescheduler(
        conflicting_timetable,
        mock_data["courses"],
        mock_data["timeslots"],
        mock_data["constraints"],
        {} # Empty config
    )
    solutions = rescheduler.find_solutions_for_conflict(conflicting_lesson_course_id)

    assert len(solutions) > 0
    for sol in solutions:
        assert sol['id'] != 1
