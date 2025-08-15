document.addEventListener('DOMContentLoaded', () => {
    const page = window.location.pathname;

    if (page.includes('/setup')) {
        initSetupWizard();
    } else if (page.includes('/dashboard')) {
        initDashboard();
    }
});

// --- Setup Wizard Logic ---
function initSetupWizard() {
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

    nextBtn.addEventListener('click', () => {
        if (currentStep < steps.length - 1) {
            currentStep++;
            updateWizard();
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentStep > 0) {
            currentStep--;
            updateWizard();
        }
    });

    // --- API Interactions ---
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

            if (!response.ok) {
                throw new Error('Failed to add teacher.');
            }

            const result = await response.json();
            console.log(result.message);

            // Add teacher to the UI
            const teacherElement = document.createElement('div');
            teacherElement.textContent = name;
            teachersList.appendChild(teacherElement);

            teacherNameInput.value = ''; // Clear input
        } catch (error) {
            console.error(error);
            alert(error.message);
        }
    });

    // Call once to initialize the view
    updateWizard();
    // TODO: Add similar form handlers for subjects, classrooms, etc.
    // TODO: Add a function to fetch all existing data on page load.
}

// --- Dashboard Logic ---
function initDashboard() {
    console.log('Dashboard initialized.');
    // TODO: Fetch current timetable data from /api/timetable
    // TODO: Implement function to render the timetable grid
    // TODO: Add event listeners for controls (Generate, Validate, etc.)
    // TODO: Implement view selector logic
    // TODO: Implement drag-and-drop for lessons
}
