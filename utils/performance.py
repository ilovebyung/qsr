import sqlite3, time

conn = sqlite3.connect("performance.db")
conn.execute('PRAGMA journal_mode=WAL;')  # Enable WAL mode
cur = conn.cursor()

start = time.time()

# Insert 1000 records
cur.execute("BEGIN")
for i in range(1000):
    cur.execute("""
        INSERT INTO Order_Cart (order_status, service_area_id, customer_id, subtotal, charged, special_request)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (0, (i % 8) + 1, None, 1000 + i * 10, 1100 + i * 10, f'Test order #{i+1}')
    )
conn.commit()

# Update 1000 records
cur.execute("BEGIN")
cur.execute("UPDATE Order_Cart SET order_status = 1 WHERE order_status = 0")
conn.commit()
cur.execute("select * from order_history order by timestamp;")

end = time.time()
print(f"Total time: {end - start:.4f} seconds")

