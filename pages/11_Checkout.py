import streamlit as st
import pandas as pd
from utils.util import format_price, calculate_split_amounts 
from utils.database import get_db_connection
from utils.style import load_css 

# Get order details with modifiers
def get_order_details():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get orders with products and their modifiers
    cursor.execute("""
        SELECT 
            oc.order_id,
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

# Get modifier details for a list of modifier IDs
def get_modifiers_details(modifier_ids_str):
    """
    Parse modifier IDs string and fetch their details
    modifier_ids_str: "12,15,18" format
    Returns: list of dicts with modifier info
    """
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
    
    return [dict(mod) for mod in modifiers]

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
    st.set_page_config(
        page_title="Checkout",
        page_icon="💳",
        layout="wide"
    )
    load_css()
    initialize_session_state()

    # st.title("💳 Checkout")
    # st.markdown("---")

    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        order_data = get_order_details()
        
        if not order_data:
            st.switch_page("pages/10_Order.py")
        
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
            
            if st.session_state.current_input:
                st.markdown(f"**Current input:** ${st.session_state.current_input}")
            else:
                st.markdown(f"**Current input:** ${0}")

            st.markdown("### Number Pad")
            
            # Calculator Grid
            for row in [["7","8","9"], ["4","5","6"], ["1","2","3"]]:
                cols = st.columns(3)
                for i, num in enumerate(row):
                    with cols[i]:
                        if st.button(num, key=f"calc_{num}", use_container_width=True):
                            handle_calculator_input(num)
                            st.rerun()
            
            calc_col1, calc_col2, calc_col3 = st.columns(3)
            with calc_col1:
                if st.button("0", key="calc_0", use_container_width=True):
                    handle_calculator_input("0")
                    st.rerun()
            with calc_col2:
                if st.button(".", key="calc_.", use_container_width=True):
                    handle_calculator_input(".")
                    st.rerun()
            with calc_col3:
                if st.button("Delete", key="calc_delete", use_container_width=True):
                    handle_calculator_input("delete")
                    st.rerun()
            
            if st.button("Enter", key="calc_enter", use_container_width=True, type="primary"):
                handle_calculator_input("enter")
                st.rerun()
        
        # COLUMN 3: PAYMENT & SPLIT
        with col3:
            st.markdown("### Payment Type")
            
            if st.button("Credit", key="credit", use_container_width=True, type="secondary"):
                pass
            
            if st.button("Cash", key="cash", use_container_width=True, type="secondary"):
                pass
            
            st.markdown("---")
            
            # Split evenly section
            st.markdown("### Split Evenly")
            
            split_col1, split_col2, split_col3 = st.columns([1, 2, 1])
            
            with split_col1:
                if st.button("➖", key="split_minus", use_container_width=True):
                    if st.session_state.split_count > 1:
                        st.session_state.split_count -= 1
                        st.rerun()
            
            with split_col2:
                st.markdown(f"<div style='text-align: center; padding: 1.5rem; font-weight: bold; font-size: 18px;'>{st.session_state.split_count}</div>", unsafe_allow_html=True)

            with split_col3:
                if st.button("➕", key="split_plus", use_container_width=True):
                    st.session_state.split_count += 1
                    st.rerun()
            
            if st.session_state.split_count > 1:
                split_amounts = calculate_split_amounts(balance_due, st.session_state.split_count)
                st.markdown("**Split amounts:**")
                for i, amount in enumerate(split_amounts):
                    st.markdown(f"<div class='split-amount'>Person {i+1}: {format_price(amount)}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Settle Button
            if st.button("Settle", key="settle", use_container_width=True, type="primary"):
                total = subtotal + TAX
                
                if settle_order(list(orders.keys()), total):
                    st.session_state.amount_tendered = 0
                    st.session_state.current_input = ""
                    st.session_state.split_count = 1
                    
                    st.success("Order settled successfully!")
                    st.switch_page("pages/10_Order.py")

if __name__ == "__main__":
    show_checkout_page()