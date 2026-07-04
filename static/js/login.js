function togglePassword() {
    const passwordInput = document.getElementById("password");
    const eyeIcon = document.querySelector(".eye-icon");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        eyeIcon.innerText = "visibility_off";
    } else {
        passwordInput.type = "password";
        eyeIcon.innerText = "visibility";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const loginBtn = document.querySelector(".login-btn");

    form.addEventListener("submit", function () {
        loginBtn.innerText = "Logging in...";
        loginBtn.disabled = true;
    });
});