from . import db

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    courses = db.relationship('Course', backref='teacher', lazy=True)
    preferences = db.relationship('Preference', backref='teacher', lazy=True)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    courses = db.relationship('Course', backref='subject', lazy=True)

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    sections = db.relationship('Section', backref='grade', lazy=True)

class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grades.id'), nullable=False)
    courses = db.relationship('Course', backref='section', lazy=True)

class Timeslot(db.Model):
    __tablename__ = 'timeslots'
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.String(20), nullable=False) # e.g., 'Monday'
    period_number = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.String(10), nullable=False) # e.g., '09:00'
    end_time = db.Column(db.String(10), nullable=False) # e.g., '09:45'
    lessons = db.relationship('Lesson', backref='timeslot', lazy=True)

class Preference(db.Model):
    """Represents teacher preferences for certain timeslots (desirable/undesirable)."""
    __tablename__ = 'preferences'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    timeslot_id = db.Column(db.Integer, db.ForeignKey('timeslots.id'), nullable=False)
    preference_type = db.Column(db.String(20), nullable=False) # e.g., 'desirable', 'undesirable'

class Course(db.Model):
    """Represents a course to be scheduled (e.g., Grade 9A Physics with Mr. Smith)."""
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    periods_per_week = db.Column(db.Integer, nullable=False, default=1)
    lessons = db.relationship('Lesson', backref='course', lazy=True)

class Lesson(db.Model):
    """Represents a single, scheduled class in the timetable."""
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    timeslot_id = db.Column(db.Integer, db.ForeignKey('timeslots.id'), nullable=False)

class Configuration(db.Model):
    """A key-value store for application settings."""
    __tablename__ = 'configurations'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=False)
