console.log("expenses.js loaded");
function openDeleteModal(id, category, amount) {
    const modal = document.getElementById("deleteModal");
    const message = document.getElementById("deleteMessage");
    const confirmForm = document.getElementById("confirmDeleteForm");

   const currencySymbol = document.getElementById("currencySymbol").value;

message.innerHTML = `
    Are you sure you want to delete<br>
    <strong>${category}</strong><br>
    ${currencySymbol}${Number(amount).toFixed(2)}?
`;

    confirmForm.action = `/delete-expense/${id}`;
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


function openEditModal(id, amount, category, date, time, payment, notes) {
    document.getElementById("editExpenseForm").action = `/update-expense/${id}`;

    document.getElementById("editAmount").value = amount;
    document.getElementById("editCategory").value = category;
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
   SEARCH EXPENSES
========================== */

function filterExpenses() {

    const input = document
        .getElementById("expenseSearch")
        .value
        .toLowerCase();

    const expenses = document.querySelectorAll(".searchable-expense");

    expenses.forEach(expense => {

        const text = expense.innerText.toLowerCase();

        if (text.includes(input)) {
            expense.style.display = "";
        } else {
            expense.style.display = "none";
        }

    });

}

/* ==========================
   SORT EXPENSES
========================== */

function sortExpenses() {
    const sortValue = document.getElementById("expenseSort").value;
    const listCard = document.querySelector(".expense-list-card");
    const items = Array.from(document.querySelectorAll(".searchable-expense"));

    items.sort((a, b) => {
        const amountA = Number(a.dataset.amount);
        const amountB = Number(b.dataset.amount);

        const dateA = new Date(a.dataset.date);
        const dateB = new Date(b.dataset.date);

        if (sortValue === "highest") {
            return amountB - amountA;
        }

        if (sortValue === "lowest") {
            return amountA - amountB;
        }

        if (sortValue === "oldest") {
            return dateA - dateB;
        }

        return dateB - dateA;
    });

    items.forEach(item => listCard.appendChild(item));
}
