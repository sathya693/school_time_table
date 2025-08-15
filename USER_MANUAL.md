# School Timetable Application - User Manual

## 1. Introduction

Welcome to the School Timetable Application! This tool is designed to help you easily set up your school's parameters and automatically generate a valid, conflict-free class schedule. You can then view the schedule from different perspectives and make manual adjustments using a drag-and-drop interface.

This manual will guide you through the two main parts of the application: the **Setup Wizard** and the **Dashboard**.

## 2. The Setup Wizard (`/setup`)

Before you can generate a timetable, you must provide the application with all the necessary data about your school. Navigate to the `/setup` page (e.g., `http://127.0.0.1:5000/setup`) to begin.

The wizard will guide you through 7 steps. After adding an item in each step, the list below the form will update to show the new data.

-   **Step 1: School Settings:** Configure school-wide settings.
    -   **Number of Periods per Day:** Set how many class periods are in a single school day. This will affect how the timetable is generated and displayed. Click "Save Settings" to apply.

-   **Step 2: Teachers:** Enter the full name of each teacher and click "Add Teacher".

-   **Step 3: Subjects:** Enter the name of each subject taught at the school (e.g., "Mathematics", "Physics").

-   **Step 4: Classrooms:** Enter the name or number of each available classroom.

-   **Step 5: Grades & Sections:** First, add the grades (e.g., "Grade 9"). Then, for each grade, select it from the dropdown and enter a section name (e.g., "Section A").

-   **Step 6: Courses:** This is where you link everything together. For each section, define which subjects they take and which teacher teaches them. You must also specify how many periods of that subject the section has per week. Use the dropdowns to select the teacher, subject, and section.

-   **Step 7: Constraints:** Here you can specify when certain teachers are unavailable. For example, if a teacher is part-time and does not work on Friday mornings, you can add a constraint for them for those timeslots.

## 3. The Dashboard (`/dashboard`)

The Dashboard is the main screen where you will generate, view, and edit the timetable.

### Loading and Generating a Timetable
- **On Page Load:** The application will automatically try to load a previously saved timetable from the database. If one is found, it will be displayed.
- **Generating:** If no schedule is found, or if you want to create a new one, click the **"Generate Timetable"** button. The application will use all the data you entered in the Setup Wizard to create a schedule. After generation, the new schedule is automatically saved and displayed.

### Reading and Filtering the Timetable
- **The Grid:** The timetable is a grid with days across the top and periods down the side. Each colored block is a lesson.
- **View Options:** The "View Options" panel on the left lets you filter the view.
    1.  **View by:** Select whether you want to see the schedule for a "Section", "Teacher", or "Classroom".
    2.  **Select:** This dropdown will then be filled with the appropriate items. Choose one to filter the grid. Select the "All" option to see the full, unfiltered timetable again.

### Manual Editing
You can make manual changes to the schedule using drag-and-drop.
1. Click the **"Enable Edit Mode"** button. It will turn red, and the lessons on the grid will become draggable.
2. Drag any lesson from its current timeslot to a new, empty timeslot.
3. The application will automatically validate the move. If the move is valid (doesn't create a conflict), the lesson will move to the new slot. If it's invalid, an alert will appear explaining the conflict, and the lesson will remain in its original position.
4. Click **"Disable Edit Mode"** to turn off drag-and-drop.

### Validating the Timetable
After making manual edits, you can check the entire schedule for conflicts.
1. Click the **"Validate"** button.
2. The "Conflicts & Suggestions" panel will update. It will either show a "No conflicts found" message or a list of all conflicts in the current schedule.

## 4. Troubleshooting
-   **Error when generating timetable:** If you see an error, it often means the problem is impossible to solve with the data you provided (e.g., a teacher has more lessons than available timeslots). Review your data in the Setup wizard.
-   **"Item already exists" error:** When adding a teacher, subject, etc., this means an item with that same name already exists. Duplicates are not allowed.
-   **Other errors:** Check the server window (the terminal where you ran `python run.py`) and your browser's developer console (usually opened with F12) for detailed error messages and logs.
