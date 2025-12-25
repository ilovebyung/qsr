import streamlit as st
import pandas as pd
from utils.util import format_price, save_receipt_to_file 
from utils.database import get_db_connection, get_order_details, get_modifiers_details
from utils.style import load_css 

st.set_page_config(page_title="Checkout",page_icon="💳",layout="wide",initial_sidebar_state="collapsed")
load_css()

def settle_order(order_ids, total):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for order_id in order_ids:
            cursor.execute("""
                UPDATE Order_Cart 
                SET order_status = 11, total = ?
                WHERE order_id = ?
            """, (total, order_id))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error settling order: {e}")
        return False
    finally:
        conn.close()

def handle_calculator_input(value):
    if value == "delete":
        st.session_state.current_input = st.session_state.current_input[:-1]
    elif value == "enter":
        if st.session_state.current_input:
            st.session_state.amount_tendered = int(float(st.session_state.current_input) * 100)
            st.session_state.current_input = ""
    elif value in [".", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        st.session_state.current_input += value
    elif value.startswith("$"):
        amount = value[1:]
        st.session_state.amount_tendered = int(float(amount) * 100)

def initialize_session_state():
    if 'selected_service_area' not in st.session_state:
        st.session_state.selected_service_area = 0
    if 'amount_tendered' not in st.session_state:
        st.session_state.amount_tendered = 0
    if 'current_input' not in st.session_state:
        st.session_state.current_input = ""
    if 'split_count' not in st.session_state:
        st.session_state.split_count = 1

def show_checkout_page():

    initialize_session_state()

    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        order_data = get_order_details()
       
        # Process order data with modifiers
        orders = {}
        subtotal = 0
        
        for row in order_data:
            order_id = row['order_id']
            if order_id not in orders:
                orders[order_id] = []
            
            if row['product_id']:
                # Get modifiers for this product
                modifiers = get_modifiers_details(row['modifiers'])
                
                # Calculate total modifier price
                modifier_total_price = sum(mod['price'] for mod in modifiers)
                
                # Item total = (product price + all modifier prices) * quantity
                item_total = (row['product_price'] + modifier_total_price) * row['product_quantity']
                
                orders[order_id].append({
                    'description': row['product_description'],
                    'quantity': row['product_quantity'],
                    'base_price': row['product_price'],
                    'modifiers': modifiers,
                    'modifier_total': modifier_total_price,
                    'item_total': item_total
                })
                
                subtotal += item_total
        
        st.subheader(f'Order: {", ".join(str(k) for k in orders.keys())}')

        # Prepare detailed table data
        table_data = []

        for order_id, items in orders.items():
            for item in items:
                # Main product row
                description = item['description']
                
                # Show modifiers in description if present
                if item['modifiers']:
                    modifier_text = ", ".join([
                        f"{mod['description']} (+{format_price(mod['price'])})" 
                        for mod in item['modifiers']
                    ])
                    description += f"\n  └─ {modifier_text}"
                
                table_data.append({
                    "Description": description,
                    "Quantity": item['quantity'],
                    "Price": format_price(item['base_price'] + item['modifier_total']),
                    "Total": format_price(item['item_total'])
                })

        # Create DataFrame
        df = pd.DataFrame(table_data)
        
        # Display as table
        st.table(df.set_index(df.columns[0]))
        
        # Payment Section    
        TAX = 175  # $1.75
        
        payment_items = [
            ("Subtotal", subtotal),
            ("Tax", TAX)
        ]
        
        for label, amount in payment_items:
            st.markdown(f"""
            <div class="payment-row">
                <span>{label}</span>
                <span>{format_price(amount)}</span>
            </div>
            """, unsafe_allow_html=True)
    
    if 'orders' in locals():
        balance_due = subtotal + TAX
        remaining_balance = balance_due - st.session_state.amount_tendered
        
        # COLUMN 2: NUMBER PAD
        with col2:
            st.markdown(f"""
            <div class="balance-header">Remaining Balance / Change Due</div>
            <div class="balance-amount">{format_price(remaining_balance)}</div>            
            """, unsafe_allow_html=True)
        
        # COLUMN 3: PAYMENT & SPLIT
        with col3:
            # st.markdown("### Payment Type")
            # Add a button to save receipt
            if st.button("Save Receipt"):
                if save_receipt_to_file(orders, subtotal, TAX):
                    st.success("Receipt saved to receipt.txt")
            
 

if __name__ == "__main__":
    show_checkout_page()