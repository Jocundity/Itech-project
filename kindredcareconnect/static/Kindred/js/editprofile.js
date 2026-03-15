document.addEventListener("DOMContentLoaded", function () {
    // Get form element
    const form = document.querySelector("#edit-profile-form");

    // Get user type and username divs and hide them when page loads
    const userTypeDiv = document.querySelector("#usertype-sign-up")
    userTypeDiv.style.display = "none";
    const usernameDiv = document.querySelector("#username-field");
    usernameDiv.style.display = "none";

    // Get council field and input fields specific to user type
    const councilField = document.querySelector(".council-signup-field");
    const careHomeOnlyFields = document.querySelectorAll(".carehome-only-signup-fields");
    const seniorAndVolunteerFields = document.querySelectorAll(".seniors-and-volunteers-signup-fields");

    // Update form fields based on user type
    const profileRole = userTypeDiv.dataset.role;

    if (profileRole == "care_home") {
        councilField.style.display = "block";
        careHomeOnlyFields.forEach((field) => field.style.display = "block");
        seniorAndVolunteerFields.forEach((field) => field.style.display = "none");
        toggleRequired(careHomeOnlyFields, true);
        toggleRequired(seniorAndVolunteerFields, false);
    } else {
        councilField.style.display = "block";
        seniorAndVolunteerFields.forEach((field) => field.style.display = "block");
        careHomeOnlyFields.forEach((field) => field.style.display = "none");
        toggleRequired(seniorAndVolunteerFields, true);
        toggleRequired(careHomeOnlyFields, false);
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
    form.addEventListener("submit", function (e) {
        // Remove old errors and start fresh every time user tries to submit form
        form.querySelectorAll(".error-message, .status-message").forEach((el) => el.remove());
        form.querySelectorAll(".bad-input").forEach((el) => el.classList.remove("bad-input"));
        
        let noErrors = true;

        const requiredInputs = form.querySelectorAll("input");

        for (const input of requiredInputs) {
            if (input.required && input.value.trim() === "") {
                noErrors = false;
                showError(input, "This field is required.")
            }
        }

        // Check to see if email is a valid email
        const email = document.querySelector("#email");
        const emailValue = email.value.trim();
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (emailValue === "" || !emailPattern.test(email.value)) {
            noErrors = false;
            showError(email, "Please enter a valid email.")
        }

        // Check password strength and that passwords match
        const password = document.querySelector("#password");
        const confirmPassword = document.querySelector("#confirm_password");

        // At least 8 characters long with 1 capital letter, 1 number, and 1 special character
        const passwordPattern = /^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*()_\-+=\[\]{}|;:'",.<>\/?]).{8,}$/;

       if (password && password.value.trim() !== "") {
           if (!passwordPattern.test(password.value)) {
               noErrors = false;
               showError(password, "Your password must be at least 8 characters long with 1 capital letter, 1 number, and 1 special character.");
           }

           if (confirmPassword.value.trim() === "") {
               noErrors = false;
               showError(confirmPassword, "Please confirm your password.");
           }

           else if (confirmPassword.value !== password.value) {
               noErrors = false;
               showError(confirmPassword, "Passwords do not match.");

           }
       }

        // Make sure user selects a gender
        if (profileRole === "senior" || profileRole === "volunteer") {
            const gender = form.querySelector('input[name="gender"]:checked');

            if (!gender) {
                noErrors = false;

                const container = document.querySelector(".seniors-and-volunteers-signup-fields");
                showError(container, "Please select a gender");   
            }
        }

        if (noErrors === false) {
            e.preventDefault(); // stop form submission
        }
    });

    function showError(element, message) {
        element.classList.add("bad-input");

        const error = document.createElement("p");
        error.innerHTML = message;
        error.classList.add("error-message");
        element.parentElement.append(error);

        // Add status message for users with screen readers
        const status = document.createElement("div");
        status.innerHTML = message;
        status.classList.add("status-message");
        status.setAttribute("role", "status");
        status.setAttribute("aria-atomic", "true");
        element.parentElement.append(status);
    }


});