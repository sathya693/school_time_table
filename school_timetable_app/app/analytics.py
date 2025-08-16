from .models import Teacher, Subject, Course
from collections import defaultdict

def get_teacher_workload(total_available_periods):
    """Calculates the number of periods assigned to each teacher."""
    teachers = Teacher.query.all()
    workload = []
    for teacher in teachers:
        assigned_periods = sum(course.periods_per_week for course in teacher.courses)
        free_periods = total_available_periods - assigned_periods
        workload.append({
            "teacher_name": teacher.name,
            "assigned_periods": assigned_periods,
            "free_periods": free_periods
        })
    return sorted(workload, key=lambda x: x['assigned_periods'], reverse=True)

def get_subject_demand_and_supply():
    """
    Calculates the total periods required for each subject and the number of
    unique teachers assigned to teach it.
    """
    subjects = Subject.query.all()
    courses = Course.query.all()

    demand = defaultdict(int)
    supply = defaultdict(set)

    for course in courses:
        demand[course.subject_id] += course.periods_per_week
        supply[course.subject_id].add(course.teacher_id)

    analysis = []
    for subject in subjects:
        analysis.append({
            "subject_name": subject.name,
            "required_periods": demand[subject.id],
            "available_teachers": len(supply[subject.id])
        })
    return sorted(analysis, key=lambda x: x['required_periods'], reverse=True)

def analyze_teacher_sufficiency(subject_analysis, periods_per_teacher=40):
    """
    Analyzes if there are enough teachers for each subject.
    Assumes a standard work week (e.g., 40 periods).
    """
    sufficiency_analysis = []
    for subject in subject_analysis:
        available_periods = subject['available_teachers'] * periods_per_teacher
        required_periods = subject['required_periods']

        status = "Surplus"
        if required_periods > available_periods:
            status = "Shortage"
        elif required_periods > available_periods * 0.8: # If using > 80% of capacity
            status = "Adequate"

        sufficiency_analysis.append({
            "subject_name": subject['subject_name'],
            "required_periods": required_periods,
            "available_periods": available_periods,
            "available_teachers": subject['available_teachers'],
            "status": status
        })
    return sufficiency_analysis

def get_section_fill_analysis():
    """
    Calculates a detailed breakdown of subject assignments for each section,
    comparing required periods (from section-subject mapping) to assigned
    periods (from created courses).
    """
    from .models import Section, Configuration, Course

    config_q = Configuration.query.all()
    config = {c.key: c.value for c in config_q}

    periods_per_day = int(config.get('periods_per_day', 8))
    work_days = config.get('work_days', 'Monday,Tuesday,Wednesday,Thursday,Friday').split(',')
    total_available = periods_per_day * len(work_days)

    sections = Section.query.all()
    analysis = []
    for section in sections:
        # Get all courses that have been created and assigned to this section
        assigned_courses = Course.query.filter_by(section_id=section.id).all()
        assigned_periods_map = defaultdict(int)
        for c in assigned_courses:
            assigned_periods_map[c.subject_id] += c.periods_per_week

        subjects_detail = []
        # Iterate through subjects that SHOULD be taught to this section
        for required_subject in section.subjects:
            required_periods = 5 # Defaulting to 5 as per seed data logic

            # Check if a course was actually created and assigned for this subject
            assigned_periods = assigned_periods_map.get(required_subject.id, 0)

            subjects_detail.append({
                "subject_name": required_subject.name,
                "required": required_periods,
                "assigned": assigned_periods
            })

        total_assigned = sum(item['assigned'] for item in subjects_detail)
        status = "Fully Scheduled"
        if total_assigned < total_available:
            status = "Under Scheduled"
        elif total_assigned > total_available:
            status = "Over Scheduled"

        analysis.append({
            "section_name": f"{section.grade.name} - {section.name}",
            "assigned_periods": total_assigned,
            "available_periods": total_available,
            "status": status,
            "subjects": sorted(subjects_detail, key=lambda x: x['subject_name'])
        })
    return sorted(analysis, key=lambda x: x['section_name'])


def generate_summary_data():
    """Generates all data needed for the summary/analytics page."""
    from .models import Configuration

    # Get base config to calculate total available periods
    config_q = Configuration.query.all()
    config = {c.key: c.value for c in config_q}
    periods_per_day = int(config.get('periods_per_day', 8))
    work_days = config.get('work_days', 'Monday,Tuesday,Wednesday,Thursday,Friday').split(',')
    total_available_periods = periods_per_day * len(work_days)

    # Generate all analytics components
    teacher_workload = get_teacher_workload(total_available_periods)
    subject_demand_supply = get_subject_demand_and_supply()
    teacher_sufficiency = analyze_teacher_sufficiency(subject_demand_supply)
    section_fill = get_section_fill_analysis()
    total_teachers = Teacher.query.count()

    return {
        "teacher_workload": teacher_workload,
        "subject_analysis": teacher_sufficiency,
        "section_fill_analysis": section_fill,
        "key_metrics": {
            "total_teachers": total_teachers,
            "total_sections": len(section_fill)
        }
    }
