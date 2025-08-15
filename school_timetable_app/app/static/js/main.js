document.addEventListener('DOMContentLoaded', () => {
    const page = window.location.pathname;

    if (page.includes('/setup')) {
        initSetupWizard();
    } else if (page.includes('/dashboard') || page === '/') {
        initDashboard();
    }
});

// --- Setup Wizard Logic (existing code) ---
function initSetupWizard() {
    // ... (keeping existing setup wizard logic as is)
    const steps = document.querySelectorAll('.wizard-step');
    const indicators = document.querySelectorAll('.step-indicator');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const finishBtn = document.getElementById('finish-btn');
    let currentStep = 0;

    function updateWizard() {
        steps.forEach((step, index) => {
            step.classList.toggle('active', index === currentStep);
        });
        indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === currentStep);
        });
        prevBtn.style.display = currentStep === 0 ? 'none' : 'inline-block';
        nextBtn.style.display = currentStep === steps.length - 1 ? 'none' : 'inline-block';
        finishBtn.style.display = currentStep === steps.length - 1 ? 'inline-block' : 'none';
    }

    nextBtn.addEventListener('click', () => { if (currentStep < steps.length - 1) { currentStep++; updateWizard(); } });
    prevBtn.addEventListener('click', () => { if (currentStep > 0) { currentStep--; updateWizard(); } });

    const teacherForm = document.getElementById('form-add-teacher');
    const teacherNameInput = document.getElementById('teacher-name');
    const teachersList = document.getElementById('teachers-list');

    teacherForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = teacherNameInput.value.trim();
        if (!name) return;
        try {
            const response = await fetch('/api/data/teacher', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name })
            });
            if (!response.ok) { throw new Error('Failed to add teacher.'); }
            const teacherElement = document.createElement('div');
            teacherElement.textContent = name;
            teachersList.appendChild(teacherElement);
            teacherNameInput.value = '';
        } catch (error) {
            console.error(error);
            alert(error.message);
        }
    });
    updateWizard();
}

// --- Dashboard Logic ---
async function initDashboard() {
    const generateBtn = document.getElementById('btn-generate');
    const timetableGrid = document.getElementById('timetable-grid');
    const viewValueSelect = document.getElementById('view-value');
    let allData = {}; // To store data from /api/data

    // 1. Fetch initial data to populate controls
    try {
        const response = await fetch('/api/data');
        if (!response.ok) throw new Error('Failed to fetch initial data.');
        allData = await response.json();

        // Populate the dropdown
        // For now, we'll just populate with sections as a default
        allData.sections.forEach(section => {
            const option = document.createElement('option');
            option.value = section.name; // A more robust implementation would use ID
            option.textContent = `${section.grade} - ${section.name}`;
            viewValueSelect.appendChild(option);
        });
    } catch (error) {
        console.error(error);
        alert(error.message);
    }

    // 2. Add event listener to the Generate button
    generateBtn.addEventListener('click', async () => {
        timetableGrid.innerHTML = '<p>Generating timetable, please wait...</p>';
        try {
            const response = await fetch('/api/timetable/generate', { method: 'POST' });
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || 'Failed to generate timetable.');
            }
            const schedule = await response.json();
            renderTimetable(schedule, allData);
        } catch (error) {
            console.error(error);
            timetableGrid.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        }
    });
}

function renderTimetable(schedule, allData) {
    const timetableGrid = document.getElementById('timetable-grid');

    // This is a simplified renderer. A real one would be more robust.
    // It assumes a 5-day week and 8 periods per day.
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const periods = 8;

    // Create grid structure
    let gridHtml = '<div class="grid-header">Time</div>';
    days.forEach(day => gridHtml += `<div class="grid-header">${day}</div>`);

    for (let p = 1; p <= periods; p++) {
        gridHtml += `<div class="grid-cell time-label">Period ${p}</div>`; // Time label
        for (const day of days) {
            gridHtml += `<div class="grid-cell" data-day="${day}" data-period="${p}"></div>`;
        }
    }
    timetableGrid.innerHTML = gridHtml;

    // Populate the grid with lessons
    // This is inefficient and for demo only. A real app would pre-process this mapping.
    schedule.forEach(lesson => {
        const timeslot = allData.timeslots.find(t => t.id === lesson.timeslot_id);
        const course = allData.courses.find(c => c.id === lesson.course_id);
        const teacher = allData.teachers.find(t => t.id === course.teacher_id);
        const section = allData.sections.find(s => s.id === course.section_id);
        const subject = allData.subjects.find(s => s.id === course.subject_id);

        if (timeslot && course) {
            const cell = timetableGrid.querySelector(`[data-day="${timeslot.day}"][data-period="${timeslot.period}"]`);
            if (cell) {
                const lessonEl = document.createElement('div');
                lessonEl.className = 'lesson';
                lessonEl.innerHTML = `
                    <div class="lesson-subject">${subject ? subject.name : 'Unknown Subject'}</div>
                    <div class="lesson-teacher">${teacher ? teacher.name : 'Unknown Teacher'}</div>
                    <div class="lesson-section">${section ? section.name : 'Unknown Section'}</div>
                `;
                cell.appendChild(lessonEl);
            }
        }
    });

    // This is a very basic renderer. A real implementation would need to handle:
    // - The "View by" logic to filter what is shown.
    // - Clashes in the view (e.g. if viewing by teacher and two sections are shown in one slot).
    // - Much more efficient data lookups.
    // The current data from API doesn't contain all info needed for rendering, this is a known limitation.
    // I will add the missing data to the API response.
}
