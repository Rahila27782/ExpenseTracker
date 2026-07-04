console.log("income.js loaded");

function openDeleteModal(id, source, amount) {
    const modal = document.getElementById("deleteModal");
    const message = document.getElementById("deleteMessage");
    const confirmBtn = document.getElementById("confirmDeleteBtn");

   const currencySymbol = document.getElementById("currencySymbol").value;

message.innerHTML = `
    Are you sure you want to delete<br>
    <strong>${source}</strong><br>
    ${currencySymbol}${Number(amount).toFixed(2)}?
`;

    confirmBtn.href = `/delete-income/${id}`;
    modal.style.display = "flex";
}

function closeDeleteModal() {
    document.getElementById("deleteModal").style.display = "none";
}

window.onclick = function(event) {
    const modal = document.getElementById("deleteModal");

    if (event.target === modal) {
        closeDeleteModal();
    }
};

function openEditModal(id, amount, source, date, time, payment, notes) {
    document.getElementById("editIncomeForm").action = `/update-income/${id}`;

    document.getElementById("editAmount").value = amount;
    document.getElementById("editSource").value = source;
    document.getElementById("editDate").value = date;
    document.getElementById("editTime").value = time;
    document.getElementById("editPayment").value = payment;
    document.getElementById("editNotes").value = notes;

    document.getElementById("editModal").style.display = "flex";
}

function closeEditModal() {
    document.getElementById("editModal").style.display = "none";
}

/* ==========================
   SEARCH INCOME
========================== */

function filterIncome() {

    const input = document
        .getElementById("incomeSearch")
        .value
        .toLowerCase();

    const incomes = document.querySelectorAll(".searchable-income");

    incomes.forEach(income => {

        const text = income.innerText.toLowerCase();

        if (text.includes(input)) {
            income.style.display = "";
        } else {
            income.style.display = "none";
        }

    });

}

function sortIncome() {
    const sortValue = document.getElementById("incomeSort").value;
    const listCard = document.querySelector(".income-list-card");
    const items = Array.from(document.querySelectorAll(".searchable-income"));

    items.sort((a, b) => {
        const amountA = Number(a.dataset.amount);
        const amountB = Number(b.dataset.amount);

        const dateA = new Date(a.dataset.date);
        const dateB = new Date(b.dataset.date);

        if (sortValue === "highest") return amountB - amountA;
        if (sortValue === "lowest") return amountA - amountB;
        if (sortValue === "oldest") return dateA - dateB;

        return dateB - dateA;
    });

    items.forEach(item => listCard.appendChild(item));
}