# School Timetable Application - User Manual

## 1. Introduction

Welcome to the School Timetable Application! This tool is designed to help you easily set up your school's parameters and automatically generate a valid, conflict-free class schedule.

This manual will guide you through the two main parts of the application: the **Setup Wizard** and the **Dashboard**.

## 2. The Setup Wizard (`/setup`)

Before you can generate a timetable, you must provide the application with all the necessary data about your school. You can do this through the Setup Wizard.

Navigate to the `/setup` page (e.g., `http://127.0.0.1:5000/setup`) to begin.

The wizard has several steps. You must enter data for each step. After adding an item in each step, the list below the form will update to show the new data.

-   **Step 1: School Settings:** Configure school-wide settings.
    -   **Number of Periods per Day:** Set how many class periods are in a single school day. This will affect how the timetable is generated and displayed.

-   **Step 2: Teachers:** Enter the full name of each teacher and click "Add Teacher".

-   **Step 3: Subjects:** Enter the name of each subject taught at the school (e.g., "Mathematics", "Physics").

-   **Step 4: Classrooms:** Enter the name or number of each available classroom.

-   **Step 5: Grades & Sections:** First, add the grades (e.g., "Grade 9", "Grade 10"). Then, for each grade, select it from the dropdown and enter a section name (e.g., "Section A").

-   **Step 6: Courses:** This is where you link everything together. For each section, define which subjects they take and which teacher teaches them. You must also specify how many periods of that subject the section has per week. Use the dropdowns to select the teacher, subject, and section.

-   **Step 7: Constraints:** Here you can specify when certain teachers are unavailable. For example, if a teacher is part-time and does not work on Friday mornings, you can add a constraint for them for those timeslots.

## 3. The Dashboard (`/dashboard`)

The Dashboard is the main screen where you will generate and view the timetable.

### Generating a Timetable

1.  Make sure you have entered all your data in the Setup Wizard. The `seed.py` script also populates the database with a full set of sample data, so you can start generating right away.
2.  Navigate to the Dashboard page.
3.  Click the **"Generate Timetable"** button. The button will show a "loading" message.
4.  The page will then display the generated timetable in the main grid. You can see the progress and data being logged in your browser's developer console.

### Reading the Timetable

The timetable is displayed in a grid format with days of the week across the top and time periods down the side. The number of periods shown will match what you configured in the Settings.

### View Options

The "View Options" panel on the left allows you to change how the timetable is displayed.

-   **View by:** You can select to view the schedule from the perspective of a "Grade/Section", a "Teacher", or a "Classroom".
-   **Select:** When you change the "View by" option, this second dropdown will automatically update with the correct list of items (e.g., a list of all teachers). Selecting an item from this list will eventually filter the timetable, though this filtering feature is planned for a future update.

## 4. Troubleshooting

-   **Error when generating timetable:** If you see an error message like "Failed to generate timetable", it usually means the problem is impossible to solve with the data you have provided.
    -   **Check your constraints:** Do you have a teacher scheduled to teach more lessons than there are available time slots?
    -   **Check your resources:** Do you have enough classrooms for all the sections?
-   **"Item already exists" error:** When adding a teacher, subject, etc., you might see this error. This means an item with that same name already exists in the database, and duplicates are not allowed.
-   **Other errors:** Check the server window (the terminal where you ran `python run.py`) and your browser's developer console (usually opened with F12) for detailed error messages and logs.
