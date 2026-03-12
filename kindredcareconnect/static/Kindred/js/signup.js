document.addEventListener("DOMContentLoaded", function () {

    // Get form element
    const form = document.querySelector("form");

    // Get radio buttons for user type
    const senior = document.querySelector("#senior");
    const volunteer = document.querySelector("#volunteer");
    const careHome = document.querySelector("#care_home");

    // Get council field and input fields specific to user type
    const councilField = document.querySelector(".council-signup-field");
    const careHomeOnlyFields = document.querySelectorAll(".carehome-only-signup-fields");
    const seniorAndVolunteerFields = document.querySelectorAll(".seniors-and-volunteers-signup-fields");

    // Update form when user selects user type
    senior.addEventListener("change", showFields);
    volunteer.addEventListener("change", showFields);
    careHome.addEventListener("change", showFields);

    // Only show fields relevant to user type
    function showFields() {
        if (careHome.checked) {
            councilField.style.display = "block";
            for (const field of careHomeOnlyFields) {
                field.style.display = "block";
            }
            

            for (const field of seniorAndVolunteerFields) {
                field.style.display = "none";
            }

            toggleRequired(careHomeOnlyFields, true);
            toggleRequired(seniorAndVolunteerFields, false);
        }


        if (senior.checked || volunteer.checked) {
            councilField.style.display = "block";
            for (const field of seniorAndVolunteerFields) {
                field.style.display = "block";
            }

            for (const field of careHomeOnlyFields) {
                field.style.display = "none";
            }
            toggleRequired(seniorAndVolunteerFields, true);
            toggleRequired(careHomeOnlyFields, false);
        }
    }

    // Make all visible fields required
    function toggleRequired(fields, bool) {
        for (const field of fields) {
            let inputs = field.querySelectorAll("input");
            for (const input of inputs) {
                input.required = bool;
            }
        }
    }

    // Validate form inputs before submitting
    form.addEventListener("submit", function(e) {
        // Remove old errors and start fresh every time user tries to submit form
        const oldErrors = form.querySelectorAll(".error-message, .status-message");
        oldErrors.forEach(oldError => {
            oldError.remove();
        });

        let noErrors = true;

        // Make sure user selects a user type
        const userType = form.querySelector('input[name="usertype"]:checked');


        if (!userType) {
            noErrors = false;

            const container = document.querySelector("#usertype-sign-up");
            const error = document.createElement("p");
            error.innerHTML = "Please select a user type.";
            error.classList.add("error-message");
            container.append(error);

            // Add status message for users with screen readers
            const status = document.createElement("div");
            status.innerHTML = "Please select a user type."
            status.classList.add("status-message");
            status.setAttribute("role", "status");
            status.setAttribute("aria-atomic", "true");
            container.append(status);


        }

        const requiredInputs = form.querySelectorAll("input");

        for (const input of requiredInputs) {
            if (!input.required) {
                continue;
            }

            // Add error message for empty inputs
            if (input.value.trim() === "") {

                noErrors = false;

                input.classList.add("bad-input");

                const error = document.createElement("p");
                error.innerHTML = "This field is required.";
                error.classList.add("error-message");
                input.parentElement.append(error);

                // Add status message for users with screen readers
                const status = document.createElement("div");
                status.innerHTML = "This field is required."
                status.classList.add("status-message");
                status.setAttribute("role", "status");
                status.setAttribute("aria-atomic", "true");
                input.parentElement.append(status);

            } else {
                input.classList.remove("bad-input");
            }
        }

        // Check to see if a username already exists
        if (usernameStatus.innerHTML === "Username is already taken.") {
            noErrors = false;
        }

        // Check to see if email is a valid email
        const email = document.querySelector("#email");
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailPattern.test(email.value)) {
            noErrors = false;

            const error = document.createElement("p");
            error.innerHTML = "Please enter a valid e-mail address.";
            error.classList.add("error-message");
            email.parentElement.append(error);

            // Add status message for users with screen readers
            const status = document.createElement("div");
            status.innerHTML = "Please enter a valid e-mail address.";
            status.classList.add("status-message");
            status.setAttribute("role", "status");
            status.setAttribute("aria-atomic", "true");
            email.parentElement.append(status);
        }


        // Check password strength and that passwords match
        const password = document.querySelector("#password");
        const confirmPassword = document.querySelector("#confirm_password");

        // At least 8 characters long with 1 capital letter, 1 number, and 1 special character
        const passwordPattern = /^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*()_\-+=\[\]{}|;:'",.<>\/?]).{8,}$/;

        if (!passwordPattern.test(password.value)) {
            noErrors = false;

            const error = document.createElement("p");
            error.innerHTML = "Your password must be at least 8 characters long with 1 capital letter, 1 number, and 1 special character.";
            error.classList.add("error-message");
            password.parentElement.append(error);

            // Add status message for users with screen readers
            const status = document.createElement("div");
            status.innerHTML = "Your password must be at least 8 characters long with 1 capital letter, 1 number, and 1 special character.";
            status.classList.add("status-message");
            status.setAttribute("role", "status");
            status.setAttribute("aria-atomic", "true");
            password.parentElement.append(status);
        }

        if (confirmPassword.value !== password.value) {
            noErrors = false;

            const error = document.createElement("p");
            error.innerHTML = "Passwords do not match.";
            error.classList.add("error-message");
            confirmPassword.parentElement.append(error);

            // Add status message for users with screen readers
            const status = document.createElement("div");
            status.innerHTML = "Passwords do not match.";
            status.classList.add("status-message");
            status.setAttribute("role", "status");
            status.setAttribute("aria-atomic", "true");
            confirmPassword.parentElement.append(status);

        }

        // Make sure user selects a gender
        if (senior.checked || volunteer.checked) {
            const gender = form.querySelector('input[name="gender"]:checked');

            if (!gender) {
                noErrors = false;

                const container = document.querySelector(".seniors-and-volunteers-signup-fields");
                const error = document.createElement("p");
                error.innerHTML = "Please select a gender.";
                error.classList.add("error-message");
                container.append(error);

                // Add status message for users with screen readers
                const status = document.createElement("div");
                status.innerHTML = "Please select a gender.";
                status.classList.add("status-message");
                status.setAttribute("role", "status");
                status.setAttribute("aria-atomic", "true");
                container.append(status);
            }
        }

        if (noErrors === false) {
            e.preventDefault(); // stop form submission
        }
    });

    // AJAX to check if username exists as user types it
    const usernameInput = document.querySelector("#username");
    const usernameStatus = document.querySelector("#username-status");

    usernameInput.addEventListener("keyup", function() {
        const username = usernameInput.value.trim();

        fetch(`/kindred/check-username-exists/?username=${username}`)
            .then(response => response.json())
            .then(data => {

                if (data.available) {
                    usernameStatus.innerHTML = "Username is available.";
                    usernameStatus.style.color = "green";
                } else {
                    usernameStatus.innerHTML = "Username is already taken.";
                    usernameStatus.style.color = "red";
                }
            })
    })

    // --- NEW ROLE SELECTION LOGIC ---
    // 1. Get role from URL (e.g., ?role=senior)
    const urlParams = new URLSearchParams(window.location.search);
    const roleParam = urlParams.get('role');

    if (roleParam) {
        // 2. Find the specific radio button
        const targetRadio = document.querySelector(`input[name="usertype"][value="${roleParam}"]`);
        
        if (targetRadio) {
            targetRadio.checked = true;
            // 3. Manually call the teammate's function to reveal the fields
            showFields(); 
        }
    }

});