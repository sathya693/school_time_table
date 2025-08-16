from .models import Teacher, Subject, Course
from collections import defaultdict

def get_teacher_workload():
    """Calculates the number of periods assigned to each teacher."""
    teachers = Teacher.query.all()
    workload = []
    for teacher in teachers:
        total_periods = sum(course.periods_per_week for course in teacher.courses)
        workload.append({
            "teacher_name": teacher.name,
            "assigned_periods": total_periods
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
    Calculates how many assigned periods each section has versus the total
    available periods in a week.
    """
    from .models import Section, Configuration

    config_q = Configuration.query.all()
    config = {c.key: c.value for c in config_q}

    periods_per_day = int(config.get('periods_per_day', 8))
    work_days = config.get('work_days', 'Monday,Tuesday,Wednesday,Thursday,Friday').split(',')
    total_available = periods_per_day * len(work_days)

    sections = Section.query.all()
    analysis = []
    for section in sections:
        assigned_periods = sum(course.periods_per_week for course in section.courses)
        status = "Fully Scheduled"
        if assigned_periods < total_available:
            status = "Under Scheduled"
        elif assigned_periods > total_available:
            status = "Over Scheduled"

        analysis.append({
            "section_name": f"{section.grade.name} - {section.name}",
            "assigned_periods": assigned_periods,
            "available_periods": total_available,
            "status": status
        })
    return sorted(analysis, key=lambda x: x['section_name'])


def generate_summary_data():
    """Generates all data needed for the summary/analytics page."""
    teacher_workload = get_teacher_workload()
    subject_demand_supply = get_subject_demand_and_supply()
    teacher_sufficiency = analyze_teacher_sufficiency(subject_demand_supply)
    section_fill = get_section_fill_analysis()

    return {
        "teacher_workload": teacher_workload,
        "subject_analysis": teacher_sufficiency,
        "section_fill_analysis": section_fill
    }
