import sqlite3
import streamlit as st
import pandas as pd
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
    conn = sqlite3.connect('pos.database', detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def get_table_data(table_name):
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table_name} ORDER BY {table_name}_id ", conn)
            return df
    except Exception as e:
        st.error(f"Error fetching data from Table {table_name}: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

def add_item(table_name, item_value):
    """Inserts a new item into the specified generic table."""
    column_name = table_name
    try:
        with get_db_connection() as conn:
            conn.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (item_value,))
            conn.commit()
            st.success(f"Added new {table_name}: **{item_value}**")
    except sqlite3.IntegrityError:
        st.warning(f"Error: {item_value} already exists in {table_name}.")
    except Exception as e:
        st.error(f"Failed to add {table_name}. Error: {e}")
        
def update_row(table_name, row_id_col, row_data):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{col} = ?" for col in row_data.keys() if col != row_id_col])
            values = [row_data[col] for col in row_data.keys() if col != row_id_col]
            values.append(row_data[row_id_col])
            cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {row_id_col} = ?", values)
            conn.commit()
    except Exception as e:
        st.error(f"Error updating row in Table {table_name}: {e}")

def delete_row(table_name, row_id_col, row_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table_name} WHERE {row_id_col} = ?", (row_id,))
    except Exception as e:
        st.error(f"Error deleting row in Table {table_name}: {e}")