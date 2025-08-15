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
        // Forms
        settingsForm: document.getElementById('form-add-setting'),
        teacherForm: document.getElementById('form-add-teacher'),
        subjectForm: document.getElementById('form-add-subject'),
        classroomForm: document.getElementById('form-add-classroom'),
        gradeForm: document.getElementById('form-add-grade'),
        sectionForm: document.getElementById('form-add-section'),
        courseForm: document.getElementById('form-add-course'),
        constraintForm: document.getElementById('form-add-constraint'),
        // Inputs
        periodsInput: document.getElementById('periods-per-day'),
        // Selects
        sectionGradeSelect: document.getElementById('section-grade-select'),
        courseTeacherSelect: document.getElementById('course-teacher-select'),
        courseSubjectSelect: document.getElementById('course-subject-select'),
        courseSectionSelect: document.getElementById('course-section-select'),
        constraintTeacherSelect: document.getElementById('constraint-teacher-select'),
        constraintTimeslotSelect: document.getElementById('constraint-timeslot-select'),
        // Data Lists
        teachersList: document.getElementById('teachers-list'),
        subjectsList: document.getElementById('subjects-list'),
        classroomsList: document.getElementById('classrooms-list'),
        gradesList: document.getElementById('grades-list'),
        sectionsList: document.getElementById('sections-list'),
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
            element.innerHTML = items.length > 0 ? items.map(formatter).join('') : '<div>No data yet.</div>';
        };
        renderList(ui.teachersList, allData.teachers, t => `<div>${t.name}</div>`);
        renderList(ui.subjectsList, allData.subjects, s => `<div>${s.name}</div>`);
        renderList(ui.classroomsList, allData.classrooms, c => `<div>${c.name}</div>`);
        renderList(ui.gradesList, allData.grades, g => `<div>${g.name}</div>`);
        renderList(ui.sectionsList, allData.sections, s => `<div>${s.grade_name} - ${s.name}</div>`);

        if (ui.periodsInput && allData.config && allData.config.periods_per_day) {
            ui.periodsInput.value = allData.config.periods_per_day;
        }

        const populateSelect = (selectElement, items = [], text, value, name) => {
            if (!selectElement) return;
            selectElement.innerHTML = `<option value="">Select ${text}</option>`;
            items.forEach(item => {
                const option = document.createElement('option');
                option.value = item[value];
                option.textContent = item[name] || `${item.grade_name || item.day_of_week} - ${item.name || item.period_number}`;
                selectElement.appendChild(option);
            });
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
            try {
                const body = getBody(e.target);
                if (body && Object.values(body).some(v => !v)) {
                    alert("Please fill out all fields.");
                    return;
                }
                await postData(url, body);
                if(form.id !== 'form-add-setting') form.reset();
                await reloadData();
            } catch (error) {
                console.error('Form submission error:', error.message);
                alert(error.message);
            }
        });
    };

    handleFormSubmit(ui.settingsForm, '/api/data/setting', f => ({ key: 'periods_per_day', value: f.elements['periods-per-day'].value }));
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
    nextBtn.addEventListener('click', () => { if (currentStep < steps.length - 1) { currentStep++; updateWizard(); } });
    prevBtn.addEventListener('click', () => { if (currentStep > 0) { currentStep--; updateWizard(); } });

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
        else if (viewType === 'classroom') { items = allData.classrooms || []; itemLabel = "Classroom"; }
        viewValueSelect.innerHTML = `<option value="">All</option>`;
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.name || `${item.grade_name} - ${item.name}`;
            viewValueSelect.appendChild(option);
        });
    };

    const loadInitialState = async () => {
        timetableGrid.innerHTML = '<p>Loading initial data...</p>';
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
                renderTimetable(schedule, allData);
            } else {
                timetableGrid.innerHTML = '<p>No schedule found. Use the Setup page to add data, then click "Generate Timetable".</p>';
            }
        } catch (error) {
            console.error(error);
            timetableGrid.innerHTML = `<p style="color:red;">${error.message}</p>`;
        }
    };

    const filterAndRender = () => {
        const viewType = viewTypeSelect.value;
        const viewId = viewValueSelect.value;
        const currentSchedule = JSON.parse(timetableGrid.dataset.currentSchedule || '[]');
        const selectedOption = viewValueSelect.options[viewValueSelect.selectedIndex];
        timetableTitle.textContent = viewId ? `Timetable for ${selectedOption.textContent}` : 'Full Timetable';
        renderTimetable(currentSchedule, allData, viewType, viewId);
    };

    viewTypeSelect.addEventListener('change', () => {
        updateViewValueOptions();
        filterAndRender();
    });
    viewValueSelect.addEventListener('change', filterAndRender);

    generateBtn.addEventListener('click', async () => {
        console.log("Generate Timetable button clicked.");
        timetableGrid.innerHTML = '<p>Generating timetable, please wait...</p>';
        try {
            const generateResponse = await fetch('/api/timetable/generate', { method: 'POST' });
            if (!generateResponse.ok) {
                const errData = await generateResponse.json();
                throw new Error(errData.error || 'Failed to generate timetable.');
            }
            const schedule = await generateResponse.json();
            await postData('/api/timetable/commit', schedule);
            const finalSchedule = await (await fetch('/api/timetable')).json();
            renderTimetable(finalSchedule, allData);
        } catch (error) {
            console.error(error);
            timetableGrid.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        }
    });

    loadInitialState();
}

function renderTimetable(schedule, allData, viewType = 'section', viewId = null) {
    console.log(`Rendering timetable with filter: ${viewType}, ${viewId}`);
    const timetableGrid = document.getElementById('timetable-grid');
    timetableGrid.dataset.currentSchedule = JSON.stringify(schedule);

    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const periods = allData.config ? parseInt(allData.config.periods_per_day) || 8 : 8;

    let gridHtml = '<div class="grid-header">Time</div>';
    days.forEach(day => gridHtml += `<div class="grid-header">${day}</div>`);

    const timeslotMap = {};
    allData.timeslots.forEach(t => {
        if (!timeslotMap[t.day_of_week]) timeslotMap[t.day_of_week] = {};
        timeslotMap[t.day_of_week][t.period_number] = t.id;
    });

    for (let p = 1; p <= periods; p++) {
        gridHtml += `<div class="grid-cell time-label">Period ${p}</div>`;
        for (const day of days) {
            const timeslotId = timeslotMap[day] ? timeslotMap[day][p] || '' : '';
            gridHtml += `<div class="grid-cell" data-timeslot-id="${timeslotId}"></div>`;
        }
    }
    timetableGrid.innerHTML = gridHtml;

    let filteredSchedule = schedule;
    if (viewId && viewId !== "") {
        const numericViewId = parseInt(viewId);
        const courseMap = new Map(allData.courses.map(c => [c.id, c]));
        if (viewType === 'teacher') {
            filteredSchedule = schedule.filter(l => (courseMap.get(l.course_id) || {}).teacher_id === numericViewId);
        } else if (viewType === 'section') {
            filteredSchedule = schedule.filter(l => (courseMap.get(l.course_id) || {}).section_id === numericViewId);
        } else if (viewType === 'classroom') {
            filteredSchedule = schedule.filter(l => l.classroom_id === numericViewId);
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
