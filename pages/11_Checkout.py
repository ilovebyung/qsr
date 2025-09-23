import streamlit as st
import pandas as pd
from utils.util import format_price, calculate_split_amounts 
from utils.database import get_db_connection
from utils.style import load_css 

# # Get available service areas
# def get_available_service_areas():
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     cursor.execute("""
#         SELECT DISTINCT oc.service_area_id
#         FROM Order_Cart oc 
#         WHERE oc.order_status IN (1, 2) 
#         ORDER BY oc.service_area_id
#     """)
    
#     results = cursor.fetchall()
#     conn.close()
#     return [row['service_area_id'] for row in results]

# Get order details
def get_order_details():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get orders for the selected service area with status 10
    cursor.execute("""
        SELECT 
            oc.order_id,
            -- oc.service_area_id,
            oc.subtotal,
            op.product_id,
            pi.description,
            op.modifier ,
            op.product_quantity,
            pi.price
        FROM Order_Cart oc
        LEFT JOIN Order_Product op ON oc.order_id = op.order_id
        LEFT JOIN Product pi ON op.product_id = pi.product_id
        WHERE oc.order_status = 10
        ORDER BY oc.order_id, pi.description
    """)
    
    results = cursor.fetchall()
    conn.close()
    return results

# Update order status and service area
# def settle_order(order_ids, total_charged, service_area_id):
def settle_order(order_ids, total_charged):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Update order status to 11 (settled) and set charged amount
        for order_id in order_ids:
            cursor.execute("""
                UPDATE Order_Cart 
                SET order_status = 11, charged = ?
                WHERE order_id = ?
            """, (total_charged, order_id))
        
        # # Update service area status to 0 (available)
        # cursor.execute("""
        #     UPDATE Service_Area 
        #     SET status = 0 
        #     WHERE service_area_id = ?
        # """, (service_area_id,))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error settling order: {e}")
        return False
    finally:
        conn.close()

# Handle calculator button clicks
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
        # Quick amount buttons
        amount = value[1:]
        st.session_state.amount_tendered = int(float(amount) * 100)

# Initialize session state
def initialize_session_state():
    if 'selected_service_area' not in st.session_state:
        st.session_state.selected_service_area = None
    if 'tips_amount' not in st.session_state:
        st.session_state.tips_amount = 0
    if 'amount_tendered' not in st.session_state:
        st.session_state.amount_tendered = 0
    if 'current_input' not in st.session_state:
        st.session_state.current_input = ""
    if 'split_count' not in st.session_state:
        st.session_state.split_count = 1

