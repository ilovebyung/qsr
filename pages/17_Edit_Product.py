import streamlit as st
from utils.util import format_price
from utils.database import  get_db_connection 
from utils.style import load_css 
import streamlit as st
import sqlite3

# Assuming utils.database contains update_row, delete_row, and get_table_data
from utils.database import update_row, delete_row, get_table_data 

# Page configuration
st.set_page_config(page_title="Manage Product", page_icon="🛠️", layout="wide", initial_sidebar_state="collapsed")

# # Set page config
# st.set_page_config(page_title="Manage Product", page_icon="🧳", layout="wide")
# st.header("🛠️ Manage Product", divider='blue')

# --- Reusable Function for Table Management UI ---

def display_dashboard(table_name):
    """Renders the UI for selecting, editing, updating, and deleting rows in a given table."""
    st.subheader(f"Manage {table_name} Data")

    try:
        df = get_table_data(table_name)
        
        if df.empty:
            st.info(f"The '{table_name}' table is currently empty.")
            return

        # 1. Row Selection
        # Use a unique key for number input

        # 1. Row Selection
        # Use a unique key for number input
        col1, col2 = st.columns([1, 3])  # col1 is narrower
        with col1:
            # row_index = st.number_input("Select row index to edit", min_value=0, max_value=len(df)-1, step=1)
            # row_data = df.iloc[row_index].to_dict()

            # row_id_col = [col for col in df.columns if col.endswith("_id")][0]
            # edited_data = {}

        
            row_index = st.number_input(
                f"Select row index to edit/delete ({table_name})", 
                min_value=0, 
                max_value=len(df)-1, 
                step=1,
                key=f"{table_name}_row_index"
            )
        
        row_data = df.iloc[row_index].to_dict()
        
        # Determine the primary key column name (e.g., Product_id, Modifier_id)
        row_id_col = [col for col in df.columns if col.endswith("_id")][0]
        edited_data = {}

        st.markdown("##### Edit Data Fields")
        
        # 2. Input Fields (distributed across 4 columns)
        input_cols = st.columns(4)
        
        for i, (col, val) in enumerate(row_data.items()):
            with input_cols[i % 4]:
                # Use a unique key for text input
                input_key = f"{table_name}_{col}_{row_data[row_id_col]}"

                if col == "status":
                    # Special handling for 'status' column (assumed to be binary: 0 or 1)
                    # options = ['Active','Inactive']
                    options = [1,0]
                    try:
                        current_index = options.index(val)
                    except ValueError:
                        current_index = 0 # Default to 0 if value is unexpected
                        
                    edited_data[col] = st.selectbox(
                        f"{col}", 
                        options, 
                        index=current_index,
                        key=input_key
                    )
                else:
                    edited_data[col] = st.text_input(
                        f"{col}", 
                        str(val),
                        key=input_key
                    )

        st.markdown("---")
        
        # 3. Action Buttons
        button_cols = st.columns(4)
        
        with button_cols[0]:
            if st.button("Update", key=f"{table_name}_update_btn"):
                # Convert status back to integer if present and not already one
                if 'status' in edited_data:
                    edited_data['status'] = int(edited_data['status'])
                
                update_row(table_name, row_id_col, edited_data)
                st.success(f"Row {edited_data[row_id_col]} updated successfully! **Please refresh the page to see changes.**")
        
        with button_cols[1]:
            if st.button("Delete", key=f"{table_name}_delete_btn"):
                delete_row(table_name, row_id_col, edited_data[row_id_col])
                st.warning(f"Row {edited_data[row_id_col]} deleted successfully! **Please refresh the page to see changes.**")

        # 4. Full Table View
        st.subheader("Full Table View")
        st.dataframe(df, width='stretch')

    except sqlite3.OperationalError:
        st.warning(f"Table '{table_name}' does not exist. Ensure the database is initialized.")
    except IndexError:
        st.error(f"Error: Row index {row_index} out of bounds for table '{table_name}'.")
    except Exception as e:
        st.error(f"An unexpected error occurred in {table_name} management: {e}")
        


# Run the page
if __name__ == "__main__":

    # --- Main App Execution ---

    # Use st.expander to wrap both tables
    # with st.expander("Table Editor (Product & Modifier)", expanded=True):

    # Use st.tabs to separate the logic for Product and Modifier
    tab_Category, tab_Product, tab_Modifier = st.tabs(["🥪 Category ","🥪 Product ", "🧂 Modifier "])  #"🧂 Modifier Group ", 

    with tab_Category:
        display_dashboard("Category")

    with tab_Product:
        display_dashboard("Product")

    # with tab_Modifier_Group:
    #     display_dashboard("Modifier_Group")

    with tab_Modifier:
        display_dashboard("Modifier")