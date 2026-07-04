document.addEventListener("DOMContentLoaded", function () {
    setDefaultIncomeDateTime();
});

function setDefaultIncomeDateTime() {
    const params = new URLSearchParams(window.location.search);

    const selectedMonth = Number(params.get("month"));
    const selectedYear = Number(params.get("year"));

    const today = new Date();

    const currentMonth = today.getMonth() + 1;
    const currentYear = today.getFullYear();

    let date;

    if (selectedMonth && selectedYear) {
        if (selectedMonth === currentMonth && selectedYear === currentYear) {
            date = today.toISOString().split("T")[0];
        } else {
            const month = String(selectedMonth).padStart(2, "0");
            date = `${selectedYear}-${month}-01`;
        }
    } else {
        date = today.toISOString().split("T")[0];
    }

    const hours = String(today.getHours()).padStart(2, "0");
    const minutes = String(today.getMinutes()).padStart(2, "0");

    document.getElementById("incomeDate").value = date;
    document.getElementById("incomeTime").value = `${hours}:${minutes}`;
}