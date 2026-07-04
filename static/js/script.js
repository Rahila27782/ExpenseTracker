/* ===========================================
   HOME DASHBOARD JAVASCRIPT
=========================================== */

let selectedMonth;
let selectedYear;
let tempMonth;
let tempYear;

const monthNames = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
];

document.addEventListener("DOMContentLoaded", function () {
    setGreeting();
    setCurrentMonthYear();
    generateYearList();
    setupMonthButtons();
    setupOutsideClick();
});

function setGreeting() {
    const hour = new Date().getHours();
    const greetingText = document.getElementById("greetingText");

    if (!greetingText) return;

    if (hour < 12) {
        greetingText.innerText = "Good Morning ☀️";
    } else if (hour < 17) {
        greetingText.innerText = "Good Afternoon 🌤️";
    } else {
        greetingText.innerText = "Good Evening 🌙";
    }
}

function setCurrentMonthYear() {
    const params = new URLSearchParams(window.location.search);
    const urlMonth = params.get("month");
    const urlYear = params.get("year");

    const today = new Date();

    selectedMonth = urlMonth ? Number(urlMonth) - 1 : today.getMonth();
    selectedYear = urlYear ? Number(urlYear) : today.getFullYear();

    tempMonth = selectedMonth;
    tempYear = selectedYear;

    updateDateText();
}

function updateDateText() {
    document.getElementById("selectedDateText").innerText =
        `📅 ${monthNames[selectedMonth]} ${selectedYear} ▼`;

    document.getElementById("modalDateTitle").innerText =
        `📅 ${monthNames[tempMonth]} ${tempYear}`;

    document.getElementById("modalYearText").innerText =
        `${tempYear} ▼`;

    highlightSelectedMonth();
}

function openDateModal() {
    tempMonth = selectedMonth;
    tempYear = selectedYear;

    document.getElementById("dateModal").style.display = "flex";
    document.getElementById("yearList").style.display = "none";
    document.getElementById("monthList").style.display = "grid";

    updateDateText();
    highlightSelectedYear();
}

function closeDateModal() {
    document.getElementById("dateModal").style.display = "none";
}

function generateYearList() {
    const yearList = document.getElementById("yearList");
    yearList.innerHTML = "";

    const currentYear = new Date().getFullYear();

    for (let year = currentYear - 10; year <= currentYear + 10; year++) {
        const btn = document.createElement("button");
        btn.innerText = year;

        btn.onclick = function () {
            tempYear = year;

            document.getElementById("modalYearText").innerText = `${tempYear} ▼`;
            document.getElementById("modalDateTitle").innerText =
                `📅 ${monthNames[tempMonth]} ${tempYear}`;

            highlightSelectedYear();
        };

        yearList.appendChild(btn);
    }
}

function toggleYearList() {
    const yearList = document.getElementById("yearList");
    const monthList = document.getElementById("monthList");

    if (yearList.style.display === "grid") {
        yearList.style.display = "none";
        monthList.style.display = "grid";
        document.getElementById("modalYearText").innerText = `${tempYear} ▼`;
    } else {
        yearList.style.display = "grid";
        monthList.style.display = "none";
        document.getElementById("modalYearText").innerText = `${tempYear} ▲`;
    }
}

function highlightSelectedYear() {
    document.querySelectorAll("#yearList button").forEach(btn => {
        btn.classList.remove("active-year");

        if (Number(btn.innerText) === tempYear) {
            btn.classList.add("active-year");
        }
    });
}

function setupMonthButtons() {
    document.querySelectorAll("#monthList button").forEach(button => {
        button.onclick = function () {
            tempMonth = Number(this.dataset.month);

            document.getElementById("modalDateTitle").innerText =
                `📅 ${monthNames[tempMonth]} ${tempYear}`;

            highlightSelectedMonth();
        };
    });
}

function highlightSelectedMonth() {
    document.querySelectorAll("#monthList button").forEach(button => {
        button.classList.remove("active-month");

        if (Number(button.dataset.month) === tempMonth) {
            button.classList.add("active-month");
        }
    });
}

function applyDateSelection() {
    selectedMonth = tempMonth;
    selectedYear = tempYear;

    const monthNumber = selectedMonth + 1;

    window.location.href = `/?month=${monthNumber}&year=${selectedYear}`;
}

function setupOutsideClick() {
    const modal = document.getElementById("dateModal");

    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeDateModal();
        }
    });
}

function openAddMenu() {
    const menu = document.getElementById("addMenu");

    menu.style.display = menu.style.display === "block" ? "none" : "block";
}

function openExpensesPage() {
    const monthNumber = selectedMonth + 1;
    window.location.href = `/expenses?month=${monthNumber}&year=${selectedYear}`;
}

function openIncomePage() {
    const monthNumber = selectedMonth + 1;
    window.location.href = `/income?month=${monthNumber}&year=${selectedYear}`;
}

function openBudgetPage() {
    const monthNumber = selectedMonth + 1;

    window.location.href =
        `/budget?month=${monthNumber}&year=${selectedYear}`;
}

function openAddExpensePage() {
    const monthNumber = selectedMonth + 1;
    window.location.href = `/add-expense?month=${monthNumber}&year=${selectedYear}`;
}

function openAddIncomePage() {
    const monthNumber = selectedMonth + 1;
    window.location.href = `/add-income?month=${monthNumber}&year=${selectedYear}`;
}


function openBalancePage() {
    const monthNumber = selectedMonth + 1;
    window.location.href = `/balance?month=${monthNumber}&year=${selectedYear}`;
}


function openChartsPage() {
    const monthNumber = selectedMonth + 1;

    window.location.href =
        `/charts?month=${monthNumber}&year=${selectedYear}`;
}





console.log("script.js loaded");

function openReportsPage() {
    const monthNumber = selectedMonth + 1;
    window.location.href = `/reports?month=${monthNumber}&year=${selectedYear}`;
}


function openProfilePage() {
    const monthNumber = selectedMonth + 1;

    window.location.href =
        `/profile?month=${monthNumber}&year=${selectedYear}`;
}


