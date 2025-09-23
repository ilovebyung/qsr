import sqlite3
from datetime import date, datetime

# Adapter: Python date → ISO 8601 string
def adapt_date_iso(val):
    return val.isoformat()

# Converter: ISO 8601 string → Python date
def convert_date(val):
    return date.fromisoformat(val.decode())

# Register them
sqlite3.register_adapter(date, adapt_date_iso)
sqlite3.register_converter("date", convert_date)

# Connect with type detection enabled
def get_db_connection():
    conn = sqlite3.connect('pos.db', detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

