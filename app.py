
from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Database connection
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create database table
def create_table():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            buy_price REAL NOT NULL,
            current_price REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Get all stocks
@app.route("/api/stocks", methods=["GET"])
def get_stocks():
    conn = get_db()
    stocks = conn.execute("SELECT * FROM stocks").fetchall()
    conn.close()

    result = []

    for stock in stocks:
        result.append({
            "id": stock["id"],
            "name": stock["name"],
            "symbol": stock["symbol"],
            "quantity": stock["quantity"],
            "buy_price": stock["buy_price"],
            "current_price": stock["current_price"],
            "investment": stock["quantity"] * stock["buy_price"],
            "value": stock["quantity"] * stock["current_price"],
            "profit": stock["quantity"] *
                      (stock["current_price"] - stock["buy_price"])
        })

    return jsonify(result)


# Add new stock
@app.route("/api/stocks", methods=["POST"])
def add_stock():
    data = request.get_json()

    name = data.get("name")
    symbol = data.get("symbol")
    quantity = data.get("quantity")
    buy_price = data.get("buy_price")
    current_price = data.get("current_price")

    if not name or not symbol:
        return jsonify({"error": "Name and symbol are required"}), 400

    try:
        quantity = int(quantity)
        buy_price = float(buy_price)
        current_price = float(current_price)

        if quantity <= 0 or buy_price <= 0 or current_price <= 0:
            return jsonify({"error": "Values must be positive"}), 400

    except (TypeError, ValueError):
        return jsonify({"error": "Enter valid numeric values"}), 400

    conn = get_db()

    conn.execute("""
        INSERT INTO stocks
        (name, symbol, quantity, buy_price, current_price)
        VALUES (?, ?, ?, ?, ?)
    """, (name, symbol, quantity, buy_price, current_price))

    conn.commit()
    conn.close()

    return jsonify({"message": "Stock added successfully"})


# Delete stock
@app.route("/api/stocks/<int:stock_id>", methods=["DELETE"])
def delete_stock(stock_id):
    conn = get_db()

    cursor = conn.execute(
        "DELETE FROM stocks WHERE id = ?", (stock_id,)
    )

    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Stock not found"}), 404

    return jsonify({"message": "Stock deleted successfully"})


# Dashboard summary
@app.route("/api/summary", methods=["GET"])
def summary():
    conn = get_db()

    stocks = conn.execute("SELECT * FROM stocks").fetchall()
    conn.close()

    investment = sum(
        s["quantity"] * s["buy_price"] for s in stocks
    )

    value = sum(
        s["quantity"] * s["current_price"] for s in stocks
    )

    profit = value - investment

    return jsonify({
        "total_investment": investment,
        "current_value": value,
        "profit_loss": profit,
        "total_stocks": len(stocks)
    })


if __name__ == "__main__":
    create_table()
    app.run(debug=True)
