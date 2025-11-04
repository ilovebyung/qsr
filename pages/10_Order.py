import streamlit as st
from datetime import datetime
from utils.util import format_price
from utils.database import get_db_connection
from utils.style import load_css

# Initialize session state for cart
if 'cart' not in st.session_state:
    st.session_state.cart = []

if 'order_id' not in st.session_state:
    st.session_state.order_id = None

def get_category():
    """Get all categories"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, description FROM category ORDER BY category_id")
    groups = cursor.fetchall()
    conn.close()
    return groups

def get_product_items(group_id):
    """Get product items for a specific group"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT product_id, description, price 
        FROM Product
        WHERE category_id = ?
        ORDER BY product_id
    ''', (group_id,))
    items = cursor.fetchall()
    conn.close()
    return items

def get_modifier_group(product_id):
    """Get modifier groups and their modifiers for a specific product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            m.modifier_id,
            m.description,
            m.modifier_group_id,
            m.price,
            mg.description as group_description
        FROM Modifier m
        LEFT JOIN Modifier_Group mg ON m.modifier_group_id = mg.modifier_group_id
        WHERE m.product_id = ? AND m.status = 1
        ORDER BY m.modifier_group_id, m.modifier_id
    ''', (product_id,))
    modifiers = cursor.fetchall()
    conn.close()
    
    # Organize modifiers by group
    modifier_groups = {}
    for mod_id, description, group_id, price, group_desc in modifiers:
        if group_id not in modifier_groups:
            modifier_groups[group_id] = {
                'group_description': group_desc,
                'modifiers': []
            }
        modifier_groups[group_id]['modifiers'].append({
            'modifier_id': mod_id,
            'description': description,
            'price': price
        })
    return modifier_groups

def add_to_cart(product_id, product_name, price, modifiers):
    """Add item to cart or update quantity if already exists"""
    # Sort modifiers by modifier_id for consistent comparison
    sorted_modifiers = sorted(modifiers, key=lambda x: x['modifier_id']) if modifiers else []
    
    # Check if item with same product and modifiers already exists
    for item in st.session_state.cart:
        item_modifiers = sorted(item['modifiers'], key=lambda x: x['modifier_id']) if item['modifiers'] else []
        if item['product_id'] == product_id and item_modifiers == sorted_modifiers:
            item['quantity'] += 1
            return
    
    # Calculate total price including all modifier prices
    modifier_price = sum(mod['price'] for mod in modifiers) if modifiers else 0
    total_price = price + modifier_price
    
    # Add new item
    st.session_state.cart.append({
        'product_id': product_id,
        'product_name': product_name,
        'base_price': price,
        'price': total_price,
        'modifiers': sorted_modifiers,
        'quantity': 1
    })

def update_quantity(index, delta):
    """Update quantity of cart item"""
    if 0 <= index < len(st.session_state.cart):
        st.session_state.cart[index]['quantity'] += delta
        if st.session_state.cart[index]['quantity'] <= 0:
            st.session_state.cart.pop(index)

def calculate_subtotal():
    """Calculate cart subtotal"""
    return sum(item['price'] * item['quantity'] for item in st.session_state.cart)

def create_order():
    """Create order and insert into database"""
    if not st.session_state.cart:
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create order in Order_Cart
        cursor.execute('''
            INSERT INTO Order_Cart (service_area_id, order_status, note)
            VALUES (0, 10, ?)
        ''', (st.session_state.note,))
        order_id = cursor.lastrowid
        st.session_state.order_id = order_id
        
        # Insert items into Order_Product
        for item in st.session_state.cart:
            # Create comma-separated list of modifier IDs
            modifier_ids = ','.join(str(mod['modifier_id']) for mod in item['modifiers']) if item['modifiers'] else None
            
            cursor.execute('''
                INSERT INTO Order_Product (order_id, product_id, modifiers, product_quantity)
                VALUES (?, ?, ?, ?)
            ''', (order_id, item['product_id'], modifier_ids, item['quantity']))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error creating order: {e}")
        return False
    finally:
        conn.close()

