document.addEventListener('DOMContentLoaded', () => {
    const page = window.location.pathname;
    if (page.includes('/setup')) {
        initSetupWizard();
    } else if (page.includes('/dashboard') || page === '/') {
        initDashboard();
    }
});

// --- Generic Helper Functions ---
async function postData(url, body) {
    console.log('POSTing to', url, 'with body:', body);
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (!response.ok) {
        const errData = await response.json().catch(() => ({ error: "An unknown error occurred." }));
        console.error('API Error:', errData);
        throw new Error(errData.details || errData.error);
    }
    return response.json();
}

// --- Setup Wizard Logic ---
function initSetupWizard() {
    console.log("Initializing Setup Wizard...");
    let allData = {};
    const ui = {
        settingsForm: document.getElementById('form-settings'),
        teacherForm: document.getElementById('form-add-teacher'),
        subjectForm: document.getElementById('form-add-subject'),
        classroomForm: document.getElementById('form-add-classroom'),
        gradeForm: document.getElementById('form-add-grade'),
        sectionForm: document.getElementById('form-add-section'),
        courseForm: document.getElementById('form-add-course'),
        constraintForm: document.getElementById('form-add-constraint'),
        periodsInput: document.getElementById('periods-per-day'),
        lunchBreakInput: document.getElementById('lunch-break-period'),
        workDaysGroup: document.getElementById('work-days-group'),
        sectionGradeSelect: document.getElementById('section-grade-select'),
        courseTeacherSelect: document.getElementById('course-teacher-select'),
        courseSubjectSelect: document.getElementById('course-subject-select'),
        courseSectionSelect: document.getElementById('course-section-select'),
        constraintTeacherSelect: document.getElementById('constraint-teacher-select'),
        constraintTimeslotSelect: document.getElementById('constraint-timeslot-select'),
        teachersList: document.getElementById('teachers-list'),
        subjectsList: document.getElementById('subjects-list'),
        classroomsList: document.getElementById('classrooms-list'),
        gradesList: document.getElementById('grades-list'),
        sectionsList: document.getElementById('sections-list'),
        coursesList: document.getElementById('courses-list'),
        constraintsList: document.getElementById('constraints-list'),
    };

    const reloadData = async () => {
        console.log("Reloading all setup data...");
        try {
            const response = await fetch('/api/data');
            allData = await response.json();
            console.log("Data reloaded:", allData);
            populateAllUI();
        } catch (e) {
            console.error("Failed to reload data", e);
            alert("Failed to load school data. Please check the server connection and refresh the page.");
        }
    };

    const populateAllUI = () => {
        const renderList = (element, items = [], formatter) => {
            if (!element) return;
            element.innerHTML = items.length > 0 ? `<ul>${items.map(i => `<li>${formatter(i)}</li>`).join('')}</ul>` : '<p class="empty-list">No data yet.</p>';
        };
        renderList(ui.teachersList, allData.teachers, t => t.name);
        renderList(ui.subjectsList, allData.subjects, s => s.name);
        renderList(ui.classroomsList, allData.classrooms, c => c.name);
        renderList(ui.gradesList, allData.grades, g => g.name);
        renderList(ui.sectionsList, allData.sections, s => `${s.grade_name} - ${s.name}`);

        const courseFormatter = c => {
            const teacher = (allData.teachers.find(t => t.id === c.teacher_id) || {}).name || 'N/A';
            const subject = (allData.subjects.find(s => s.id === c.subject_id) || {}).name || 'N/A';
            const section = allData.sections.find(s => s.id === c.section_id);
            const sectionName = section ? `${section.grade_name} - ${section.name}` : 'N/A';
            return `${subject} for ${sectionName} (Taught by ${teacher}, ${c.periods_per_week}p/w)`;
        };
        renderList(ui.coursesList, allData.courses, courseFormatter);

        const constraintFormatter = c => {
            const teacher = (allData.teachers.find(t => t.id === c.teacher_id) || {}).name || 'N/A';
            const timeslot = allData.timeslots.find(t => t.id === c.timeslot_id);
            const timeslotLabel = timeslot ? `${timeslot.day_of_week} - Period ${timeslot.period_number}` : 'N/A';
            return `${teacher} is unavailable at ${timeslotLabel}`;
        };
        renderList(ui.constraintsList, allData.constraints, constraintFormatter);

        if (allData.config) {
            if (ui.periodsInput && allData.config.periods_per_day) {
                ui.periodsInput.value = allData.config.periods_per_day;
            }
            if (ui.lunchBreakInput && allData.config.lunch_break_period) {
                ui.lunchBreakInput.value = allData.config.lunch_break_period;
            }
            if (ui.workDaysGroup && allData.config.work_days) {
                const workDays = allData.config.work_days.split(',');
                ui.workDaysGroup.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                    checkbox.checked = workDays.includes(checkbox.value);
                });
            }
        }

        const populateSelect = (selectElement, items = [], text, value, nameKey) => {
            if (!selectElement) return;
            const currentVal = selectElement.value;
            selectElement.innerHTML = `<option value="">Select ${text}</option>`;
            items.forEach(item => {
                const option = document.createElement('option');
                option.value = item[value];
                let label = item[nameKey];
                if (text === 'Section') label = `${item.grade_name} - ${item.name}`;
                if (text === 'Timeslot') label = `${item.day_of_week} - Period ${item.period_number}`;
                option.textContent = label;
                selectElement.appendChild(option);
            });
            selectElement.value = currentVal;
        };
        populateSelect(ui.sectionGradeSelect, allData.grades, 'Grade', 'id', 'name');
        populateSelect(ui.courseTeacherSelect, allData.teachers, 'Teacher', 'id', 'name');
        populateSelect(ui.courseSubjectSelect, allData.subjects, 'Subject', 'id', 'name');
        populateSelect(ui.courseSectionSelect, allData.sections, 'Section', 'id', 'name');
        populateSelect(ui.constraintTeacherSelect, allData.teachers, 'Teacher', 'id', 'name');
        populateSelect(ui.constraintTimeslotSelect, allData.timeslots, 'Timeslot', 'id', 'id');
    };

    const handleFormSubmit = (form, url, getBody) => {
        if (!form) return;
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const button = form.querySelector('button[type="submit"]');
            const originalButtonText = button.textContent;
            button.textContent = 'Saving...';
            button.disabled = true;

            try {
                const body = getBody(e.target);
                if (body && Object.values(body).some(v => !v)) {
                    alert("Please fill out all fields.");
                    return;
                }
                await postData(url, body);
                form.reset();
                await reloadData();
            } catch (error) {
                console.error('Form submission error:', error.message);
                alert(error.message);
            } finally {
                button.textContent = originalButtonText;
                button.disabled = false;
            }
        });
    };

    if (ui.settingsForm) {
        ui.settingsForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const button = ui.settingsForm.querySelector('button[type="submit"]');
            const originalButtonText = button.textContent;
            button.textContent = 'Saving...';
            button.disabled = true;

            try {
                const periodsPerDay = ui.periodsInput.value;
                const lunchBreak = ui.lunchBreakInput.value;
                const workDaysCheckboxes = ui.workDaysGroup.querySelectorAll('input:checked');
                const workDays = Array.from(workDaysCheckboxes).map(cb => cb.value).join(',');

                if (!workDays) {
                    alert("Please select at least one working day.");
                    return;
                }

                const settingsToSave = [
                    { key: 'periods_per_day', value: periodsPerDay },
                    { key: 'work_days', value: workDays },
                    { key: 'lunch_break_period', value: lunchBreak }
                ];

                await Promise.all(settingsToSave.map(setting =>
                    postData('/api/data/setting', setting)
                ));

                button.textContent = 'Saved!';
                setTimeout(() => { button.textContent = originalButtonText; }, 2000);

                await reloadData();
            } catch (error) {
                console.error('Settings submission error:', error.message);
                alert(error.message);
                button.textContent = originalButtonText;
            } finally {
                button.disabled = false;
            }
        });
    }

    handleFormSubmit(ui.teacherForm, '/api/data/teacher', f => ({ name: f.elements['teacher-name'].value.trim() }));
    handleFormSubmit(ui.subjectForm, '/api/data/subject', f => ({ name: f.elements['subject-name'].value.trim() }));
    handleFormSubmit(ui.classroomForm, '/api/data/classroom', f => ({ name: f.elements['classroom-name'].value.trim() }));
    handleFormSubmit(ui.gradeForm, '/api/data/grade', f => ({ name: f.elements['grade-name'].value.trim() }));
    handleFormSubmit(ui.sectionForm, '/api/data/section', f => ({ name: f.elements['section-name'].value.trim(), grade_id: f.elements['section-grade-select'].value }));
    handleFormSubmit(ui.courseForm, '/api/data/course', f => ({ teacher_id: f.elements['course-teacher-select'].value, subject_id: f.elements['course-subject-select'].value, section_id: f.elements['course-section-select'].value, periods_per_week: f.elements['course-periods'].value }));
    handleFormSubmit(ui.constraintForm, '/api/data/constraint', f => ({ teacher_id: f.elements['constraint-teacher-select'].value, timeslot_id: f.elements['constraint-timeslot-select'].value }));

    const steps = document.querySelectorAll('.wizard-step');
    const indicators = document.querySelectorAll('.step-indicator');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const finishBtn = document.getElementById('finish-btn');
    let currentStep = 0;

    const updateWizard = () => {
        steps.forEach((step, index) => step.classList.toggle('active', index === currentStep));
        indicators.forEach((indicator, index) => indicator.classList.toggle('active', index === currentStep));
        prevBtn.style.display = currentStep === 0 ? 'none' : 'inline-block';
        nextBtn.style.display = currentStep === steps.length - 1 ? 'none' : 'inline-block';
        finishBtn.style.display = currentStep === steps.length - 1 ? 'inline-block' : 'none';
    };
    nextBtn.addEventListener('click', () => { if (currentstep < steps.length - 1) { currentstep++; updatewizard(); } });
    prevBtn.addEventListener('click', () => { if (currentstep > 0) { currentstep--; updatewizard(); } });
    finishBtn.addEventListener('click', () => { window.location.href = '/dashboard'; });

    reloadData().then(() => updateWizard());
}

