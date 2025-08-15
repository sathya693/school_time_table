import unittest
from app import create_app, db
from app.models import Teacher, Subject, Course, Section, Grade

class AnalyticsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create sample data
        t1 = Teacher(name='Mr. A')
        t2 = Teacher(name='Ms. B')
        s1 = Subject(name='Math')
        s2 = Subject(name='Art')
        g1 = Grade(name='Grade 1')
        sec1 = Section(name='A', grade=g1)

        db.session.add_all([t1, t2, s1, s2, g1, sec1])
        db.session.commit()

        # Mr. A teaches Math to Sec A for 5 periods
        c1 = Course(teacher_id=t1.id, subject_id=s1.id, section_id=sec1.id, periods_per_week=5)
        # Ms. B teaches Math to Sec A for 5 periods (co-teacher)
        c2 = Course(teacher_id=t2.id, subject_id=s1.id, section_id=sec1.id, periods_per_week=5)
        # Ms. B also teaches Art to Sec A for 2 periods
        c3 = Course(teacher_id=t2.id, subject_id=s2.id, section_id=sec1.id, periods_per_week=2)

        db.session.add_all([c1, c2, c3])
        db.session.commit()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_teacher_workload(self):
        from app.analytics import get_teacher_workload
        workload = get_teacher_workload()

        self.assertEqual(len(workload), 2)

        # Find Mr. A and Ms. B in the workload list
        mr_a_workload = next((item for item in workload if item['teacher_name'] == 'Mr. A'), None)
        ms_b_workload = next((item for item in workload if item['teacher_name'] == 'Ms. B'), None)

        self.assertIsNotNone(mr_a_workload)
        self.assertIsNotNone(ms_b_workload)

        self.assertEqual(mr_a_workload['assigned_periods'], 5)
        self.assertEqual(ms_b_workload['assigned_periods'], 7)

    def test_subject_demand_and_supply(self):
        from app.analytics import get_subject_demand_and_supply
        analysis = get_subject_demand_and_supply()

        self.assertEqual(len(analysis), 2)

        math_analysis = next((item for item in analysis if item['subject_name'] == 'Math'), None)
        art_analysis = next((item for item in analysis if item['subject_name'] == 'Art'), None)

        self.assertIsNotNone(math_analysis)
        self.assertIsNotNone(art_analysis)

        self.assertEqual(math_analysis['required_periods'], 10) # 5 from Mr. A + 5 from Ms. B
        self.assertEqual(math_analysis['available_teachers'], 2)

        self.assertEqual(art_analysis['required_periods'], 2)
        self.assertEqual(art_analysis['available_teachers'], 1)

    def test_teacher_sufficiency_analysis(self):
        from app.analytics import get_subject_demand_and_supply, analyze_teacher_sufficiency
        subject_analysis = get_subject_demand_and_supply()
        sufficiency = analyze_teacher_sufficiency(subject_analysis, periods_per_teacher=8) # Low value for testing

        math_sufficiency = next((item for item in sufficiency if item['subject_name'] == 'Math'), None)
        art_sufficiency = next((item for item in sufficiency if item['subject_name'] == 'Art'), None)

        self.assertIsNotNone(math_sufficiency)
        self.assertIsNotNone(art_sufficiency)

        # Math: 10 required, 2 teachers * 8 periods = 16 available. 10/16 = 62.5%, which is not > 80%. Status should be Surplus.
        self.assertEqual(math_sufficiency['status'], 'Surplus')

        # Art: 2 required, 1 teacher * 8 periods = 8 available. Status should be Surplus
        self.assertEqual(art_sufficiency['status'], 'Surplus')

        # Test shortage
        shortage_subject_analysis = [{"subject_name": "Gym", "required_periods": 10, "available_teachers": 1}]
        shortage_sufficiency = analyze_teacher_sufficiency(shortage_subject_analysis, periods_per_teacher=8)
        self.assertEqual(shortage_sufficiency[0]['status'], 'Shortage')
