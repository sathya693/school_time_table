from flask import Blueprint, render_template, request, jsonify
from . import db
from .models import Teacher, Subject, Classroom, Section, Course, Constraint

main = Blueprint('main', __name__)

# Page-rendering routes
@main.route('/')
def index():
    """Serves the main dashboard page."""
    return render_template('dashboard.html')

@main.route('/dashboard')
def dashboard():
    """Serves the main dashboard page."""
    return render_template('dashboard.html')

@main.route('/setup')
def setup():
    """Serves the setup wizard page."""
    return render_template('setup.html')


# API routes (to be implemented fully later)
@main.route('/api/data', methods=['GET'])
def get_all_data():
    # This is a placeholder implementation.
    # It will be expanded to query the database.
    response = {
        "teachers": [],
        "subjects": [],
        "grades": [],
        "sections": [],
        "classrooms": []
    }
    return jsonify(response), 200

@main.route('/api/data/teacher', methods=['POST'])
def create_teacher():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Invalid payload. 'name' is required."}), 400

    new_teacher = Teacher(name=data['name'])
    db.session.add(new_teacher)
    db.session.commit()

    return jsonify({"message": "Teacher created successfully", "id": new_teacher.id}), 201

# Add other API endpoints later...