// --- Dashboard Logic ---
async function initDashboard() {
    console.log("Initializing Dashboard...");
    const generateBtn = document.getElementById('btn-generate');
    const timetableGrid = document.getElementById('timetable-grid');
    const timetableTitle = document.getElementById('timetable-title');
    const viewTypeSelect = document.getElementById('view-type');
    const viewValueSelect = document.getElementById('view-value');
    let allData = {};

    const updateViewValueOptions = () => {
        const viewType = viewTypeSelect.value;
        let items = [];
        let itemLabel = "Item";
        if (viewType === 'section') { items = allData.sections || []; itemLabel = "Section"; }
        else if (viewType === 'teacher') { items = allData.teachers || []; itemLabel = "Teacher"; }
        viewValueSelect.innerHTML = `<option value="">All</option>`;
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            // FIX: Explicitly check for section to format the name correctly.
            if (viewType === 'section') {
                option.textContent = `${item.grade_name} - ${item.name}`;
            } else {
                option.textContent = item.name;
            }
            viewValueSelect.appendChild(option);
        });
    };

    const loadInitialState = async () => {
        timetableGrid.innerHTML = '<p>Loading school data...</p>';
        try {
            const dataResponse = await fetch('/api/data');
            if (!dataResponse.ok) throw new Error('Failed to fetch school data.');
            allData = await dataResponse.json();
            console.log("Dashboard data received:", allData);
            updateViewValueOptions();

            const timetableResponse = await fetch('/api/timetable');
            if (!timetableResponse.ok) throw new Error('Failed to fetch timetable.');
            const schedule = await timetableResponse.json();
            if (schedule && schedule.length > 0) {
                console.log("Existing schedule found, rendering...");
                timetableTitle.textContent = 'Full Timetable';
                // FIX: Store the full, original schedule in the dataset only once.
                timetableGrid.dataset.originalSchedule = JSON.stringify(schedule);
                renderTimetable(schedule, allData);
            } else {
                timetableTitle.textContent = 'No Schedule Found';
                timetableGrid.innerHTML = '<p>No schedule found in the database. Go to the Setup page to add data, then click "Generate Timetable".</p>';
            }
        } catch (error) {
            console.error(error);
            timetableGrid.innerHTML = `<p style="color:red;">${error.message}</p>`;
        }
    };

    const filterAndRender = () => {
        const viewType = viewTypeSelect.value;
        const viewId = viewValueSelect.value;
        // FIX: Always filter from the original, full schedule.
        const originalSchedule = JSON.parse(timetableGrid.dataset.originalSchedule || '[]');
        const selectedOption = viewValueSelect.options[viewValueSelect.selectedIndex];
        timetableTitle.textContent = viewId ? `Timetable for ${selectedOption.textContent}` : 'Full Timetable';
        renderTimetable(originalSchedule, allData, viewType, viewId);
    };

    viewTypeSelect.addEventListener('change', () => {
        updateViewValueOptions();
        // Reset the second dropdown and re-render the full schedule
        viewValueSelect.value = "";
        filterAndRender();
    });
    viewValueSelect.addEventListener('change', filterAndRender);

    generateBtn.addEventListener('click', async () => {
        console.log("Generate Timetable button clicked.");
        timetableGrid.innerHTML = '<p>Generating timetable, please wait...</p>';
        timetableTitle.textContent = "Generating...";
        try {
            const generateResponse = await fetch('/api/timetable/generate', { method: 'POST' });
            if (!generateResponse.ok) {
                const errData = await generateResponse.json();
                throw new Error(errData.details || 'Failed to generate timetable.');
            }
            const schedule = await generateResponse.json();
            await postData('/api/timetable/commit', schedule);
            const finalSchedule = await (await fetch('/api/timetable')).json();
            timetableTitle.textContent = "Full Timetable";
            // FIX: Update the original schedule dataset after generating a new one.
            timetableGrid.dataset.originalSchedule = JSON.stringify(finalSchedule);
            renderTimetable(finalSchedule, allData);
        } catch (error) {
            console.error(error);
            timetableTitle.textContent = "Error!";
            timetableGrid.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        }
    });

    loadInitialState();
}

