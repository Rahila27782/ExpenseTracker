function togglePassword(inputId, iconElement) {
    const passwordInput = document.getElementById(inputId);

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        iconElement.innerText = "visibility_off";
    } else {
        passwordInput.type = "password";
        iconElement.innerText = "visibility";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirmPassword");
    const registerBtn = document.querySelector(".register-btn");

    form.addEventListener("submit", function (event) {
        if (password.value !== confirmPassword.value) {
            event.preventDefault();
            alert("Passwords do not match.");
            return;
        }

        registerBtn.innerText = "Creating Account...";
        registerBtn.disabled = true;
    });
});