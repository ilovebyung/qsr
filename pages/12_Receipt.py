import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from utils.util import format_price
from utils.database import get_db_connection
from utils.style import load_css

def get_order_details():
    """Get all orders with status 10 (pending)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            oc.order_id,
            oc.note,
            oc.subtotal,
            op.product_id,
            op.modifiers,
            pi.description as product_description,
            op.product_quantity,
            pi.price as product_price
        FROM Order_Cart oc
        LEFT JOIN Order_Product op ON oc.order_id = op.order_id
        LEFT JOIN Product pi ON op.product_id = pi.product_id
        WHERE oc.order_status = 10
        ORDER BY oc.order_id, pi.description
    """)
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_modifiers_details(modifier_ids_str):
    """Get modifier details from comma-separated IDs"""
    if not modifier_ids_str:
        return []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    modifier_ids = modifier_ids_str.split(',')
    placeholders = ','.join(['?' for _ in modifier_ids])
    
    cursor.execute(f"""
        SELECT 
            modifier_id,
            description,
            price
        FROM Modifier
        WHERE modifier_id IN ({placeholders})
        AND status = 1
    """, modifier_ids)
    
    modifiers = cursor.fetchall()
    conn.close()
    
    return [{'modifier_id': m[0], 'description': m[1], 'price': m[2]} for m in modifiers]

def show_orders_page():
    """Display all pending orders"""
    st.set_page_config(
        page_title="Orders Display",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    load_css()
    
    # Auto-refresh every 10 seconds
    st_autorefresh(interval=10 * 1000, limit=None, key="refresh")
    
    # st.title("📋 Orders Display")
    # st.markdown("Live view of all pending orders (auto-refreshes every 10 seconds)")
    # st.markdown("---")
    
    # Get order data
    order_data = get_order_details()
    
    if not order_data:
        st.info("No pending orders")
        return
    
    # Process orders
    orders = {}
    
    for row in order_data:
        order_id = row['order_id']
        if order_id not in orders:
            orders[order_id] = {
                'note': row['note'],
                'items': [],
                'subtotal': 0
            }
        
        if row['product_id']:
            # Get modifiers for this product
            modifiers = get_modifiers_details(row['modifiers'])
            
            # Calculate total modifier price
            modifier_total_price = sum(mod['price'] for mod in modifiers)
            
            # Item total = (product price + all modifier prices) * quantity
            item_total = (row['product_price'] + modifier_total_price) * row['product_quantity']
            
            orders[order_id]['items'].append({
                'description': row['product_description'],
                'quantity': row['product_quantity'],
                'base_price': row['product_price'],
                'modifiers': modifiers,
                'modifier_total': modifier_total_price,
                'item_total': item_total
            })
            
            orders[order_id]['subtotal'] += item_total
    
    # # Display summary metrics
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.metric("Total Orders", len(orders))
    # with col2:
    #     total_revenue = sum(order['subtotal'] for order in orders.values())
    #     st.metric("Total Revenue", format_price(total_revenue))
    
    # st.markdown("---")
    
    # Display each order
    for order_id, order_data in orders.items():
        with st.container():
            
            # Order items table
            table_data = []
            for item in order_data['items']:
                # Main product row
                description = item['description']
                
                # Add modifiers to description if present
                if item['modifiers']:
                    modifier_text = ", ".join([
                        f"{mod['description']}" + (f" (+{format_price(mod['price'])})" if mod['price'] > 0 else "")
                        for mod in item['modifiers']
                    ])
                    description += f"\n  └─ {modifier_text}"
                
                table_data.append({
                    "Item": description,
                    "Qty": item['quantity'],
                    "Price": format_price(item['base_price'] + item['modifier_total']),
                    "Total": format_price(item['item_total'])
                })
            
            # Create and display DataFrame
            df = pd.DataFrame(table_data)
            df.reset_index(drop=True)
            st.table(df)
            
            # st.divider()

if __name__ == "__main__":
    show_orders_page()
    st.info(f"Showing receipt for pending orders only.")