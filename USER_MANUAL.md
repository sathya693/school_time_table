# School Timetable Application - User Manual

## 1. Introduction

Welcome to the School Timetable Application! This tool is designed to help you easily set up your school's parameters and automatically generate a valid, conflict-free class schedule.

This manual will guide you through the two main parts of the application: the **Setup Wizard** and the **Dashboard**.

## 2. The Setup Wizard (`/setup`)

Before you can generate a timetable, you must provide the application with all the necessary data about your school. You can do this through the Setup Wizard.

Navigate to the `/setup` page (e.g., `http://127.0.0.1:5000/setup`) to begin.

The wizard has several steps. You must enter data for each step.

-   **Step 1: Teachers:** Enter the full name of each teacher and click "Add Teacher".
-   **Step 2: Subjects:** Enter the name of each subject taught at the school (e.g., "Mathematics", "Physics") and click "Add Subject".
-   **Step 3: Classrooms:** Enter the name or number of each available classroom.
-   **Step 4: Grades & Sections:** First, add the grades (e.g., "Grade 9", "Grade 10"). Then, for each grade, add the sections (e.g., "Section A", "Section B").
-   **Step 5: Courses:** This is where you link everything together. For each section, define which subjects they take and which teacher teaches them. You must also specify how many periods of that subject the section has per week.
-   **Step 6: Constraints:** Here you can specify when certain teachers are unavailable. For example, if a teacher is part-time and does not work on Friday mornings, you can add a constraint for them for those timeslots.

Complete all steps to ensure the generator has all the information it needs.

## 3. The Dashboard (`/dashboard`)

The Dashboard is the main screen where you will generate and view the timetable.

### Generating a Timetable

1.  Make sure you have entered all your data in the Setup Wizard.
2.  Navigate to the Dashboard page.
3.  Click the **"Generate Timetable"** button.
4.  Please wait a few moments. The system will run the scheduling algorithm.
5.  The page will refresh and display the generated timetable in the main grid.

### Reading the Timetable

The timetable is displayed in a grid format with days of the week across the top and time periods down the side.

Each cell in the grid represents a class, and will show:
-   **Subject Name**
-   **Teacher Name**
-   **Section Name**

### View Options

The "View Options" panel on the left allows you to change how the timetable is displayed.

-   **View by:** You can select to view the schedule from the perspective of a "Grade/Section", a "Teacher", or a "Classroom".
-   **Select:** Once you choose a view type, this dropdown will be populated with the corresponding items (e.g., a list of all teachers). Selecting an item will filter the main grid to show only the schedule for that teacher.

*(Note: The view filtering logic is a feature for future development. Currently, the grid will always show the full schedule.)*

## 4. Troubleshooting

-   **Error when generating timetable:** If you see an error message like "Failed to generate timetable", it usually means the problem is impossible to solve with the data you have provided.
    -   **Check your constraints:** Do you have a teacher scheduled to teach more lessons than there are available time slots?
    -   **Check your resources:** Do you have enough classrooms for all the sections that need to have classes at the same time?
    -   Try removing some constraints or reducing the number of periods for some courses in the Setup wizard.
-   **Data not saving:** If you add a teacher and they don't appear, make sure the application server is running correctly in your terminal. Any errors will be displayed there.
