let allActivities = [];

// Helper to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// --- GLOBAL LOGIC (Runs on every page) ---
document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Notification Mark as Read
    const notificationBell = document.getElementById('notificationDropdown');
    if (notificationBell) {
        notificationBell.addEventListener('show.bs.dropdown', function () {
            const badge = this.querySelector('.badge');
            if (badge && badge.style.display !== 'none') {
                fetch('/kindred/notifications/clear-history/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    if (response.ok) {
                        badge.style.display = 'none';
                    }
                })
                .catch(err => console.error("Notification update failed:", err));
            }
        });
    }

// Volunteer withdrawing logic 
let withdrawMatchId = null;
let withdrawActivityId = null;

// 1. Capture IDs when modal opens
document.addEventListener('show.bs.modal', function (event) {
    if (event.target.id === 'withdrawModal') {
        const button = event.relatedTarget;
        withdrawMatchId = button.dataset.matchId;
        withdrawActivityId = button.dataset.activityId;
    }
});

// 2. Handle the confirmation click
const confirmWithdrawBtn = document.getElementById('confirmWithdrawBtn');
if (confirmWithdrawBtn) {
    confirmWithdrawBtn.addEventListener('click', function() {
        const reason = document.getElementById('withdrawReason').value.trim();
        const url = withdrawMatchId ? `/kindred/withdraw-application/${withdrawMatchId}/` : `/kindred/withdraw-by-activity/${withdrawActivityId}/`;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ reason: reason }) // Send the custom reason
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();
            }
        });
    });
}

// Cancel form logic
const cancelModal = document.getElementById('cancelModal');
if (cancelModal) {
    cancelModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const matchId = button.getAttribute('data-match-id');
        const form = this.querySelector('#cancelForm');
        
        // Dynamically change the title based on which button was clicked
        const modalTitle = this.querySelector('.modal-title');
        if (button.innerText === "Decline") {
            modalTitle.innerText = "Decline Volunteer";
        } else {
            modalTitle.innerText = "Cancel Confirmed Plan";
        }

        form.action = `/kindred/remove-match/${matchId}/`;
    });
}

// redact button logic
let redactActivityId = null;
let redactCardElement = null;

const redactModal = document.getElementById('redactModal');
if (redactModal) {
    redactModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        redactActivityId = button.getAttribute('data-id');
        redactCardElement = button.closest('.card'); // Store the card to remove it later
    });
}

