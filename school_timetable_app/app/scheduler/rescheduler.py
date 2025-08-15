class TimetableRescheduler:
    """
    Finds alternative slots for a conflicting lesson.
    """
    def __init__(self, schedule, courses, timeslots, constraints, config=None):
        """
        Initializes the rescheduler.

        Args:
            schedule (list of dicts): The current timetable, potentially with conflicts.
            courses (list of dicts): All available courses.
            timeslots (list of dicts): All available timeslots.
            constraints (list of dicts): Teacher unavailability constraints.
            config (dict): Application configuration, e.g., lunch break period.
        """
        self.schedule = schedule
        self.courses = courses
        self.timeslots = timeslots
        self.constraints = constraints
        self.config = config if config is not None else {}

        # Pre-process for faster lookups
        self.teacher_constraints = {}
        for c in self.constraints:
            if c['teacher_id'] not in self.teacher_constraints:
                self.teacher_constraints[c['teacher_id']] = set()
            self.teacher_constraints[c['teacher_id']].add(c['timeslot_id'])

        self.schedule_by_timeslot = {}
        for lesson in self.schedule:
            tid = lesson.get('timeslot_id')
            if tid not in self.schedule_by_timeslot:
                self.schedule_by_timeslot[tid] = []
            self.schedule_by_timeslot[tid].append(lesson)

        self.timeslot_map = {t['id']: t for t in self.timeslots}

    def find_solutions_for_conflict(self, conflicting_lesson_course_id):
        """
        Finds valid alternative slots for a lesson that is part of a conflict.

        Args:
            conflicting_lesson_course_id (int): The course ID of the lesson to be rescheduled.

        Returns:
            A list of valid timeslot dictionaries that are potential solutions.
        """
        # For simplicity, we find the first lesson matching the course ID to reschedule.
        # A more robust implementation would take a specific lesson instance ID.
        lesson_to_reschedule = None
        for lesson in self.schedule:
            if lesson['course_id'] == conflicting_lesson_course_id:
                lesson_to_reschedule = lesson
                break

        if not lesson_to_reschedule:
            return []

        solutions = []
        for timeslot in self.timeslots:
            # A slot is a potential solution if it's not the lesson's current slot
            # and it doesn't violate any hard constraints.
            if timeslot['id'] != lesson_to_reschedule.get('timeslot_id') and \
               not self._is_hard_constraint_violated(lesson_to_reschedule, timeslot['id']):
                solutions.append(timeslot)

        return solutions

    def _is_hard_constraint_violated(self, lesson, timeslot_id):
        """
        Checks if placing a lesson in a given timeslot violates any hard constraints.
        """
        timeslot = self.timeslot_map.get(timeslot_id)
        if not timeslot:
            return True # Should not happen

        # Check for lunch break
        lunch_break_period = self.config.get('lunch_break_period')
        if lunch_break_period and timeslot.get('period') == int(lunch_break_period):
            return True # It's lunch time

        # Check teacher availability constraint
        if lesson['teacher_id'] in self.teacher_constraints and \
           timeslot_id in self.teacher_constraints[lesson['teacher_id']]:
            return True

        # Check for clashes with other lessons already scheduled in that timeslot
        if timeslot_id in self.schedule_by_timeslot:
            for scheduled_lesson in self.schedule_by_timeslot[timeslot_id]:
                # Ignore the lesson we are trying to reschedule itself
                if scheduled_lesson['course_id'] == lesson['course_id']:
                    continue

                if scheduled_lesson['teacher_id'] == lesson['teacher_id']:
                    return True # Teacher clash
                if scheduled_lesson['section_id'] == lesson['section_id']:
                    return True # Section clash

        return False
