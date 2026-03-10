let allActivities = []; // Global memory to store database results

// 1. Fetch Activities data from the database
async function fetchAndRenderActivities() {
    try {
        const response = await fetch('/kindred/api/activities/');
        allActivities = await response.json(); 
        
        // Initially show everything
        renderFilteredActivities('all'); 
    } catch (error) {
        console.error("Error fetching activities:", error);
    }
}

function renderFilteredActivities(category) {
    const list = document.getElementById('managed-activities-list');
    const availableList = document.getElementById('available-activities-list');

    // Grab the role from our new container
    const container = document.getElementById('activity-page-container');
    const userRole = container ? container.dataset.userRole : '';

    // Filter logic remains the same
    const filtered = category === 'all' 
        ? allActivities 
        : allActivities.filter(act => act.category.toLowerCase() === category.toLowerCase());

    // --- 1. HANDLE MANAGED LIST (Care Home View) ---
    if (list) {
        list.innerHTML = ''; 

        if (filtered.length === 0) {
            list.innerHTML = '<p class="text-muted text-center py-4">No activities found for this category.</p>';
        } else {
            filtered.forEach(act => {
                list.innerHTML += `
                    <div class="card border-0 shadow-sm rounded-4 safety-card mb-3">
                        <div class="card-body p-4">
                            <div class="row g-4 align-items-center text-center text-lg-start">
                                <div class="col-12 col-lg-4">
                                    <h5 class="fw-bold mb-1">${act.activity_name}</h5>
                                    <p class="text-muted smaller mb-0">${act.category}</p>
                                </div>
                                <div class="col-12 col-lg-6">
                                    <div class="row">
                                        <div class="col-4 border-end">
                                            <span class="text-muted smaller d-block">Location</span>
                                            <span class="small fw-medium">${act.council_area}</span>
                                        </div>
                                        <div class="col-4 border-end">
                                            <span class="text-muted smaller d-block">Date</span>
                                            <span class="small fw-medium">${act.date}</span>
                                        </div>
                                        <div class="col-4">
                                            <span class="text-muted smaller d-block">Time</span>
                                            <span class="small fw-medium">${act.time}</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-12 col-lg-2 d-flex justify-content-center justify-content-lg-end gap-2">
                                    <button class="btn btn-light btn-sm px-3 border shadow-sm">Edit</button>
                                    <button class="btn btn-danger btn-sm px-3 border-0 shadow-sm redact-pop">Redact</button>
                                </div>
                            </div>
                        </div>
                    </div>`;
            });
        }
    }

    // --- 2. HANDLE AVAILABLE LIST (Volunteer/Senior View) ---
    if (availableList) {
        if (filtered.length === 0) {
            availableList.innerHTML = '<p class="text-muted text-center py-4">No activities found for this category.</p>';
        } else {
            availableList.innerHTML = filtered.map(act => {
                // Set text and class based on the role we just grabbed
                    const isSenior = userRole === 'senior';
                    const btnText = isSenior ? 'JOIN ACTIVITY →' : 'Volunteer for this →';
                
                return `
                <div class="col-lg-6">
                    <div class="card border-0 shadow-sm rounded-4 safety-card p-4 h-100">
                        <div class="d-flex justify-content-between mb-3">
                            <h4 class="fw-bold mb-0">${act.activity_name}</h4>
                            <span class="small fw-bold text-emerald">⭐ 5.0</span>
                        </div>
                        <p class="text-muted small mb-4">${act.category} | ${act.council_area}</p>
                        <div class="d-grid gap-2">
                            <button class="btn btn-emerald py-2 fw-bold join-btn" data-id="${act.id}">
                                ${btnText}
                            </button>
                        </div>
                    </div>
                </div>
            `}).join('');
        }
    }
}