def show_order_page():
    # Page layout
    st.set_page_config(
        page_title="Order Cart", 
        page_icon="🛒",
        layout="wide"
    )
    load_css()

    st.title("🛒 Order Cart")
    st.markdown("---")

    # Create two columns
    col_cart, col_menu = st.columns([1, 2])

    # Left column - Cart
    with col_cart:
        st.subheader("Order Cart")
        
        if st.session_state.cart:
            # Display cart items
            for i, item in enumerate(st.session_state.cart):
                with st.container():
                    cart_col1, cart_col2, cart_col3 = st.columns([3, 2, 2])
                    
                    with cart_col1:
                        st.write(f"**{item['product_name']}**")
                        st.caption(f"Base: {format_price(item['base_price'])}")
                        if item['modifiers']:
                            for modifier in item['modifiers']:
                                mod_price = f" (+{format_price(modifier['price'])})" if modifier['price'] > 0 else ""
                                st.caption(f"• {modifier['description']}{mod_price}")
                    
                    with cart_col2:
                        quantity_col1, quantity_col2, quantity_col3 = st.columns([1, 1, 1])
                        with quantity_col1:
                            if st.button("➖", key=f"dec_{i}", help="Decrease quantity"):
                                update_quantity(i, -1)
                                st.rerun()
                        with quantity_col2:
                            st.write(f"{item['quantity']}")
                        with quantity_col3:
                            if st.button("➕", key=f"inc_{i}", help="Increase quantity"):
                                update_quantity(i, 1)
                                st.rerun()
                    
                    with cart_col3:
                        st.write(format_price(item['price'] * item['quantity']))
                    
                    st.divider()
        else:
            st.info("Cart is empty")

        # Input field for note
        if 'note' not in st.session_state:
            st.session_state.note = ''   

        with st.popover("note"):
            # st.markdown("Is there any special request? 👋")
            st.session_state.note = st.text_input("Is there any special request? 👋")

        # Subtotal
        subtotal = calculate_subtotal()
        st.subheader(f"Subtotal: {format_price(subtotal)}")
        
        # Checkout button
        checkout_disabled = len(st.session_state.cart) == 0
        if st.button("Checkout", type="primary", use_container_width=False, disabled=checkout_disabled):
            if create_order():
                st.success("Order created successfully!")
                # Clear cart after successful order
                st.session_state.cart = []
                # Navigate to checkout
                st.switch_page("pages/11_Checkout.py")

    # Right column - Menu
    with col_menu:
        st.subheader("Menu")
        
        # Get product groups
        category = get_category()
        
        # Create tabs for product groups
        if category:
            group_names = [group[1] for group in category]
            tabs = st.tabs(group_names)
            
            for i, (group_id, group_name) in enumerate(category):
                with tabs[i]:
                    # Get product items for this group
                    product_items = get_product_items(group_id)
                    
                    # Display product items
                    for product_id, product_name, price in product_items:
                        with st.container():
                            st.write(f"**{product_name}** - {format_price(price)}")
                            
                            # Get modifier groups for this product
                            modifier_groups = get_modifier_group(product_id)
                            
                            # Display modifier groups
                            if modifier_groups:
                                for group_id, group_data in modifier_groups.items():
                                    group_desc = group_data['group_description'] or "Options"
                                    modifiers = group_data['modifiers']
                                    
                                    if group_id == 0:
                                        # Checkbox for group_id = 0 (multiple selection)
                                        st.write(f"*{group_desc}:*")
                                        for modifier in modifiers:
                                            mod_price = f" (+{format_price(modifier['price'])})" if modifier['price'] > 0 else ""
                                            checkbox_key = f"check_{product_id}_{modifier['modifier_id']}"
                                            st.checkbox(
                                                f"{modifier['description']}{mod_price}",
                                                key=checkbox_key
                                            )
                                    else:
                                        # Radio button for group_id != 0 (single selection)
                                        st.write(f"*{group_desc}:*")
                                        radio_options = ["None"] + [
                                            f"{mod['description']}" + (f" (+{format_price(mod['price'])})" if mod['price'] > 0 else "")
                                            for mod in modifiers
                                        ]
                                        radio_key = f"radio_{product_id}_{group_id}"
                                        st.radio(
                                            group_desc,
                                            radio_options,
                                            key=radio_key,
                                            label_visibility="collapsed"
                                        )
                            
                            # Add to cart button
                            if st.button("Add to Cart", key=f"add_{product_id}", type="secondary", use_container_width=False):
                                selected_modifiers = []
                                
                                # Collect selected modifiers
                                if modifier_groups:
                                    for group_id, group_data in modifier_groups.items():
                                        modifiers = group_data['modifiers']
                                        
                                        if group_id == 0:
                                            # Get checkbox selections (multiple modifiers)
                                            for modifier in modifiers:
                                                checkbox_key = f"check_{product_id}_{modifier['modifier_id']}"
                                                if st.session_state.get(checkbox_key, False):
                                                    selected_modifiers.append(modifier)
                                        else:
                                            # Get radio selection (single modifier per group)
                                            radio_key = f"radio_{product_id}_{group_id}"
                                            selected_option = st.session_state.get(radio_key, "None")
                                            if selected_option != "None":
                                                # Find the matching modifier
                                                for modifier in modifiers:
                                                    mod_label = f"{modifier['description']}" + (f" (+{format_price(modifier['price'])})" if modifier['price'] > 0 else "")
                                                    if selected_option == mod_label:
                                                        selected_modifiers.append(modifier)
                                                        break
                                
                                add_to_cart(product_id, product_name, price, selected_modifiers)
                                st.rerun()
                            
                            st.divider()

# Run the page
if __name__ == "__main__":
    show_order_page()