function renderTimetable(schedule, allData, viewType = 'section', viewId = null) {
    console.log(`Rendering timetable with filter: ${viewType}, ${viewId}`);
    const timetableGrid = document.getElementById('timetable-grid');

    const days = allData.config.work_days ? allData.config.work_days.split(',') : ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const periods = allData.config ? parseInt(allData.config.periods_per_day) || 8 : 8;

    // --- Transposed Grid Logic ---
    let gridHtml = '<div class="grid-header">Day</div>';
    for (let p = 1; p <= periods; p++) {
        gridHtml += `<div class="grid-header">Period ${p}</div>`;
    }

    const timeslotMap = {};
    if(allData.timeslots) {
        allData.timeslots.forEach(t => {
            if (!timeslotMap[t.day_of_week]) timeslotMap[t.day_of_week] = {};
            timeslotMap[t.day_of_week][t.period_number] = t.id;
        });
    }

    for (const day of days) {
        gridHtml += `<div class="grid-cell day-label">${day}</div>`; // Day label
        for (let p = 1; p <= periods; p++) {
            const timeslotId = timeslotMap[day] ? timeslotMap[day][p] || '' : '';
            gridHtml += `<div class="grid-cell" data-timeslot-id="${timeslotId}"></div>`;
        }
    }
    timetableGrid.innerHTML = gridHtml;
    // Adjust CSS grid columns dynamically
    timetableGrid.style.gridTemplateColumns = `120px repeat(${periods}, 1fr)`;

    let filteredSchedule = schedule;
    if (viewId && viewId !== "") {
        const numericViewId = parseInt(viewId);
        const courseMap = new Map(allData.courses.map(c => [c.id, c]));
        if (viewType === 'teacher') {
            filteredSchedule = schedule.filter(l => (courseMap.get(l.course_id) || {}).teacher_id === numericViewId);
        } else if (viewType === 'section') {
            filteredSchedule = schedule.filter(l => (courseMap.get(l.course_id) || {}).section_id === numericViewId);
        }
    }

    filteredSchedule.forEach(lesson => {
        const timeslot = allData.timeslots.find(t => t.id === lesson.timeslot_id);
        const course = allData.courses.find(c => c.id === lesson.course_id);
        if (!timeslot || !course) return;

        const teacher = allData.teachers.find(t => t.id === course.teacher_id);
        const section = allData.sections.find(s => s.id === course.section_id);
        const subject = allData.subjects.find(s => s.id === course.subject_id);

        const cell = timetableGrid.querySelector(`[data-timeslot-id="${timeslot.id}"]`);
        if (cell) {
            const lessonEl = document.createElement('div');
            lessonEl.className = 'lesson';
            lessonEl.innerHTML = `
                <div class="lesson-subject">${subject ? subject.name : '...'}</div>
                <div class="lesson-teacher">${teacher ? teacher.name : '...'}</div>
                <div class="lesson-section">${section ? (section.grade_name + ' - ' + section.name) : '...'}</div>
            `;
            cell.appendChild(lessonEl);
        }
    });
    console.log("Timetable rendering complete.");
}
