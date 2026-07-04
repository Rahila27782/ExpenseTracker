document.addEventListener("DOMContentLoaded", function () {
    animateBudgetProgress();
});

function animateBudgetProgress() {
    const progressFill = document.querySelector(".progress-fill");

    if (!progressFill) {
        return;
    }

    const actualPercent = Number(progressFill.getAttribute("data-width")) || 0;
    const displayPercent = Math.min(actualPercent, 100);

    if (actualPercent > 100) {
        progressFill.style.background = "linear-gradient(90deg,#E53935,#FF7043)";
    } else if (actualPercent >= 70) {
        progressFill.style.background = "linear-gradient(90deg,#F9A825,#FFCA28)";
    } else {
        progressFill.style.background = "linear-gradient(90deg,#4CAF50,#81C784)";
    }

    setTimeout(function () {
        progressFill.style.width = `${displayPercent}%`;
    }, 200);
}