function downloadReportCSV() {
    const reportDataElement = document.getElementById("reportData");

    if (!reportDataElement) {
        alert("Report data not found.");
        return;
    }

    const data = JSON.parse(reportDataElement.textContent);

    const rows = [
        ["Monthly Financial Report"],
        ["Month", data.month],
        ["Year", data.year],
        [],
        ["Total Income", data.totalIncome],
        ["Total Expenses", data.totalExpense],
        ["Balance", data.balance],
        ["Total Transactions", data.transactions]
    ];

    const csvContent = rows
        .map(row => row.join(","))
        .join("\n");

    const blob = new Blob([csvContent], {
        type: "text/csv;charset=utf-8;"
    });

    const link = document.createElement("a");
    const fileName = `financial_report_${data.month}_${data.year}.csv`;

    link.href = URL.createObjectURL(blob);
    link.download = fileName;
    link.click();

    URL.revokeObjectURL(link.href);
}