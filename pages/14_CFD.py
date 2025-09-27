import streamlit as st
import pandas as pd
import time
from utils.util import format_price
from utils.database import  get_db_connection 
from utils.style import load_css 
# from streamlit_autorefresh import st_autorefresh



# Get all open orders (order_status = 11)
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
        WHERE oc.order_status = 11 
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
            op.modifier as option,
            op.product_quantity
        FROM Order_Product op
        INNER JOIN Product pi ON op.product_id = pi.product_id
        INNER JOIN Order_Cart oc ON op.order_id = oc.order_id
        WHERE op.order_id = ? AND oc.order_status = 11
        ORDER BY pi.description
    """, (order_id,))
    
    items = cursor.fetchall()
    conn.close()
    return items

# Main KDS page
def show_kds_page():
    st.set_page_config(
        page_title="Customer-Facing Display",
        page_icon="🍳",
        layout="wide"
    )
    
    load_css()
    
    st.title("🍳 Customer-Facing Display")
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
                # display_order_card(order, items)
                st.subheader(f'Order: {order['order_id']}') 
                for item in items:
                    product_display = item['product_name']
                    if item['option']:
                        product_display += f" ({item['option']})"
                    st.write(f"- {product_display} x {item['product_quantity']}")

                # if st.button("Confirm", key=f"confirm_{order['order_id']}", width='stretch'):
                #     if confirm_order(order['order_id']):
                #         st.success(f"Order {order['order_id']} confirmed!")
                #         st.rerun()
    
    st.markdown("---")
    st.write("Last updated:", time.strftime("%Y-%m-%d %H:%M:%S"))    

# Run the page
if __name__ == "__main__":
    # Note: The st_autorefresh function is set to refresh the page every 10 seconds to keep the KDS updated.
    # st_autorefresh(interval=10 * 1000, limit=None, key="refresh")
    show_kds_page()

