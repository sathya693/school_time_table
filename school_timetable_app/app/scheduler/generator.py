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
        Constructs an initial timetable using a greedy first-fit algorithm.
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

        random.shuffle(lessons_to_schedule) # Introduce randomness

        for lesson in lessons_to_schedule:
            possible_slots = []
            # Find all valid slots for the current lesson
            for timeslot in self.timeslots:
                if not self._is_hard_constraint_violated(schedule, lesson, timeslot['id']):
                    possible_slots.append(timeslot)

            if not possible_slots:
                print(f"Failed to place a lesson for course {lesson['course_id']}. Not enough resources or too many constraints.")
                return None  # Failed to create a valid schedule

            # Score the possible slots to find the best one
            best_slot = None
            max_score = -1

            # Shuffle the possible slots to avoid bias for neutral slots
            random.shuffle(possible_slots)

            for slot in possible_slots:
                score = 0 # Neutral score
                key = (lesson['teacher_id'], slot['id'])
                if self.prefs_map.get(key) == 'desirable':
                    score = 5 # Desirable score

                if score > max_score:
                    max_score = score
                    best_slot = slot
                # If the best possible score is already found, no need to check further
                if max_score == 5:
                    break

            # If no slot had a positive score, best_slot will be the first random valid one
            if best_slot is None:
                best_slot = possible_slots[0]

            schedule.append({
                **lesson,
                'timeslot_id': best_slot['id'],
            })

        return schedule

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