# Main checkout page
def show_checkout_page():
    st.set_page_config(
        page_title="Checkout",
        page_icon="💳",
        layout="wide"
    )
    load_css()
    initialize_session_state()

    st.title("💳 Checkout")
    st.markdown("---")

    # FOUR COLUMN LAYOUT
    col1, col2, col3, col4 = st.columns([2, 1.4, 1, 1])
    
    # COLUMN 1: SERVICE AREA DROPDOWN
    with col1:
        st.markdown("### Select Service Area")
        
        # # Get available service areas
        # available_areas = get_available_service_areas()
        
        # if not available_areas:
        #     st.error("No service areas with pending orders found.")
        #     return
        
        # # Service area dropdown
        # selected_area = st.selectbox(
        #     "Service Area ID:",
        #     options=[None] + available_areas,
        #     format_func=lambda x: "Select..." if x is None else str(x),
        #     key="service_area_dropdown"
        # )

        # Set selected_area 10 as default (if not set)
        selected_area = 10
        
        if selected_area:
            # st.session_state.selected_service_area = selected_area
            
            # Get order data only after service area is selected
            order_data = get_order_details()
            
            if not order_data:
                st.error("No confirmed orders found for this service area.")
                return
            
            # Process order data
            orders = {}
            subtotal = 0
            
            for row in order_data:
                order_id = row['order_id']
                if order_id not in orders:
                    orders[order_id] = []
                
                if row['product_id']:  # Check if product exists
                    orders[order_id].append({
                        'description': row['description'],
                        'modifier': row['modifier'],
                        'quantity': row['product_quantity'],
                        'price': row['price']
                    })
                    subtotal += row['price'] * row['product_quantity']
            
            # Display Order Cart
            st.markdown("---")

            # Header
            # st.subheader(f'Service Area: {selected_area}, Order: {", ".join(str(k) for k in orders.keys())}')
            st.subheader(f'Order: {", ".join(str(k) for k in orders.keys())}')

            # Prepare table data
            table_data = []

            for order_id, items in orders.items():
                for item in items:
                    description = item['description']
                    if item['modifier']:
                        description += f" ({item['modifier']})"
                    
                    quantity = item['quantity']
                    total_price = format_price(item['price'] * quantity)

                    table_data.append({
                        "Description": description,
                        "Quantity": quantity,
                        "Total": total_price
                    })

            # Create DataFrame
            df = pd.DataFrame(table_data)


            # Display as table
            st.table(df.set_index(df.columns[0]))
            # st.table(df)  # or use st.dataframe(df) for scrollable, sortable table
            
            ## Payment Section    
            # Constants
            TAX = 175  # $1.75
            
            payment_items = [
                ("Subtotal", subtotal),
                ("Tax", TAX),
                ("Tips", st.session_state.tips_amount)
            ]
            
            for label, amount in payment_items:
                st.markdown(f"""
                <div class="payment-row">
                    <span>{label}</span>
                    <span>{format_price(amount)}</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Tips Warning - Display if tips is larger than subtotal
            if st.session_state.tips_amount > subtotal:
                st.warning(f"⚠️ Warning:  Tips amount is larger than subtotal! ")
        else:
            st.info("Please select a service area to proceed with checkout.")
    
    # Only show remaining columns if service area is selected
    if st.session_state.selected_service_area and 'orders' in locals():
        # Calculate totals
        total_tips = st.session_state.tips_amount
        balance_due = subtotal + TAX + total_tips
        remaining_balance = balance_due - st.session_state.amount_tendered
        
        # COLUMN 2: NUMBER PAD
        with col2:
            # Balance Display
            st.markdown(f"""
            <div class="balance-header">Remaining Balance / Change Due</div>
            <div class="balance-amount">{format_price(remaining_balance)}</div>            
            """, unsafe_allow_html=True)
            
            # Display current input
            if st.session_state.current_input:
                st.markdown(f"**Current input:** ${st.session_state.current_input}")
            else:
                st.markdown(f"**Current input:** ${0}")

            st.markdown("### Number Pad")
            
            # Calculator Grid - 4x3 layout
            # Row 1
            calc_col1, calc_col2, calc_col3 = st.columns(3)
            with calc_col1:
                if st.button("7", key="calc_7", width='stretch'):
                    handle_calculator_input("7")
                    st.rerun()
            with calc_col2:
                if st.button("8", key="calc_8", width='stretch'):
                    handle_calculator_input("8")
                    st.rerun()
            with calc_col3:
                if st.button("9", key="calc_9", width='stretch'):
                    handle_calculator_input("9")
                    st.rerun()
            
            # Row 2
            calc_col1, calc_col2, calc_col3 = st.columns(3)
            with calc_col1:
                if st.button("4", key="calc_4", width='stretch'):
                    handle_calculator_input("4")
                    st.rerun()
            with calc_col2:
                if st.button("5", key="calc_5", width='stretch'):
                    handle_calculator_input("5")
                    st.rerun()
            with calc_col3:
                if st.button("6", key="calc_6", width='stretch'):
                    handle_calculator_input("6")
                    st.rerun()
            
            # Row 3
            calc_col1, calc_col2, calc_col3 = st.columns(3)
            with calc_col1:
                if st.button("1", key="calc_1", width='stretch'):
                    handle_calculator_input("1")
                    st.rerun()
            with calc_col2:
                if st.button("2", key="calc_2", width='stretch'):
                    handle_calculator_input("2")
                    st.rerun()
            with calc_col3:
                if st.button("3", key="calc_3", width='stretch'):
                    handle_calculator_input("3")
                    st.rerun()
            
            # Row 4
            calc_col1, calc_col2, calc_col3 = st.columns(3)
            with calc_col1:
                if st.button("0", key="calc_0", width='stretch'):
                    handle_calculator_input("0")
                    st.rerun()
            with calc_col2:
                if st.button(".", key="calc_.", width='stretch'):
                    handle_calculator_input(".")
                    st.rerun()
            with calc_col3:
                if st.button("Delete", key="calc_delete", width='stretch'):
                    handle_calculator_input("delete")
                    st.rerun()
            
            # Enter button
            if st.button("Enter", key="calc_enter", width='stretch', type="primary"):
                handle_calculator_input("enter")
                st.rerun()
        
        # COLUMN 3: PAYMENT & TIPS
        with col3:
            st.markdown("### Payment Type")
            
            # Payment type buttons
            if st.button("Credit", key="credit", width='stretch', type="secondary"):
                pass
            
            if st.button("Cash", key="cash", width='stretch', type="secondary"):
                pass
            
            st.markdown("---")
            
            # Tips buttons
            st.markdown("### Tips")
            if st.button("Tips", key="tips_button", width='stretch', type="secondary"):
                # Use current input as tips if available
                if st.session_state.current_input:
                    st.session_state.tips_amount = int(float(st.session_state.current_input) * 100)
                    st.session_state.current_input = ""
                    st.rerun()

            if st.button("Clear Tips", key="clear_tips_button", width='stretch', type="secondary"):
                st.session_state.tips_amount = 0
                st.rerun()
        
        # COLUMN 4: SPLIT & SETTLE
        with col4:
            # Split evenly section
            st.markdown("### Split Evenly")
            
            # Split counter controls
            split_col1, split_col2, split_col3 = st.columns([1, 2, 1])
            
            with split_col1:
                if st.button("➖", key="split_minus", width='stretch'):
                    if st.session_state.split_count > 1:
                        st.session_state.split_count -= 1
                        st.rerun()
            
            with split_col2:
                st.markdown(f"<div style='text-align: center; padding: 1.5rem; font-weight: bold; font-size: 18px;'>{st.session_state.split_count}</div>", unsafe_allow_html=True)

            with split_col3:
                if st.button("➕", key="split_plus", width='stretch'):
                    st.session_state.split_count += 1
                    st.rerun()
            
            # Calculate and display split amounts
            if st.session_state.split_count > 1:
                split_amounts = calculate_split_amounts(balance_due, st.session_state.split_count)
                st.markdown("**Split amounts:**")
                for i, amount in enumerate(split_amounts):
                    st.markdown(f"<div class='split-amount'>Person {i+1}: {format_price(amount)}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Settle Button
            if st.button("Settle", key="settle", width='stretch', type="primary"):
                # Calculate total charged (subtotal + tax + tips)
                total_charged = subtotal + TAX + total_tips
                
                if settle_order(list(orders.keys()), total_charged):
                    # Clear session state
                    # st.session_state.selected_service_area = None
                    st.session_state.tips_amount = 0
                    st.session_state.amount_tendered = 0
                    st.session_state.current_input = ""
                    st.session_state.split_count = 1
                    
                    st.success("Order settled successfully!")
                    st.switch_page("pages/10_Order.py")

# Run the page
if __name__ == "__main__":
    show_checkout_page()