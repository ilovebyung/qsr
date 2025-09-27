import streamlit as st
import pandas as pd
import time
from utils.util import format_price
from utils.database import  get_db_connection 
from utils.style import load_css 
# from streamlit_autorefresh import st_autorefresh

# Initialize session state for checkbox tracking
def init_session_state():
    if 'item_states' not in st.session_state:
        st.session_state.item_states = {}

# Get all open orders (order_status = 1)
def get_open_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT 
            oc.order_id,
            oc.service_area_id,
            oc.order_status,
            oc.created_at
        FROM Order_Cart oc
        INNER JOIN Order_Product op ON oc.order_id = op.order_id
        WHERE oc.order_status = 1
        ORDER BY oc.created_at ASC
    """)
    
    orders = cursor.fetchall()
    conn.close()
    return orders

# Get order items for a specific order
def get_order_items(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            op.order_id,
            op.product_id,
            pi.description as product_name,
            op.option,
            op.product_quantity
        FROM Order_Product op
        INNER JOIN Product_Item pi ON op.product_id = pi.product_id
        INNER JOIN Order_Cart oc ON op.order_id = oc.order_id
        WHERE op.order_id = ? AND oc.order_status = 1
        ORDER BY pi.description
    """, (order_id,))
    
    items = cursor.fetchall()
    conn.close()
    return items

# Confirm order (set order_status to 2)
def confirm_order(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE Order_Cart 
            SET order_status = 2 
            WHERE order_id = ?
        """, (order_id,))
        
        conn.commit()
        # Clean up session state for this order
        keys_to_remove = [key for key in st.session_state.item_states.keys() if key.startswith(f"{order_id}_")]
        for key in keys_to_remove:
            del st.session_state.item_states[key]
        return True
    except Exception as e:
        st.error(f"Error confirming order: {e}")
        return False
    finally:
        conn.close()

# Create unique item key for session state
def create_item_key(order_id, product_id, option, index):
    return f"{order_id}_{product_id}_{option or 'none'}_{index}"

# Display order with checkboxes
def display_order_with_checkboxes(order, items):
    st.subheader(f'Service Area: {order["service_area_id"]}, Order: {order["order_id"]}')
    
    all_checked = True
    
    for i, item in enumerate(items):
        product_display = item['product_name']
        if item['option']:
            product_display += f" ({item['option']})"
        product_display += f" x {item['product_quantity']}"
        
        # Create unique key for this item
        item_key = create_item_key(order['order_id'], item['product_id'], item['option'], i)
        
        # Initialize checkbox state if not exists
        if item_key not in st.session_state.item_states:
            st.session_state.item_states[item_key] = False
        
        # Create checkbox and display item on the same line
        col1, col2 = st.columns([0.1, 0.9])
        
        with col1:
            is_checked = st.checkbox(
                label="",
                value=st.session_state.item_states[item_key],
                key=f"checkbox_{item_key}",
                label_visibility="collapsed"
            )
        
        with col2:
            # Update session state
            st.session_state.item_states[item_key] = is_checked
            
            # Display item with or without strikethrough
            if is_checked:
                st.markdown(f"~~{product_display}~~")
            else:
                st.write(f"{product_display}")
                all_checked = False
    
    # Show confirm button
    button_disabled = not all_checked
    button_text = "All items ready - Confirm Order" if all_checked else "Confirm Order"
    
    if st.button(button_text, key=f"confirm_{order['order_id']}", disabled=button_disabled, use_container_width=True):
        if confirm_order(order['order_id']):
            st.success(f"Order {order['order_id']} confirmed!")
            st.rerun()

# Main KDS page
def show_kds_page():
    st.set_page_config(
        page_title="Kitchen Display System",
        page_icon="🍳",
        layout="wide"
    )
    
    # Initialize session state
    init_session_state()
    
    load_css()
    
    st.title("🍳 Kitchen Display System")
    st.markdown("---")

    # Get open orders
    orders = get_open_orders()
    
    if not orders:
        st.subheader("""
                📋 No pending orders. All caught up! 🎉
            """)
        return
    
    # Display orders in three fixed columns
    cols = st.columns(3)
    
    for i, order in enumerate(orders):
        col_index = i % 3
        
        with cols[col_index]:
            # Get items for this order
            items = get_order_items(order['order_id'])
            
            if items:  # Only display if order has items
                display_order_with_checkboxes(order, items)
    
    st.markdown("---")
    st.write("Last updated:", time.strftime("%Y-%m-%d %H:%M:%S"))    

# Run the page
if __name__ == "__main__":
    # Note: The st_autorefresh function is set to refresh the page every 10 seconds to keep the KDS updated.
    # st_autorefresh(interval=10 * 1000, limit=None, key="refresh")
    show_kds_page()