// Helper function to render a specific array of activities (for search bar)
function renderManualResults(dataArray) {
    const list = document.getElementById('managed-activities-list');
    const availableList = document.getElementById('available-activities-list');

    // Grab the role from our new container
    const container = document.getElementById('activity-page-container');
    const userRole = container ? container.dataset.userRole : '';

    // --- 1. Update Managed List (If user is a Care Home) ---
    if (list) {
        list.innerHTML = ''; 
        if (dataArray.length === 0) {
            list.innerHTML = '<p class="text-muted text-center py-4">No activities match your search.</p>';
        } else {
            dataArray.forEach(act => {
                list.innerHTML += `
                    <div class="card border-0 shadow-sm rounded-4 safety-card mb-3">
                        <div class="card-body p-4">
                            <div class="row align-items-center">
                                <div class="col-md-4">
                                    <h5 class="fw-bold mb-1">${act.activity_name}</h5>
                                    <p class="text-muted smaller mb-0">${act.category}</p>
                                </div>
                                <div class="col-md-2 text-center border-start">
                                    <span class="text-muted smaller d-block">Location</span>
                                    <span class="small fw-medium">${act.council_area}</span>
                                </div>
                                <div class="col-md-2 text-center border-start">
                                    <span class="text-muted smaller d-block">Date</span>
                                    <span class="small fw-medium">${act.date}</span>
                                </div>
                                <div class="col-md-4 d-flex justify-content-end gap-2">
                                    <button class="btn btn-light btn-sm px-3 border shadow-sm">Edit</button>
                                    <button class="btn btn-danger btn-sm px-3 border-0 shadow-sm redact-pop">Redact</button>
                                </div>
                            </div>
                        </div>
                    </div>`;
            });
        }
    }

    // --- 2. Update Available List (If user is a Volunteer/Senior) ---
    if (availableList) {
        availableList.innerHTML = '';
        if (dataArray.length === 0) {
            availableList.innerHTML = '<p class="text-muted text-center py-4">No activities match your search.</p>';
        } else {
            availableList.innerHTML = dataArray.map(act => {
                // Set text and class based on the role we just grabbed
                    const isSenior = userRole === 'senior';
                    const btnText = isSenior ? 'JOIN ACTIVITY →' : 'Volunteer for this →';
                
                return `
                <div class="col-lg-6">
                    <div class="card border-0 shadow-sm rounded-4 safety-card p-4 h-100">
                        <div class="d-flex justify-content-between mb-3">
                            <h4 class="fw-bold mb-0">${act.activity_name}</h4>
                            <span class="small fw-bold text-emerald">⭐ 5.0</span>
                        </div>
                        <p class="text-muted small mb-4">${act.category} | ${act.council_area}</p>
                        <div class="d-grid gap-2">
                            <button class="btn btn-emerald py-2 fw-bold join-btn" data-id="${act.id}">
                                ${btnText}
                            </button>
                        </div>
                    </div>
                </div>
            `}).join('');
        }
    }
}

// 3. Setup Button Listeners
document.querySelectorAll('.category-filter').forEach(card => {
    card.addEventListener('click', function() {
        // UI Highlight when clicked
        document.querySelectorAll('.category-filter').forEach(c => c.classList.remove('active-category'));
        this.classList.add('active-category');

        // Trigger filter when clicked
        const selected = this.getAttribute('data-category');
        renderFilteredActivities(selected);
    });
});

// Add an event listener to the search input
document.getElementById('activity-search').addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase(); // Get what user typed
    
    // Filter our global memory array
    const searchResults = allActivities.filter(act => {
        return act.activity_name.toLowerCase().includes(searchTerm); // || act.council_area.toLowerCase().includes(searchTerm)
    });

    // render when search bar recieves input
    renderManualResults(searchResults); // A helper function to display them
});

// Add listener to the dropdown
document.getElementById('category-dropdown').addEventListener('change', function(e) {
    const selectedCategory = e.target.value;
    renderFilteredActivities(selectedCategory); // call existing filter function when dropdown value changes
});

// 2. Join/Volunteer Logic Listener
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('join-btn')) {
        const activityId = e.target.getAttribute('data-id');
        
        // Simple alert for now to test if it's working!
        alert("Joining activity ID: " + activityId);
        
        // In the next step, we will replace this with a real database save
    }
});

// fetch data when page loads ( to be used for filter logic)
fetchAndRenderActivities();