const confirmRedactBtn = document.getElementById('confirmRedactBtn');
if (confirmRedactBtn) {
    confirmRedactBtn.addEventListener('click', function() {
        if (!redactActivityId) return;

        // Get the value from the new textarea
        const reasonInput = document.getElementById('redactReason');
        const reason = reasonInput.value.trim() || ""; 

        fetch(`/kindred/redact-activity/${redactActivityId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json', // Required to send JSON
                'X-Requested-With': 'XMLHttpRequest'
            },
            // ADD THIS: Convert the reason into a JSON string to send to Django
            body: JSON.stringify({ reason: reason })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Hide modal
                const modalElement = document.getElementById('redactModal');
                const modalInstance = bootstrap.Modal.getInstance(modalElement);
                modalInstance.hide();
                
                // Clear the textarea for the next time the modal opens
                reasonInput.value = "";

                // --- UI UPDATES ---
                // 1. If on the Activities Browse Page:
                if (document.getElementById('available-activities-list')) {
                    fetchAndRenderActivities(); // Refresh the feed
                } 
                // 2. If on the Profile Page:
                else if (redactCardElement) {
                    redactCardElement.style.transition = 'all 0.3s ease';
                    redactCardElement.style.opacity = '0';
                    setTimeout(() => {
                        redactCardElement.remove();
                        // Check if no requests left to show empty state
                        if (document.querySelectorAll('#open-requests .card').length === 0) {
                            location.reload();
                        }
                    }, 300);
                }
            }
        })
        .catch(err => console.error("Redact failed:", err));
    });
}

// Logic for the 'Clear All' button inside the Notification Modal
const executeNotificationClear = document.getElementById('executeNotificationClear');
if (executeNotificationClear) {
    executeNotificationClear.addEventListener('click', function() {
        fetch('/kindred/notifications/clear-history/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        }).then(response => {
            if (response.ok) {
                // UI updates: Empty the dropdown and hide the badge
                const scrollContainer = document.querySelector('.notification-scroll');
                if (scrollContainer) {
                    scrollContainer.innerHTML = '<li class="text-center py-4 text-muted"><div class="mb-2 fs-3">🔔</div><p class="small mb-0">No new notifications</p></li>';
                }
                const badge = document.querySelector('#notificationDropdown .badge');
                if (badge) badge.style.display = 'none';
                
                // Close the modal using Bootstrap's API
                const modalElement = document.getElementById('confirmNotificationClear');
                const modalInstance = bootstrap.Modal.getInstance(modalElement);
                if (modalInstance) modalInstance.hide();
            }
        });
    });
}

// Logic for the Mark Complete Modal
const completeModal = document.getElementById('completeModal');
if (completeModal) {
    completeModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget; // Button that triggered the modal
        const matchId = button.getAttribute('data-match-id');
        const form = this.querySelector('#completeForm');
        
        // Update the form action URL dynamically
        form.action = `/kindred/complete-activity/${matchId}/`;
    });
}

// Confirm volunteer logic
// Variable to store the ID temporarily
let pendingActivityId = null;

// When the modal opens, store the ID and update the text
const confirmModal = document.getElementById('confirmVolunteerModal');
if (confirmModal) {
    confirmModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        pendingActivityId = button.getAttribute('data-id');
        const activityName = button.getAttribute('data-name');
        document.getElementById('volunteerModalTaskName').innerText = `Apply to help with: ${activityName}`;
   
        const act = allActivities.find(a => a.id == pendingActivityId);
        const reviewBtn = document.getElementById('reviewDetailsBtn');
        if (act && reviewBtn) {
            reviewBtn.setAttribute('data-name', act.activity_name || 'Activity Details');
            reviewBtn.setAttribute('data-category', act.category || 'General');
            reviewBtn.setAttribute('data-area', act.council_area || 'TBD');
            reviewBtn.setAttribute('data-date', (act.date + ' at ' + act.time) || 'Flexible');
            reviewBtn.setAttribute('data-desc', act.description || 'No additional details provided.');
        }
    });
}

// Handle the final click inside the modal
const finalJoinBtn = document.getElementById('finalJoinBtn');
if (finalJoinBtn) {
    finalJoinBtn.addEventListener('click', function() {
        if (!pendingActivityId) return;

        fetch(`/kindred/join-activity/${pendingActivityId}/`, {
            method: 'POST',
            headers: { 
                'X-CSRFToken': getCookie('csrftoken'), 
                'Content-Type': 'application/json' 
            }
        })
        .then(res => res.json())
        .then(data => { 
            if (data.status === 'success') {
                location.reload(); 
            } else if (data.status === 'error') {
                // Hide the confirmation modal first
                const confirmModal = bootstrap.Modal.getInstance(document.getElementById('confirmVolunteerModal'));
                confirmModal.hide();

                // Show the "Busy" modal
                const busyModal = new bootstrap.Modal(document.getElementById('busyModal'));
                busyModal.show();
            }
        });
    });
}

// Profile page Edit buttons
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('edit-btn')) {
        const activityId = e.target.dataset.id;
        const form = document.getElementById('editActivityForm');
        
        if (form) {
            form.action = `/kindred/edit-activity/${activityId}/`;
            
            // 1. Try to find data in allActivities (Activities Page)
            let act = allActivities.find(a => a.id == activityId);
            
            if (act) {
                // Populate using the API data
                document.getElementById('editName').value = act.activity_name;
                document.getElementById('editDate').value = act.date;
                document.getElementById('editTime').value = act.time;
                document.getElementById('editCategory').value = act.category.toLowerCase();
                document.getElementById('editCouncilArea').value = act.council_area;
            } else {
                // 2. Fallback: Populate using data attributes (Profile Page)
                document.getElementById('editName').value = e.target.dataset.name || '';
                document.getElementById('editDate').value = e.target.dataset.date || '';
                document.getElementById('editTime').value = e.target.dataset.time || '';
                
                const categorySelect = document.getElementById('editCategory');
                if (categorySelect) categorySelect.value = (e.target.dataset.category || '').toLowerCase();
                
                const areaSelect = document.getElementById('editCouncilArea');
                if (areaSelect) areaSelect.value = e.target.dataset.area || '';
            }
        }
    }
});

// Approve a volunteer confirmation logic
const approveModal = document.getElementById('confirmApproveModal');
if (approveModal) {
    approveModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const matchId = button.getAttribute('data-match-id');
        const volunteerName = button.getAttribute('data-volunteer-name');
        
        document.getElementById('approveVolunteerName').innerText = volunteerName;
        document.getElementById('approveForm').action = `/kindred/approve-match/${matchId}/`;
    });
}

document.addEventListener('click', function(e) {
    const userLink = e.target.closest('.view-user-link');
    if (userLink) {
        e.preventDefault();
        const userId = userLink.dataset.userId;
        
        fetch(`/kindred/api/user-profile/${userId}/`)
            .then(res => res.json())
            .then(data => {
                // 1. Update text fields
                document.getElementById('previewName').innerText = data.full_name;
                document.getElementById('previewBadge').innerText = data.usertype.charAt(0).toUpperCase() + data.usertype.slice(1);
                document.getElementById('previewLocation').innerText = data.council_area;
                document.getElementById('previewJoined').innerText = data.joined;

                // 2. NEW: Handle Profile Picture Logic
                const profileImg = document.getElementById('previewProfilePic');
                const defaultIcon = document.getElementById('previewDefaultIcon');

                if (data.profile_picture_url) {
                    // If the user has a photo, show the image and hide the icon
                    profileImg.src = data.profile_picture_url;
                    profileImg.classList.remove('d-none');
                    defaultIcon.classList.add('d-none');
                } else {
                    // If no photo exists, hide the image and show the default icon
                    profileImg.classList.add('d-none');
                    defaultIcon.classList.remove('d-none');
                }

                // 3. Handle Contact Info
                const contactSection = document.getElementById('contactInfoSection');
                if (data.email) {
                    contactSection.classList.remove('d-none');
                    document.getElementById('previewEmail').innerText = data.email;
                } else {
                    contactSection.classList.add('d-none');
                }

                // 4. Handle Address
                const addressSection = document.getElementById('addressSection');
                if (data.address) {
                    addressSection.classList.remove('d-none');
                    document.getElementById('previewAddress').innerText = data.address;
                } else {
                    addressSection.classList.add('d-none');
                }

                new bootstrap.Modal(document.getElementById('userPreviewModal')).show();
            });
    }
});



    // --- ACTIVITIES PAGE ONLY LOGIC ---
    const availableList = document.getElementById('available-activities-list');
    if (availableList) {
        fetchAndRenderActivities();
        setupActivityListeners();
    }
});

// --- ACTIVITY FUNCTIONS ---

async function fetchAndRenderActivities() {
    try {
        const response = await fetch('/kindred/api/activities/');
        allActivities = await response.json(); 
        renderWithData(allActivities); 
    } catch (error) {
        console.error("Error fetching activities:", error);
    }
}

function renderWithData(dataToRender) {
    const availableList = document.getElementById('available-activities-list');
    const container = document.getElementById('activity-page-container');
    if (!availableList || !container) return;

    const userRole = container.dataset.userRole || '';
    const currentUser = container.dataset.currentUser || '';
    const currentUserId = Number(container.dataset.userId) || null;

    availableList.innerHTML = dataToRender.map(act => {
        const isOwner = act.requester_username.toLowerCase() === currentUser.toLowerCase();
        
        // --- 1. CARE HOME LIST VIEW (Full Width Rows) ---
        if (userRole === 'care_home') {
            return `
            <div class="col-12 mb-3">
                <div class="card border-0 shadow-sm rounded-4 p-3 bg-white border-start border-4 ${isOwner ? 'border-emerald' : 'border-light'} interactive-card" 
                    data-id="${act.id}">
                    <div class="row align-items-center">
                        <div class="col-md-4">
                            <h5 class="fw-bold mb-1">${act.activity_name}</h5>
                            <small class="text-muted">
                                By ${isOwner ? '<span class="fw-bold text-emerald">You</span>' : 
                                `<a href="#" class="view-user-link text-emerald fw-bold text-decoration-none" data-user-id="${act.requester_id}">${act.requester_username}</a>`} 
                                | ${act.category}
                            </small>
                        </div>
                        <div class="col-md-3">
                            <span class="small d-block text-muted">Location</span>
                            <span class="small fw-medium">${act.council_area}</span>
                        </div>
                        <div class="col-md-2">
                            <span class="small d-block text-muted">Schedule</span>
                            <span class="small fw-medium">${act.date}</span>
                        </div>
                        <div class="col-md-3 text-end">
                            ${isOwner ? `
                                <button class="btn btn-light btn-sm rounded-pill border edit-btn" 
                                        data-id="${act.id}" data-bs-toggle="modal" data-bs-target="#editActivityModal">
                                    Edit
                                </button>
                                <button class="btn btn-danger btn-sm rounded-pill" 
                                        data-id="${act.id}" 
                                        data-bs-toggle="modal" 
                                        data-bs-target="#redactModal">
                                    Redact
                                </button>
                            ` : `
                                <button type="button" class="btn btn-outline-emerald py-2 fw-bold rounded-pill shadow-sm view-details-btn" 
                                        data-bs-toggle="modal" 
                                        data-bs-target="#activityDetailsModal"
                                        data-name="${act.activity_name}"
                                        data-category="${act.category}"
                                        data-area="${act.council_area}"
                                        data-date="${act.date} at ${act.time}"
                                        data-desc="${act.description || 'No additional details provided.'}">
                                    View Details
                                </button>
                            `}
                        </div>
                    </div>
                </div>
            </div>`;
        }

        // --- 2. VOLUNTEER & SENIOR CARD VIEW (2-Column Grid) ---
        const hasApplied = act.applied_volunteer_ids && act.applied_volunteer_ids.map(Number).includes(currentUserId);
        
        let actionButton = '';
        if (userRole === 'volunteer') {
            actionButton = hasApplied ? 
               `<div class="d-flex gap-2 mb-2">
                    <button class="btn btn-secondary py-2 fw-bold flex-grow-1 rounded-pill shadow-sm" style="font-size: 0.85rem;" disabled>Sent ✓</button>
                    <button class="btn btn-outline-danger py-2 fw-bold flex-grow-1 rounded-pill shadow-sm withdraw-app-btn" 
                            data-activity-id="${act.id}" 
                            data-bs-toggle="modal" 
                            data-bs-target="#withdrawModal"
                            style="font-size: 0.85rem;">
                        Withdraw
                    </button>
                </div>` : 
                `<button class="btn btn-emerald py-2 fw-bold w-100 rounded-pill shadow-sm mb-2" 
                        data-bs-toggle="modal" data-bs-target="#confirmVolunteerModal" 
                        data-id="${act.id}" data-name="${act.activity_name}">
                    Volunteer for this →
                </button>`;
        }

        return `
        <div class="col-lg-6">
            <div class="card border-0 shadow-sm rounded-4 p-4 h-100 interactive-card ${isOwner ? 'border-start border-4 border-emerald' : ''}" data-id="${act.id}">
                <div class="d-flex justify-content-between">
                    <h4 class="fw-bold mb-1">${act.activity_name}</h4>
                    ${isOwner ? '<span class="badge bg-emerald-light text-emerald rounded-pill px-3 shadow-sm d-inline-flex align-items-center justify-content-center" style="height: 24px; line-height: 1;">Your Listing</span>' : ''}
                </div>
                    <p class="text-muted small mb-4">
                        By ${isOwner ? '<span class="fw-bold text-emerald">You</span>' : 
                        `<a href="#" class="view-user-link text-emerald fw-bold text-decoration-none" data-user-id="${act.requester_id}">${act.requester_username}</a>`} 
                        | ${act.category} | ${act.council_area}
                    </p>
                <div class="d-grid gap-2 mt-auto">
                    ${isOwner ? `
                        <div class="d-flex gap-2">
                            <button class="btn btn-outline-secondary btn-sm flex-grow-1 rounded-pill px-3 py-2 edit-btn" 
                                    data-id="${act.id}" data-bs-toggle="modal" data-bs-target="#editActivityModal">Edit</button>
                            <button class="btn btn-outline-danger btn-sm flex-grow-1 px-3 py-2 redact-btn rounded-pill" 
                                    data-id="${act.id}" 
                                    data-bs-toggle="modal" 
                                    data-bs-target="#redactModal">
                                Redact
                            </button>
                        </div>
                    ` : `
                        ${actionButton}
                       <button type="button" class="btn btn-outline-emerald py-2 fw-bold rounded-pill shadow-sm view-details-btn" 
                               data-bs-toggle="modal" 
                               data-bs-target="#activityDetailsModal"
                               data-name="${act.activity_name}"
                               data-category="${act.category}"
                               data-area="${act.council_area}"
                               data-date="${act.date} at ${act.time}"
                               data-desc="${act.description || 'No additional details provided.'}">
                            View Details
                       </button>
                    `}
                </div>
            </div>
        </div>`;
    }).join('');
}

function setupActivityListeners() {
    // 1. Category Tabs
    document.querySelectorAll('.category-filter').forEach(card => {
        card.addEventListener('click', function() {
            document.querySelectorAll('.category-filter').forEach(c => c.classList.remove('active-category'));
            this.classList.add('active-category');
            const category = this.getAttribute('data-category');
            const filtered = category === 'all' ? allActivities : 
                allActivities.filter(act => act.category.toLowerCase() === category.toLowerCase());
            renderWithData(filtered);
        });
    });

    // 2. Category Dropdown
    const categoryDropdown = document.getElementById('category-dropdown');
    if (categoryDropdown) {
        categoryDropdown.addEventListener('change', (e) => {
            const category = e.target.value;
            const filtered = category === 'all' ? allActivities : 
                allActivities.filter(act => act.category.toLowerCase() === category.toLowerCase());
            renderWithData(filtered);
        });
    }

    // 3. Search
    const searchInput = document.getElementById('activity-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const results = allActivities.filter(act => 
                act.activity_name.toLowerCase().includes(term)
            );
            renderWithData(results);
        });
    }

    // 4. Consolidated Click Handler
    document.addEventListener('click', (e) => {
        const editBtn = e.target.closest('.edit-btn');
        const redactBtn = e.target.closest('.redact-btn');
        const viewBtn = e.target.closest('.view-details-btn');
        const card = e.target.closest('.interactive-card');
        const volunteerBtn = e.target.closest('[data-bs-target="#confirmVolunteerModal"]');

        if (editBtn || redactBtn || volunteerBtn) return; 

        if (card || viewBtn) {
            const activityId = card ? card.dataset.id : viewBtn.dataset.id;
            const act = allActivities.find(a => a.id == activityId);
            if (act) {
                console.log("Card clicked for activity:", act.activity_name);
            }
        }
    });
} // This brace correctly closes setupActivityListeners