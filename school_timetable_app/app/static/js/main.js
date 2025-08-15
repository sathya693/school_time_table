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
        gradeForm: document.getElementById('form-add-grade'),
        sectionForm: document.getElementById('form-add-section'),

        periodsInput: document.getElementById('periods-per-day'),
        workDaysGroup: document.getElementById('work-days-group'),

        sectionGradeSelect: document.getElementById('section-grade-select'),

        // New Assignment UI
        assignmentTeacherSelect: document.getElementById('assignment-teacher-select'),
        teacherAssignmentDetails: document.getElementById('teacher-assignment-details'),
        subjectAssignmentContainer: document.getElementById('subject-assignment-container'),
        btnAddSubjectAssignment: document.getElementById('btn-add-subject-assignment'),
        preferencesContainer: document.getElementById('preferences-container'),
        btnSaveTeacherAssignments: document.getElementById('btn-save-teacher-assignments'),

        // Data lists
        teachersList: document.getElementById('teachers-list'),
        subjectsList: document.getElementById('subjects-list'),
        gradesList: document.getElementById('grades-list'),
        sectionsList: document.getElementById('sections-list'),

        // New Section-Subject UI
        sectionSubjectSelect: document.getElementById('section-subject-select'),
        sectionSubjectChecklist: document.getElementById('section-subject-checklist'),
        btnSaveSectionSubjects: document.getElementById('btn-save-section-subjects'),
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
        renderList(ui.gradesList, allData.grades, g => g.name);
        renderList(ui.sectionsList, allData.sections, s => `${s.grade_name} - ${s.name}`);

        if (allData.config) {
            if (ui.periodsInput && allData.config.periods_per_day) {
                ui.periodsInput.value = allData.config.periods_per_day;
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
        populateSelect(ui.assignmentTeacherSelect, allData.teachers, 'Teacher', 'id', 'name');
        populateSelect(ui.sectionSubjectSelect, allData.sections, 'Section', 'id', 'name');
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
                const workDaysCheckboxes = ui.workDaysGroup.querySelectorAll('input:checked');
                const workDays = Array.from(workDaysCheckboxes).map(cb => cb.value).join(',');

                if (!workDays) {
                    alert("Please select at least one working day.");
                    return;
                }

                const payload = {
                    periods_per_day: periodsPerDay,
                    work_days: workDays,
                };

                await postData('/api/settings', payload);

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
    handleFormSubmit(ui.gradeForm, '/api/data/grade', f => ({ name: f.elements['grade-name'].value.trim() }));
    handleFormSubmit(ui.sectionForm, '/api/data/section', f => ({ name: f.elements['section-name'].value.trim(), grade_id: f.elements['section-grade-select'].value }));

    // --- Section-Subject Assignment Logic ---

    const renderSubjectChecklist = (assignedSubjectIds = []) => {
        const assignedSet = new Set(assignedSubjectIds);
        ui.sectionSubjectChecklist.innerHTML = '';
        allData.subjects.forEach(subject => {
            const isChecked = assignedSet.has(subject.id);
            const label = document.createElement('label');
            label.innerHTML = `<input type="checkbox" value="${subject.id}" ${isChecked ? 'checked' : ''}> ${subject.name}`;
            ui.sectionSubjectChecklist.appendChild(label);
        });
    };

    if (ui.sectionSubjectSelect) {
        ui.sectionSubjectSelect.addEventListener('change', async (e) => {
            const sectionId = e.target.value;
            if (!sectionId) {
                ui.sectionSubjectChecklist.innerHTML = '<p>Please select a section first.</p>';
                return;
            }
            try {
                const response = await fetch(`/api/section/${sectionId}/subjects`);
                if (!response.ok) throw new Error('Failed to fetch subjects for section.');
                const assignedSubjectIds = await response.json();
                renderSubjectChecklist(assignedSubjectIds);
            } catch (error) {
                console.error(error);
                ui.sectionSubjectChecklist.innerHTML = `<p class="error-cell">${error.message}</p>`;
            }
        });
    }

    if (ui.btnSaveSectionSubjects) {
        ui.btnSaveSectionSubjects.addEventListener('click', async () => {
            const sectionId = ui.sectionSubjectSelect.value;
            if (!sectionId) {
                alert('Please select a section before saving.');
                return;
            }

            const selectedSubjectIds = Array.from(ui.sectionSubjectChecklist.querySelectorAll('input:checked'))
                .map(input => parseInt(input.value));

            try {
                await postData(`/api/section/${sectionId}/subjects`, selectedSubjectIds);
                alert('Subject assignments saved successfully!');
            } catch (error) {
                alert(`Error saving subject assignments: ${error.message}`);
            }
        });
    }

    // --- Summary Tab Logic ---

    const renderWorkloadTable = (workload) => {
        const tbody = document.querySelector('#summary-teacher-workload tbody');
        if (!tbody) return;
        tbody.innerHTML = ''; // Clear existing rows
        workload.forEach(item => {
            const row = `<tr><td>${item.teacher_name}</td><td>${item.assigned_periods}</td></tr>`;
            tbody.innerHTML += row;
        });
    };

    const renderAnalysisTable = (analysis) => {
        const tbody = document.querySelector('#summary-subject-analysis tbody');
        if (!tbody) return;
        tbody.innerHTML = ''; // Clear existing rows
        analysis.forEach(item => {
            let statusClass = '';
            if (item.status === 'Shortage') statusClass = 'status-shortage';
            else if (item.status === 'Surplus') statusClass = 'status-surplus';
            const row = `<tr>
                <td>${item.subject_name}</td>
                <td>${item.required_periods}</td>
                <td>${item.available_teachers}</td>
                <td class="${statusClass}">${item.status}</td>
            </tr>`;
            tbody.innerHTML += row;
        });
    };

    const loadSummaryData = async () => {
        console.log("Loading summary data...");
        try {
            const response = await fetch('/api/analytics/summary');
            if (!response.ok) throw new Error('Failed to fetch summary data.');
            const summaryData = await response.json();

            renderWorkloadTable(summaryData.teacher_workload);
            renderAnalysisTable(summaryData.subject_analysis);
        } catch (error) {
            console.error('Failed to load summary data:', error);
            // Optionally, display an error in the tables
            document.querySelector('#summary-teacher-workload tbody').innerHTML = `<tr><td colspan="2" class="error-cell">${error.message}</td></tr>`;
            document.querySelector('#summary-subject-analysis tbody').innerHTML = `<tr><td colspan="4" class="error-cell">${error.message}</td></tr>`;
        }
    };

    // --- Teacher Assignment Logic ---

    const createCourseRow = (assignment = {}) => {
        const row = document.createElement('div');
        row.className = 'assignment-row';

        const subjectId = assignment.subject_id || '';
        const sectionId = assignment.section_id || '';
        const periods = assignment.periods_per_week || 1;

        // 1. Subject Dropdown
        const subjectSelect = document.createElement('select');
        subjectSelect.className = 'assignment-subject-select';
        let subjectOptions = '<option value="">-- Select Subject --</option>';
        allData.subjects.forEach(s => {
            subjectOptions += `<option value="${s.id}" ${s.id === subjectId ? 'selected' : ''}>${s.name}</option>`;
        });
        subjectSelect.innerHTML = subjectOptions;

        // 2. Section Dropdown
        const sectionSelect = document.createElement('select');
        sectionSelect.className = 'assignment-section-select';
        let sectionOptions = '<option value="">-- Select Section --</option>';
        allData.sections.forEach(s => {
            sectionOptions += `<option value="${s.id}" ${s.id === sectionId ? 'selected' : ''}>${s.grade_name} - ${s.name}</option>`;
        });
        sectionSelect.innerHTML = sectionOptions;

        // 3. Periods Input
        const periodsInput = document.createElement('input');
        periodsInput.type = 'number';
        periodsInput.className = 'assignment-periods-input';
        periodsInput.value = periods;
        periodsInput.min = 1;

        // 4. Remove Button
        const removeBtn = document.createElement('button');
        removeBtn.textContent = 'Remove';
        removeBtn.className = 'btn-remove-assignment';
        removeBtn.onclick = () => row.remove();

        // Add cascading dropdown logic
        sectionSelect.addEventListener('change', () => {
            const selectedSectionId = sectionSelect.value;
            const validSubjectIds = new Set(allData.section_subject_map[selectedSectionId] || []);

            // Preserve the currently selected subject if it's still valid
            const currentSubjectId = subjectSelect.value;

            let subjectOptions = '<option value="">-- Select Subject --</option>';
            allData.subjects.forEach(s => {
                if (validSubjectIds.has(s.id)) {
                    subjectOptions += `<option value="${s.id}">${s.name}</option>`;
                }
            });
            subjectSelect.innerHTML = subjectOptions;

            // Restore selection if possible
            if (validSubjectIds.has(parseInt(currentSubjectId))) {
                subjectSelect.value = currentSubjectId;
            }
        });

        row.append(subjectSelect, sectionSelect, periodsInput, removeBtn);

        // Trigger the change event on initial render to populate subjects correctly
        sectionSelect.dispatchEvent(new Event('change'));

        return row;
    };

    const renderCourseAssignments = (assignments = []) => {
        ui.subjectAssignmentContainer.innerHTML = '';
        if (assignments.length === 0) {
            ui.subjectAssignmentContainer.appendChild(createCourseRow());
        } else {
            assignments.forEach(assignment => {
                ui.subjectAssignmentContainer.appendChild(createCourseRow(assignment));
            });
        }
    };

    const renderPreferences = (preferences = []) => {
        ui.preferencesContainer.innerHTML = '';
        const preferencesMap = new Map(preferences.map(p => [p.timeslot_id, p.preference_type]));

        const days = (allData.config && allData.config.work_days) ? allData.config.work_days.split(',') : ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
        const periods = (allData.config && allData.config.periods_per_day) ? parseInt(allData.config.periods_per_day) : 8;

        const grid = document.createElement('div');
        grid.className = 'preferences-grid';
        grid.style.gridTemplateColumns = `100px repeat(${days.length}, 1fr)`;

        // 1. Header Row (Days)
        let headerHtml = '<div class="pref-grid-cell period-label"></div>'; // Empty corner
        days.forEach(day => {
            headerHtml += `<div class="pref-grid-cell day-label">${day}</div>`;
        });
        grid.innerHTML = headerHtml;

        // 2. Map timeslots for easy lookup
        const timeslotMap = {};
        if (allData.timeslots) {
            allData.timeslots.forEach(t => {
                if (!timeslotMap[t.period_number]) timeslotMap[t.period_number] = {};
                timeslotMap[t.period_number][t.day_of_week] = t.id;
            });
        }

        // 3. Period Rows
        for (let p = 1; p <= periods; p++) {
            const row = document.createElement('div');
            row.className = 'pref-grid-row';
            row.innerHTML += `<div class="pref-grid-cell period-label">Period ${p}</div>`;

            days.forEach(day => {
                const timeslotId = timeslotMap[p] ? timeslotMap[p][day] : null;
                const cell = document.createElement('div');
                cell.className = 'pref-grid-cell';
                if (timeslotId) {
                    const currentPref = preferencesMap.get(timeslotId) || 'neutral';
                    cell.dataset.timeslotId = timeslotId;

                    const isDesirable = currentPref === 'desirable';
                    const isUndesirable = currentPref === 'undesirable';

                    cell.innerHTML = `
                        <button data-pref-type="desirable" class="pref-btn ${isDesirable ? 'active' : ''}" title="Desirable">D</button>
                        <button data-pref-type="undesirable" class="pref-btn ${isUndesirable ? 'active' : ''}" title="Undesirable">U</button>
                    `;
                }
                row.appendChild(cell);
            });
            grid.appendChild(row);
        }

        ui.preferencesContainer.appendChild(grid);

        grid.addEventListener('click', (e) => {
            if (e.target.matches('.pref-btn')) {
                const btn = e.target;
                const currentCell = btn.parentElement;
                if (btn.classList.contains('active')) {
                    btn.classList.remove('active');
                } else {
                    const otherBtn = currentCell.querySelector(`.pref-btn:not([data-pref-type="${btn.dataset.prefType}"])`);
                    if (otherBtn) otherBtn.classList.remove('active');
                    btn.classList.add('active');
                }
            }
        });
    };

    const handleTeacherSelection = async (teacherId) => {
        if (!teacherId) {
            ui.teacherAssignmentDetails.classList.add('hidden');
            return;
        }
        console.log(`Fetching assignments for teacher ID: ${teacherId}`);
        try {
            const response = await fetch(`/api/teacher/${teacherId}/assignments`);
            if (!response.ok) throw new Error('Failed to fetch teacher assignments.');

            const data = await response.json();
            console.log('Received teacher assignment data:', data);

            renderCourseAssignments(data.assignments);
            renderPreferences(data.preferences);

            ui.teacherAssignmentDetails.classList.remove('hidden');
        } catch (error) {
            console.error(error);
            alert('Could not load teacher assignment details. Please try again.');
            ui.teacherAssignmentDetails.classList.add('hidden');
        }
    };

    if (ui.assignmentTeacherSelect) {
        ui.assignmentTeacherSelect.addEventListener('change', (e) => {
            handleTeacherSelection(e.target.value);
        });
    }

    if (ui.btnAddSubjectAssignment) {
        ui.btnAddSubjectAssignment.textContent = 'Add Assignment'; // Update button text
        ui.btnAddSubjectAssignment.addEventListener('click', () => {
            ui.subjectAssignmentContainer.appendChild(createCourseRow());
        });
    }

    if (ui.btnSaveTeacherAssignments) {
        ui.btnSaveTeacherAssignments.addEventListener('click', async () => {
            const teacherId = ui.assignmentTeacherSelect.value;
            if (!teacherId) {
                alert('Please select a teacher first.');
                return;
            }

            const assignments = [];
            document.querySelectorAll('.assignment-row').forEach(row => {
                const subjectSelect = row.querySelector('.assignment-subject-select');
                const sectionSelect = row.querySelector('.assignment-section-select');
                const periodsInput = row.querySelector('.assignment-periods-input');

                // Only include complete rows
                if (subjectSelect.value && sectionSelect.value && periodsInput.value) {
                    assignments.push({
                        subject_id: parseInt(subjectSelect.value),
                        section_id: parseInt(sectionSelect.value),
                        periods_per_week: parseInt(periodsInput.value)
                    });
                }
            });

            const preferences = [];
            document.querySelectorAll('.preferences-grid .pref-grid-cell').forEach(cell => {
                const activeBtn = cell.querySelector('.pref-btn.active');
                if (activeBtn) {
                    preferences.push({
                        timeslot_id: parseInt(cell.dataset.timeslotId),
                        preference_type: activeBtn.dataset.prefType,
                        subject_id: null // Subject-specific preferences can be added later
                    });
                }
            });

            const payload = { assignments, preferences };
            console.log('Saving teacher assignments:', payload);

            try {
                await postData(`/api/teacher/${teacherId}/assignments`, payload);
                alert('Teacher assignments saved successfully!');
            } catch (error) {
                alert(`Error saving assignments: ${error.message}`);
            }
        });
    }

    const steps = document.querySelectorAll('.wizard-step');
    const indicators = document.querySelectorAll('.step-indicator');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const finishBtn = document.getElementById('finish-btn');
    let currentStep = 0;

    const updateWizard = () => {
        steps.forEach((step, index) => step.classList.toggle('active', index === currentStep));
        indicators.forEach((indicator, index) => indicator.classList.toggle('active', index === currentStep));

        // If the new summary tab is active, fetch its data
        if (currentStep === 5) { // Step 6 is at index 5
            loadSummaryData();
        }

        prevBtn.style.display = currentStep === 0 ? 'none' : 'inline-block';
        nextBtn.style.display = currentStep === steps.length - 1 ? 'none' : 'inline-block';
        finishBtn.style.display = currentStep === steps.length - 1 ? 'inline-block' : 'none';
    };

    indicators.forEach(indicator => {
        indicator.addEventListener('click', () => {
            const stepNumber = parseInt(indicator.dataset.step);
            currentStep = stepNumber - 1;
            updateWizard();
        });
    });

    nextBtn.addEventListener('click', () => { if (currentStep < steps.length - 1) { currentStep++; updateWizard(); } });
    prevBtn.addEventListener('click', () => { if (currentStep > 0) { currentStep--; updateWizard(); } });
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
        const originalSchedule = JSON.parse(timetableGrid.dataset.originalSchedule || '[]');
        const selectedOption = viewValueSelect.options[viewValueSelect.selectedIndex];
        timetableTitle.textContent = viewId ? `Timetable for ${selectedOption.textContent}` : 'Full Timetable';
        renderTimetable(originalSchedule, allData, viewType, viewId);
    };

    viewTypeSelect.addEventListener('change', () => {
        updateViewValueOptions();
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
            // Reload all data from the server to ensure the UI reflects the latest config
            await loadInitialState();
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

    // --- Configuration ---
    console.log("Configuration received by renderTimetable:", allData.config);
    const days = (allData.config && allData.config.work_days)
        ? allData.config.work_days.split(',')
        : ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const periods = (allData.config && allData.config.periods_per_day)
        ? parseInt(allData.config.periods_per_day)
        : 8;
    console.log("Effective days:", days);
    console.log("Effective periods:", periods);

    // --- Grid Header ---
    let gridHtml = '<div class="grid-header">Day</div>';
    for (let p = 1; p <= periods; p++) {
        gridHtml += `<div class="grid-header">Period ${p}</div>`;
    }

    // --- Timeslot Mapping ---
    const timeslotMap = {};
    if (allData.timeslots) {
        allData.timeslots.forEach(t => {
            if (!timeslotMap[t.day_of_week]) timeslotMap[t.day_of_week] = {};
            timeslotMap[t.day_of_week][t.period_number] = t.id;
        });
    }

    // --- Grid Body ---
    for (const day of days) {
        gridHtml += `<div class="grid-cell day-label">${day}</div>`;
        for (let p = 1; p <= periods; p++) {
            const timeslotId = timeslotMap[day] ? timeslotMap[day][p] || '' : '';
            gridHtml += `<div class="grid-cell" data-timeslot-id="${timeslotId}"></div>`;
        }
    }
    timetableGrid.innerHTML = gridHtml;
    timetableGrid.style.gridTemplateColumns = `120px repeat(${periods}, 1fr)`;

    // --- Filtering Logic ---
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

    // --- Lesson Placement ---
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
