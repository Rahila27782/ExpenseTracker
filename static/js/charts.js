document.addEventListener("DOMContentLoaded", function () {
    const chartDataElement = document.getElementById("chartData");

    if (!chartDataElement) {
        return;
    }

    const chartData = JSON.parse(chartDataElement.textContent);

    drawExpensePieChart(chartData);
    drawIncomeExpenseChart(chartData);
    animateCategoryBars();
});

function drawExpensePieChart(chartData) {
    const pieCanvas = document.getElementById("expensePieChart");

    if (!pieCanvas || chartData.categoryLabels.length === 0) {
        return;
    }

    new Chart(pieCanvas, {
        type: "pie",
        data: {
            labels: chartData.categoryLabels,
            datasets: [
                {
                    data: chartData.categoryAmounts,
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom"
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.label}: ${chartData.currencySymbol}${context.raw}`;
                        }
                    }
                }
            }
        }
    });
}

function drawIncomeExpenseChart(chartData) {
    const barCanvas = document.getElementById("incomeExpenseChart");

    if (!barCanvas) {
        return;
    }

    new Chart(barCanvas, {
        type: "bar",
        data: {
            labels: ["Income", "Expenses"],
            datasets: [
                {
                    label: "Amount",
                    data: [chartData.totalIncome, chartData.totalExpense],
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${chartData.currencySymbol}${context.raw}`;
                        }
                    }
                }
            }
        }
    });
}

function animateCategoryBars() {
    document.querySelectorAll(".bar-fill").forEach(function (bar) {
        const width = bar.getAttribute("data-width") || 0;

        setTimeout(function () {
            bar.style.width = `${width}%`;
        }, 200);
    });
}
