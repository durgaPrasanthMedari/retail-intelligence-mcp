import sqlite3

# Connect creates the file if it doesn't exist
conn = sqlite3.connect("retail.db")
cursor = conn.cursor()

# ── TABLE 1: Products ─────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    sku         TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    price       REAL NOT NULL,
    cost        REAL NOT NULL,
    total_units INTEGER NOT NULL,
    units_sold  INTEGER DEFAULT 0,
    stock       INTEGER NOT NULL
)
""")

# ── TABLE 2: Suppliers ────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS suppliers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    country     TEXT NOT NULL,
    lead_days   INTEGER NOT NULL,
    reliability TEXT NOT NULL
)
""")

# ── TABLE 3: Weekly sales ─────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS weekly_sales (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sku         TEXT NOT NULL,
    week        TEXT NOT NULL,
    units_sold  INTEGER NOT NULL,
    revenue     REAL NOT NULL
)
""")

# ── SAMPLE DATA: Products ─────────────────────────────
products = [
    ("WJ-001", "Winter Parka Navy",      "Outerwear", 299.0, 89.0,  120, 97,  23),
    ("WJ-002", "Winter Parka Black",     "Outerwear", 299.0, 89.0,  100, 41,  59),
    ("KN-001", "Merino Knit Camel",     "Knitwear",  149.0, 42.0,  200, 188, 12),
    ("KN-002", "Merino Knit Cream",     "Knitwear",  149.0, 42.0,  150, 62,  88),
    ("TR-001", "Slim Trouser Black",    "Trousers",  119.0, 31.0,  180, 162, 18),
    ("TR-002", "Slim Trouser Grey",     "Trousers",  119.0, 31.0,  160, 55,  105),
    ("AC-001", "Leather Belt Brown",    "Accessories",79.0, 18.0, 300, 274, 26),
    ("AC-002", "Wool Scarf Burgundy",   "Accessories",69.0, 15.0, 250, 48,  202),
    ("SH-001", "Chelsea Boot Black",    "Shoes",     249.0, 78.0,  90,  83,  7),
    ("SH-002", "Loafer Tan",           "Shoes",     219.0, 65.0,  80,  19,  61),
]
cursor.executemany(
    "INSERT OR REPLACE INTO products VALUES (?,?,?,?,?,?,?,?)",
    products
)

# ── SAMPLE DATA: Suppliers ────────────────────────────
suppliers = [
    ("Textil Milano SRL",  "Italy",   14, "Excellent"),
    ("Fabric House Porto", "Portugal",21, "Good"),
    ("AsiaTex Ltd",        "Vietnam", 45, "Average"),
    ("Leather Co Istanbul","Turkey",  18, "Good"),
]
cursor.executemany(
    "INSERT OR IGNORE INTO suppliers (name,country,lead_days,reliability) VALUES (?,?,?,?)",
    suppliers
)

# ── SAMPLE DATA: Weekly sales ─────────────────────────
weekly = [
    ("WJ-001","W48",12,3588.0), ("WJ-002","W48",4,1196.0),
    ("KN-001","W48",23,3427.0), ("KN-002","W48",6,894.0),
    ("TR-001","W48",18,2142.0), ("AC-001","W48",31,2449.0),
    ("SH-001","W48",9,2241.0),  ("AC-002","W48",5,345.0),
]
cursor.executemany(
    "INSERT OR IGNORE INTO weekly_sales (sku,week,units_sold,revenue) VALUES (?,?,?,?)",
    weekly
)

conn.commit()
conn.close()
print("retail.db created with products, suppliers and weekly sales data")