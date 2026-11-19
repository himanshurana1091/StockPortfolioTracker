
const form = document.getElementById("stockForm");

// Load dashboard
async function loadDashboard() {
    const response = await fetch("/api/summary");
    const data = await response.json();

    document.getElementById("investment").innerText =
        "₹" + data.total_investment.toFixed(2);

    document.getElementById("currentValue").innerText =
        "₹" + data.current_value.toFixed(2);

    const profitElement = document.getElementById("profit");

    profitElement.innerText =
        "₹" + data.profit_loss.toFixed(2);

    profitElement.style.color =
        data.profit_loss >= 0 ? "green" : "red";

    document.getElementById("totalStocks").innerText =
        data.total_stocks;
}


// Load stock table
async function loadStocks() {
    const response = await fetch("/api/stocks");
    const stocks = await response.json();

    const table = document.getElementById("stockTable");

    table.innerHTML = "";

    stocks.forEach(stock => {

        const row = document.createElement("tr");

        const values = [
            stock.name,
            stock.symbol,
            stock.quantity,
            "₹" + stock.buy_price.toFixed(2),
            "₹" + stock.current_price.toFixed(2),
            "₹" + stock.investment.toFixed(2),
            "₹" + stock.profit.toFixed(2)
        ];

        values.forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        const actionCell = document.createElement("td");

        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";
        deleteButton.className = "delete-btn";

        deleteButton.addEventListener("click", () => {
            deleteStock(stock.id);
        });

        actionCell.appendChild(deleteButton);
        row.appendChild(actionCell);

        table.appendChild(row);
    });
}


// Add stock
form.addEventListener("submit", async function(event) {

    event.preventDefault();

    const stock = {
        name: document.getElementById("name").value,
        symbol: document.getElementById("symbol").value,
        quantity: document.getElementById("quantity").value,
        buy_price: document.getElementById("buyPrice").value,
        current_price: document.getElementById("currentPrice").value
    };

    const response = await fetch("/api/stocks", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(stock)
    });

    const result = await response.json();

    if (!response.ok) {
        alert(result.error);
        return;
    }

    alert(result.message);

    form.reset();

    loadDashboard();
    loadStocks();
});


// Delete stock
async function deleteStock(id) {

    if (!confirm("Are you sure you want to delete this stock?")) {
        return;
    }

    const response = await fetch(`/api/stocks/${id}`, {
        method: "DELETE"
    });

    const result = await response.json();

    if (!response.ok) {
        alert(result.error);
        return;
    }

    alert(result.message);

    loadDashboard();
    loadStocks();
}


// Initial loading
loadDashboard();
loadStocks();
