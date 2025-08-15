class TimetableRescheduler:
    """
    Finds alternative slots for a conflicting lesson.
    """
    def __init__(self, schedule, courses, timeslots, constraints):
        """
        Initializes the rescheduler.

        Args:
            schedule (list of dicts): The current timetable, potentially with conflicts.
            courses (list of dicts): All available courses.
            timeslots (list of dicts): All available timeslots.
            constraints (list of dicts): Teacher unavailability constraints.
        """
        self.schedule = schedule
        self.courses = courses
        self.timeslots = timeslots
        self.constraints = constraints

        # Pre-process for faster lookups
        self.teacher_constraints = {}
        for c in self.constraints:
            if c['teacher_id'] not in self.teacher_constraints:
                self.teacher_constraints[c['teacher_id']] = set()
            self.teacher_constraints[c['teacher_id']].add(c['timeslot_id'])

        self.schedule_by_timeslot = {}
        for lesson in self.schedule:
            tid = lesson['timeslot_id']
            if tid not in self.schedule_by_timeslot:
                self.schedule_by_timeslot[tid] = []
            self.schedule_by_timeslot[tid].append(lesson)

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
