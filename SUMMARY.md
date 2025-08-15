# Application Summary: School Timetable Generator

This document provides a high-level summary of how the School Timetable Generator application works, from initial setup to final schedule generation.

## The Goal

The primary goal of this application is to take all the complex requirements of a school's schedule—teachers, subjects, sections, and constraints—and automatically produce a valid, conflict-free timetable. It also provides tools to analyze the school's resource allocation.

## The Workflow: A Step-by-Step Process

The application is designed around a clear, linear workflow, primarily centered in the **Setup Wizard**.

### Step 1: School Settings
This is the foundation. Here, you define the basic grid of the entire schedule:
-   **Number of Periods per Day:** Sets the number of columns in the timetable.
-   **Working Days:** Sets the days of the week that classes can be scheduled on.
When these settings are saved, the application creates the grid of all possible `Timeslots` (e.g., Monday-Period 1, Monday-Period 2, etc.).

### Step 2 & 3: Add Teachers and Subjects
These steps are for entering the master data for the school's resources: all the available teachers and all the subjects that can be taught.

### Step 4: Add Grades, Sections, and Map Subjects
This is a two-part step:
1.  **Create Grades and Sections:** You define the structure of the student body (e.g., Grade 9, Section A).
2.  **Assign Subjects to Sections:** This is a crucial step where you define the curriculum for each section. You select a section (e.g., "Grade 9A") and then choose which subjects are taught to that specific group of students (e.g., "Physics" and "Chemistry", but not "Science").

### Step 5: Teacher Assignments
This is where all the data comes together. For each teacher, you create a list of the specific courses they will teach. A **course** is a unique combination of a **Subject** and a **Section**.
-   The UI in this step is constrained by the mapping from Step 4. When you select a section for a teacher's new assignment, the subject dropdown will only show subjects that are actually offered in that section.
-   You also define the **Periods per Week** for each specific course.
-   Finally, you can set a teacher's **scheduling preferences**, marking certain times of the week as "undesirable" to avoid scheduling them at that time.

### Step 6: Summary
This is a read-only analytical view of all the data you have entered. It helps you answer questions like:
-   Is any teacher significantly overloaded or under-loaded?
-   Do we have enough teachers to cover all the required periods for a specific subject like Math?
This allows you to review your resource allocation before generating the timetable.

## Timetable Generation

Once the setup is complete, you can navigate to the **Dashboard** and click the **"Generate Timetable"** button. This triggers the following process:

1.  **Data Collection:** The backend gathers all the `Course` records you created.
2.  **Lesson Creation:** For each course, it creates the required number of individual "lesson" units (e.g., a course with 5 periods per week becomes 5 lessons to be scheduled).
3.  **Scheduling:** The scheduler takes this big list of lessons and all the available `Timeslots`. It shuffles them randomly and then, one by one, places each lesson into the first valid timeslot it can find. A slot is "valid" if it doesn't break any hard rules (like the teacher or section already being busy at that time).
4.  **Committing:** Once a valid schedule is generated, it is saved to the database as a series of `Lesson` records.
5.  **Display:** The dashboard UI fetches these `Lesson` records and displays them in the timetable grid, allowing you to filter by teacher or section.
