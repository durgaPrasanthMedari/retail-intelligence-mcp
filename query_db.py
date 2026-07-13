import sqlite3
import json

# ── PATTERN 1: Connect and fetch all rows ─────────────
def get_all_products():
    conn = sqlite3.connect("retail.db")
    conn.row_factory = sqlite3.Row  # returns dict-like rows
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    # dict() converts Row to a real dictionary
    return [dict(row) for row in rows]

# ── PATTERN 2: Filter with WHERE clause ───────────────
def get_products_by_category(category: str):
    conn = sqlite3.connect("retail.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # ALWAYS use ? placeholders — never f-strings in SQL
    cursor.execute(
        "SELECT * FROM products WHERE category = ?",
        (category,)  # note: must be a tuple, even with 1 value
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ── PATTERN 3: Calculate in SQL ───────────────────────
def get_sell_through_report():
    conn = sqlite3.connect("retail.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            sku,
            name,
            category,
            units_sold,
            total_units,
            stock,
            ROUND(units_sold * 100.0 / total_units, 1) AS sell_through_pct,
            ROUND(price * stock, 2) AS stock_value_eur
        FROM products
        ORDER BY sell_through_pct DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ── PATTERN 4: Find underperformers ───────────────────
def get_underperformers(threshold: float = 50.0):
    conn = sqlite3.connect("retail.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sku, name, category,
               ROUND(units_sold * 100.0 / total_units, 1) AS sell_through_pct,
               stock AS units_remaining,
               ROUND(price * stock, 2) AS stock_value_at_risk
        FROM products
        WHERE (units_sold * 100.0 / total_units) < ?
        ORDER BY sell_through_pct ASC
    """, (threshold,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ── PATTERN 5: JOIN two tables ────────────────────────
def get_weekly_summary(week: str):
    conn = sqlite3.connect("retail.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ws.sku, p.name, p.category,
               ws.units_sold, ws.revenue,
               ROUND(ws.revenue / ws.units_sold, 2) AS avg_selling_price
        FROM weekly_sales ws
        JOIN products p ON ws.sku = p.sku
        WHERE ws.week = ?
        ORDER BY ws.revenue DESC
    """, (week,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ── PATTERN 6: Get top selling cities based on units sold ────────────────────────
DB_PATH = "merch_assistant.db"

def get_top_selling_cities(limit: int = 3):
    """Fetches the top selling cities based on total units sold from the sales table.
    Assumes your sales_history or a store table tracks city locations."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Adjust the table/column names if your schema uses 'store_city' or similar
        cursor.execute('''
            SELECT city, SUM(units_sold) as total_sales
            FROM sales_history
            GROUP BY city
            ORDER BY total_sales DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        # Return a list of city names: ['Milan', 'Paris', 'London']
        return [row[0] for row in rows] if rows else []
    except sqlite3.OperationalError:
        # Fallback in case your sales table doesn't have a city column yet
        return ["Milan", "Paris"]
    finally:
        conn.close()

# ── PATTERN 7: Add trends and logics to the table(runs only on user inputs not automatic) ──────────────────────── to be verified if should exists in query_db or create_db
DB_PATH = "merch_assistant.db"

def save_new_market_trend(trend_name: str, source: str, target_audience: str, description: str):
    """Saves an incoming market event or viral trend into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fashion_trends (
            trend_id INTEGER PRIMARY KEY AUTOINCREMENT,
            trend_name TEXT UNIQUE,
            source TEXT,
            target_audience TEXT,
            description TEXT,
            detected_date TEXT,
            status TEXT DEFAULT 'Active'
        )
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO fashion_trends (trend_name, source, target_audience, description, detected_date)
        VALUES (?, ?, ?, ?, DATE('now'))
    ''', (trend_name, source, target_audience, description))
    
    conn.commit()
    conn.close()

def match_trend_to_inventory(keywords: list):
    """Finds items in stock that could match a trending keyword."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    matches = []
    for word in keywords:
        cursor.execute('''
            SELECT product_id, name, category, stock_level, current_price 
            FROM inventory 
            WHERE name LIKE ? OR category LIKE ?
        ''', (f"%{word}%", f"%{word}%"))
        matches.extend(cursor.fetchall())
        
    conn.close()
    # Remove duplicates
    unique_matches = list(set(matches))
    return [
        {"id": m[0], "name": m[1], "category": m[2], "stock": m[3], "price": m[4]} 
        for m in unique_matches
    ]

# ── PATTERN 8: Catalogue scanning engine
import sqlite3

DB_PATH = "merch_assistant.db"

def proactive_catalog_match(keywords: list):
    """
    Scans the inventory database to check if existing catalog profiles 
    can satisfy a trending social media topic.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    matched_items = []
    for keyword in keywords:
        # Clean up punctuation and scan both names and high-level categories
        clean_word = f"%{keyword.strip().lower()}%"
        cursor.execute('''
            SELECT product_id, name, category, stock_level, current_price 
            FROM inventory 
            WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ?
        ''', (clean_word, clean_word))
        
        for row in cursor.fetchall():
            matched_items.append({
                "product_id": row[0],
                "name": row[1],
                "category": row[2],
                "stock_level": row[3],
                "price": row[4]
            })
            
    conn.close()
    
    # Deduplicate rows by product_id
    unique_matches = {item["product_id"]: item for item in matched_items}.values()
    return list(unique_matches)

# ── RUN ALL TESTS ─────────────────────────────────────
if __name__ == "__main__":
    print("=== ALL PRODUCTS ===")
    for p in get_all_products():
        print(f"  {p['sku']} | {p['name']} | €{p['price']}")

    print("\n=== KNITWEAR ONLY ===")
    for p in get_products_by_category("Knitwear"):
        print(f"  {p['name']} — stock: {p['stock']}")

    print("\n=== SELL-THROUGH REPORT ===")
    for p in get_sell_through_report():
        print(f"  {p['sku']} | {p['sell_through_pct']}% | stock value: €{p['stock_value_eur']}")

    print("\n=== UNDERPERFORMERS (below 50%) ===")
    for p in get_underperformers(50.0):
        print(f"  {p['sku']} | {p['sell_through_pct']}% | €{p['stock_value_at_risk']} at risk")

    print("\n=== WEEK 48 SALES ===")
    for p in get_weekly_summary("W48"):
        print(f"  {p['name']} | {p['units_sold']} units | €{p['revenue']}")