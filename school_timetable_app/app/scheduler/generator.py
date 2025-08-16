import random

class TimetableGenerator:
    """
    Generates a school timetable using a hybrid two-phase algorithm.
    1. Constructive Heuristic: Builds a valid initial solution.
    2. Metaheuristic Optimizer: Improves the solution using Tabu Search.
    """
    def __init__(self, courses, timeslots, config=None, preferences=None):
        """
        Initializes the generator with necessary data.

        Args:
            courses (list of dicts): Courses to be scheduled.
            timeslots (list of dicts): Available timeslots.
            config (dict): Application configuration, e.g., lunch break period.
            preferences (list of dicts): Teacher preferences for timeslots.
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

        # Pre-process timeslots for faster lookup
        self.timeslot_map = {t['id']: t for t in self.timeslots}

    def generate(self):
        """
        Main method to generate the timetable.
        """
        print("Starting timetable generation...")
        # Phase 1: Construct an initial, valid solution
        initial_solution = self._construct_initial_solution()
        if not initial_solution:
            print("Failed to construct an initial solution.")
            return None

        # Phase 2: Optimize the solution using Tabu Search
        # For this example, we will return the initial solution.
        # The optimization logic is complex and would be added here.
        print("Initial solution constructed. Optimization phase skipped for now.")
        # optimized_solution = self._optimize_solution(initial_solution)

        return initial_solution

    def _is_hard_constraint_violated(self, schedule, lesson, timeslot_id):
        """Checks for hard constraint violations for a potential lesson placement."""
        timeslot = self.timeslot_map.get(timeslot_id)
        if not timeslot:
            return True # Should not happen

        # Check teacher availability constraint
        key = (lesson['teacher_id'], timeslot_id)
        preference = self.prefs_map.get(key)
        if preference in ['unavailable', 'undesirable']:
            return True # Teacher is unavailable or has marked the slot as undesirable

        # Check for clashes
        for scheduled_lesson in schedule:
            if scheduled_lesson['timeslot_id'] == timeslot_id:
                if scheduled_lesson['teacher_id'] == lesson['teacher_id']:
                    return True # Teacher clash
                if scheduled_lesson['section_id'] == lesson['section_id']:
                    return True # Section clash
        return False

    def _construct_initial_solution(self):
        """
        Constructs an initial timetable using a recursive backtracking algorithm.
        """
        schedule = []
        lessons_to_schedule = []
        for course in self.courses:
            for _ in range(course['periods_per_week']):
                lessons_to_schedule.append({
                    'course_id': course['id'],
                    'teacher_id': course['teacher_id'],
                    'section_id': course['section_id']
                })

        random.shuffle(lessons_to_schedule)

        # The main schedule object to be populated by the recursive solver
        final_schedule = []

        def solve(lesson_index):
            # Base case: If all lessons are scheduled, we found a solution.
            if lesson_index >= len(lessons_to_schedule):
                return True

            lesson = lessons_to_schedule[lesson_index]

            # Find and score all possible slots for the current lesson
            possible_slots = []
            for timeslot in self.timeslots:
                if not self._is_hard_constraint_violated(final_schedule, lesson, timeslot['id']):
                    score = 0
                    if self.prefs_map.get((lesson['teacher_id'], timeslot['id'])) == 'desirable':
                        score = 5
                    possible_slots.append({'slot': timeslot, 'score': score})

            # Sort slots to try the best (most desirable) ones first
            possible_slots.sort(key=lambda x: x['score'], reverse=True)

            # Try to place the lesson in one of the possible slots
            for possibility in possible_slots:
                slot = possibility['slot']

                # 1. Place the lesson
                final_schedule.append({**lesson, 'timeslot_id': slot['id']})

                # 2. Recurse
                if solve(lesson_index + 1):
                    return True # Success, propagate it up

                # 3. Backtrack: If the recursive call failed, undo the placement
                final_schedule.pop()

            # If no possible slot led to a solution, return False
            return False

        # Kick off the recursive solver
        if solve(0):
            return final_schedule
        else:
            print("Failed to construct an initial solution. The problem is likely unsolvable.")
            return None

    def _optimize_solution(self, schedule):
        """
        Optimizes the schedule using a metaheuristic like Tabu Search.
        (This is a placeholder for the complex optimization logic).
        """
        # 1. Initialize: current_best = schedule, tabu_list = []
        # 2. Loop for N iterations:
        # 3.   Generate neighbors (e.g., by swapping two lessons)
        # 4.   Find the best neighbor not in tabu_list
        # 5.   Update current_best
        # 6.   Add the move to tabu_list
        # 7. Return current_best
        print("Optimization logic would run here.")
        return schedule

    def _calculate_fitness(self, schedule):
        """
        Calculates the fitness of a schedule. Lower score is better.
        Penalizes soft constraint violations.
        """
        penalty = 0

        # --- Soft constraint: Teacher gaps ---
        teacher_schedules = {}
        for lesson in schedule:
            tid = lesson['teacher_id']
            if tid not in teacher_schedules:
                teacher_schedules[tid] = []
            teacher_schedules[tid].append(lesson['timeslot_id'])

        for tid, slots in teacher_schedules.items():
            sorted_slots = sorted(slots)
            for i in range(len(sorted_slots) - 1):
                gap = sorted_slots[i+1] - sorted_slots[i]
                if gap > 1:
                    penalty += (gap - 1) # Add penalty for each idle period

        # --- Soft constraint: Teacher preferences ---
        for lesson in schedule:
            teacher_id = lesson['teacher_id']
            timeslot_id = lesson['timeslot_id']
            key = (teacher_id, timeslot_id)

            if key in self.prefs_map:
                pref_type = self.prefs_map[key]
                if pref_type == 'undesirable':
                    penalty += 10  # High penalty for undesirable slots
                elif pref_type == 'desirable':
                    penalty -= 5   # Reward for desirable slots

        return penalty
