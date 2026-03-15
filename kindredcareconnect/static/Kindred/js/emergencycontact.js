document.addEventListener("DOMContentLoaded", function() {
    // Get form element, add button, mobile field, and mobile error div
    const formDiv = document.querySelector("#emergency-contact-form");
    const form = document.querySelector("#emergency-contact-form form");
    const addButton = document.querySelector("#add-contact");
    const mobileField = document.querySelector("input[name='mobile']");
    const mobileError = document.querySelector("#mobile-error");

    // Regular expression for mobile number validation (11 digits)
    const mobilePattern = /^\d{11}$/;

    // Toggle form visibility when user clicks add button
    addButton.addEventListener("click", function () {
        if (formDiv.style.display == "none") {
            formDiv.style.display = "block";
            mobileError.style.display = "none";
        } else {
            formDiv.style.display = "none";
        }
    });

    // Stop the user from submitting if they provide an invalid phone number
    form.addEventListener("submit", function (event) {
        const mobileNumber = mobileField.value.trim();

        if (!mobilePattern.test(mobileNumber)) {
            event.preventDefault();
            mobileError.style.display = "block";
            mobileField.classList.add("bad-input");

            // For screen readers
            mobileField.setAttribute("aria-invalid", "true");
            mobileField.setAttribute("aria-describedby", "mobile-error");
            mobileField.focus();
        } else {
            mobileField.removeAttribute("aria-invalid");
            mobileField.removeAttribute("aria-describedby");
            mobileError.style.display = "none";
        }
    });

    // Remove error message when user starts typing
    mobileField.addEventListener("input", function () {
        mobileError.style.display = "none";
    });

});