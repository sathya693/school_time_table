import random

class TimetableGenerator:
    """
    Generates a school timetable using a recursive backtracking algorithm.
    """
    def __init__(self, courses, timeslots, config=None, preferences=None):
        """
        Initializes the generator with necessary data.
        """
        self.courses = courses
        self.timeslots = timeslots
        self.config = config if config is not None else {}
        self.preferences = preferences if preferences is not None else []

        # Pre-process for faster lookups
        self.prefs_map = {}
        for p in self.preferences:
            key = (p['teacher_id'], p['timeslot_id'])
            self.prefs_map[key] = p['preference_type']

        self.timeslot_map = {t['id']: t for t in self.timeslots}

    def generate(self):
        """
        Main method to generate the timetable.
        """
        print("Starting timetable generation...")
        return self._construct_initial_solution()

    def _is_hard_constraint_violated(self, schedule, lesson, timeslot, day_subject_section_lookup):
        """Checks for hard constraint violations for a potential lesson placement."""
        if not timeslot:
            return True

        # O(1) check for the "no subject clumping" rule
        day_of_week = timeslot.get('day')
        lookup_key = (day_of_week, lesson['section_id'], lesson['course_id'])
        if lookup_key in day_subject_section_lookup:
            return True

        # Check teacher availability constraint
        key = (lesson['teacher_id'], timeslot['id'])
        if self.prefs_map.get(key) in ['unavailable', 'undesirable']:
            return True

        # Check for teacher/section clashes for the current timeslot
        for scheduled_lesson in schedule:
            if scheduled_lesson['timeslot_id'] == timeslot['id']:
                if scheduled_lesson['teacher_id'] == lesson['teacher_id']:
                    return True  # Teacher clash
                if scheduled_lesson['section_id'] == lesson['section_id']:
                    return True  # Section clash
        return False

    def _construct_initial_solution(self):
        """
        Sets up and kicks off the recursive backtracking solver.
        """
        lessons_to_schedule = []
        for course in self.courses:
            for _ in range(course['periods_per_week']):
                lessons_to_schedule.append({
                    'course_id': course['id'],
                    'teacher_id': course['teacher_id'],
                    'section_id': course['section_id']
                })

        # Heuristic: Sort lessons to schedule the ones for the busiest teachers first.
        teacher_ids = {c['teacher_id'] for c in self.courses}
        teacher_workload = {tid: 0 for tid in teacher_ids}
        for c in self.courses:
            teacher_workload[c['teacher_id']] += c['periods_per_week']
        lessons_to_schedule.sort(key=lambda l: teacher_workload.get(l['teacher_id'], 0), reverse=True)

        final_schedule = []
        day_subject_section_lookup = set()

        def solve(lesson_index):
            if lesson_index >= len(lessons_to_schedule):
                return True

            lesson = lessons_to_schedule[lesson_index]

            possible_slots = []
            for timeslot in self.timeslots:
                if not self._is_hard_constraint_violated(final_schedule, lesson, timeslot, day_subject_section_lookup):
                    score = 5 if self.prefs_map.get((lesson['teacher_id'], timeslot['id'])) == 'desirable' else 0
                    possible_slots.append({'slot': timeslot, 'score': score})

            possible_slots.sort(key=lambda x: x['score'], reverse=True)

            for possibility in possible_slots:
                slot = possibility['slot']

                final_schedule.append({**lesson, 'timeslot_id': slot['id']})
                lookup_key = (slot['day'], lesson['section_id'], lesson['course_id'])
                day_subject_section_lookup.add(lookup_key)

                if solve(lesson_index + 1):
                    return True

                day_subject_section_lookup.remove(lookup_key)
                final_schedule.pop()

            return False

        if solve(0):
            print("Successfully generated a valid timetable.")
            return final_schedule
        else:
            print("Failed to construct an initial solution. The problem is likely unsolvable.")
            return None
