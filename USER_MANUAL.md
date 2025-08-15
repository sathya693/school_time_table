# School Timetable Application - User Manual

## 1. Introduction

Welcome to the School Timetable Application! This tool is designed to help you easily set up your school's parameters and automatically generate a valid, conflict-free class schedule. You can then view the schedule from different perspectives and make manual adjustments using a drag-and-drop interface.

This manual will guide you through the two main parts of the application: the **Setup Wizard** and the **Dashboard**.

## 2. The Setup Wizard (`/setup`)

Before you can generate a timetable, you must provide the application with all the necessary data about your school. The `seed.py` script provides a rich set of sample data, but you can use this wizard to add or modify it.

Navigate to the `/setup` page (e.g., `http://127.0.0.1:5000/setup`) to begin.

The wizard guides you through entering all the required information. After you add an item in a step, the list below the form will automatically update to show the new data.

-   **Step 1: School Settings:** This step is for school-wide configurations.
    -   **Number of Periods per Day:** Set how many class periods are in a single school day (e.g., 8). This determines the height of the timetable grid. Click "Save Settings" to apply.

-   **Step 2: Teachers:** Enter the full name of each teacher (e.g., "Mr. Smith") and click "Add Teacher".

-   **Step 3: Subjects:** Enter the name of each subject taught (e.g., "Mathematics", "Physics").

-   **Step 4: Classrooms:** Enter the name or number of each available classroom (e.g., "Room 101", "Science Lab A").

-   **Step 5: Grades & Sections:** This is a two-part step.
    1.  **Add a Grade:** First, enter the name of a grade level (e.g., "Grade 9", "Grade 10").
    2.  **Add a Section:** Once grades exist, select a grade from the dropdown menu and enter a name for a section within that grade (e.g., "Section A").

-   **Step 6: Courses:** This is the most important step for scheduling. A "Course" links a teacher to a subject for a specific section.
    -   Use the dropdowns to select the Teacher, Subject, and Section.
    -   Enter the number of times that course should occur per week in the "Periods per week" box.
    -   Example: To schedule Grade 9A for 5 periods of Math with Mr. Smith, you would select "Mr. Smith", "Mathematics", "Grade 9 - Section A", and enter "5".

-   **Step 7: Constraints:** Here you can specify when a teacher is **not** available.
    -   Select a teacher and a timeslot from the dropdowns.
    -   Clicking "Add Constraint" means that the selected teacher cannot be scheduled for any class during that specific timeslot.

## 3. The Dashboard (`/dashboard`)

The Dashboard is the main screen where you will generate, view, and edit the timetable.

### Loading and Generating a Timetable
- **On Page Load:** The application automatically loads the most recently saved timetable from the database. If no timetable has been saved, you will see a message prompting you to generate one.
- **Generating a New Timetable:** Click the **"Generate Timetable"** button. The application will use all the data from the Setup Wizard to find a valid schedule. This may take a few moments. Once complete, the new schedule is automatically saved and displayed on the grid.

### Reading and Filtering the Timetable
- **The Grid:** The timetable is a grid with days across the top and periods down the side. Each colored block is a lesson showing the subject, teacher, and section.
- **View Options:** The "View Options" panel on the left lets you dynamically filter the view.
    1.  **View by:** Select whether you want to see the schedule for a "Section", "Teacher", or "Classroom". The second dropdown will update automatically.
    2.  **Select:** Choose a specific item from the second dropdown to see only the lessons relevant to it. To see the full schedule again, choose the "All" option.

### Manual Editing (Drag-and-Drop)
1. Click the **"Enable Edit Mode"** button. It will turn red, and the lessons on the grid will become draggable.
2. Click and drag any lesson from its current timeslot to a new, empty timeslot.
3. The application will automatically check if the move is valid. If it is, the lesson will move. If it would create a conflict (e.g., the teacher is already busy), an alert will appear explaining the error, and the lesson will not move.
4. Click **"Disable Edit Mode"** to turn off dragging and save your changes.

### Validating the Timetable
After making manual edits, you can double-check the entire schedule for conflicts.
1. Click the **"Validate"** button.
2. The "Conflicts & Suggestions" panel will show a list of all conflicts or a success message if there are none.

## 4. Troubleshooting
-   **"Failed to generate timetable" error:** This usually means the problem is impossible to solve with the current data. The most common reason is a resource shortage (e.g., a teacher has more assigned periods than there are available timeslots in the week). Try reducing the number of periods for some courses or removing constraints in the Setup Wizard.
-   **"Item already exists" error:** This means an item with that same name already exists in the database. Names for teachers, subjects, etc., must be unique.
-   **For other errors,** check the server window (the terminal where you ran the application) and your browser's developer console (usually opened with F12) for detailed error messages.
