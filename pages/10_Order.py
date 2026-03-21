import streamlit as st
from datetime import datetime
from utils.util import format_price
from utils.database import get_db_connection
from utils.style import load_css

# Page layout
st.set_page_config(page_title="Orders", page_icon="🗒", layout="wide", initial_sidebar_state="collapsed")
load_css()


# Initialize session state for cart
if 'cart' not in st.session_state:
    st.session_state.cart = []

if 'order_id' not in st.session_state:
    st.session_state.order_id = None

# --- Two-dialog state ---
# Confirmed non-type-1 selections: { modifier_id: { modifier_id, description, price, selected_item } }
if 'dialog_modifier_selections' not in st.session_state:
    st.session_state.dialog_modifier_selections = {}

# Set when a non-type-1 modifier button is clicked → triggers sub-dialog on next render
# { modifier_id, modifier_description, modifier_type_id, price }
if 'pending_sub_modifier' not in st.session_state:
    st.session_state.pending_sub_modifier = None

# Set to True after sub-dialog confirms → re-opens main dialog
if 'reopen_main_dialog' not in st.session_state:
    st.session_state.reopen_main_dialog = False

# --- Database Sync Logic for CFD ---

def sync_live_cart():
    """
    Flushes the Live_Cart table and inserts the current session's cart items 
    so the Customer Facing Display (CFD) can read it in real-time.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Flush the table for the new state
        cursor.execute("DELETE FROM Live_Cart")
        
        # Insert current cart items
        for item in st.session_state.cart:
            mod_text = ", ".join([m['description'] for m in item['modifiers']]) if item['modifiers'] else ""
            cursor.execute('''
                INSERT INTO Live_Cart (product_name, modifiers_text, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                item['product_name'], 
                mod_text, 
                item['quantity'], 
                item['price'], 
                item['price'] * item['quantity']
            ))
        
        conn.commit()
    except Exception as e:
        st.error(f"Error syncing to CFD: {e}")
    finally:
        conn.close()

def get_category():
    """Get all categories"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, description FROM category WHERE status = 1 ORDER BY category_id")
    groups = cursor.fetchall()
    conn.close()
    return groups

def get_products(group_id):
    """Get product items for a specific group"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT product_id, description, price 
        FROM Product
        WHERE category_id = ?
        ORDER BY rank
    ''', (group_id,))
    items = cursor.fetchall()
    conn.close()
    return items

def get_modifiers(product_id):
    """Get modifier groups and their modifiers for a specific product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            m.modifier_id,
            m.description,
            m.modifier_type_id,
            m.price,
            mt.description as group_description
        FROM Modifier m
        LEFT JOIN Modifier_Type mt ON m.modifier_type_id = mt.modifier_type_id
        WHERE m.product_id = ? AND m.status = 1
        ORDER BY m.modifier_type_id, m.modifier_id
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

def get_modifier_type_items(modifier_type_id):
    """Get selectable items for a given modifier type from Modifier_Type_Item."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT description
        FROM Modifier_Type_Item
        WHERE modifier_type_id = ?
        ORDER BY rowid
    ''', (modifier_type_id,))
    items = [row[0] for row in cursor.fetchall()]
    conn.close()
    return items

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
    sync_live_cart() # Update the shared database table

def update_quantity(index, delta):
    """Update quantity of cart item"""
    if 0 <= index < len(st.session_state.cart):
        st.session_state.cart[index]['quantity'] += delta
        if st.session_state.cart[index]['quantity'] <= 0:
            st.session_state.cart.pop(index)
    sync_live_cart() # Update the shared database table

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
            INSERT INTO Order_Cart (service_area_id, order_status, username, provided_name, note)
            VALUES (0, 10, ?, ?, ?)
        ''', (st.session_state.get('username'), st.session_state.provided_name, st.session_state.note))
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
        st.session_state.cart = [] # Clear internal cart
        sync_live_cart() # Flush the CFD display table
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error creating order: {e}")
        return False
    finally:
        conn.close()

@st.dialog("Customize Your Order")
def show_modifier_dialog():
    """
    Dialog 1 — shown when a menu item is tapped.
    • modifier_type_id == 1  →  st.checkbox  (multiple allowed)
    • modifier_type_id != 1  →  button that triggers Dialog 2
    Previously confirmed sub-dialog selections are displayed with a ✅ badge.
    """
    if 'selected_product' not in st.session_state or not st.session_state.selected_product:
        return

    product      = st.session_state.selected_product
    product_id   = product['product_id']
    product_name = product['product_name']
    price        = product['price']

    st.write(f"**{product_name}**")
    st.write(f"Base Price: {format_price(price)}")
    st.divider()

    modifier_groups = get_modifiers(product_id)

    if modifier_groups:
        for type_id, group_data in modifier_groups.items():
            group_desc = group_data['group_description'] or "Modifiers"
            modifiers  = group_data['modifiers']

            st.write(f"**{group_desc}**")

            if type_id == 1:
                # ── Checkbox (type 1) ─────────────────────────────────────
                for modifier in modifiers:
                    mod_price = f" (+{format_price(modifier['price'])})" if modifier['price'] > 0 else ""
                    st.checkbox(
                        f"{modifier['description']}{mod_price}",
                        key=f"dialog_check_{product_id}_{modifier['modifier_id']}"
                    )
            else:
                # ── Select-type button (type != 1) ────────────────────────
                for modifier in modifiers:
                    mod_id    = modifier['modifier_id']
                    mod_price = f" (+{format_price(modifier['price'])})" if modifier['price'] > 0 else ""

                    saved = st.session_state.dialog_modifier_selections.get(mod_id)
                    if saved:
                        label = f"✅  {modifier['description']}: {saved['selected_item']}{mod_price}"
                    else:
                        label = f"➕  {modifier['description']}{mod_price}  — tap to select"

                    if st.button(label, key=f"sub_btn_{product_id}_{mod_id}", use_container_width=True):
                        # Store which modifier needs sub-dialog, then rerun to open Dialog 2
                        st.session_state.pending_sub_modifier = {
                            'modifier_id':          mod_id,
                            'modifier_description': modifier['description'],
                            'modifier_type_id':     type_id,
                            'price':                modifier['price']
                        }
                        st.rerun()

            st.write("")

    # ── Footer ────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.session_state.selected_product           = None
            st.session_state.dialog_modifier_selections = {}
            st.session_state.pending_sub_modifier       = None
            st.rerun()
    with col2:
        if st.button("Add to Cart", type="primary", use_container_width=True):
            selected_modifiers = []

            if modifier_groups:
                for type_id, group_data in modifier_groups.items():
                    modifiers = group_data['modifiers']

                    if type_id == 1:
                        for modifier in modifiers:
                            key = f"dialog_check_{product_id}_{modifier['modifier_id']}"
                            if st.session_state.get(key, False):
                                selected_modifiers.append(modifier)
                    else:
                        for modifier in modifiers:
                            saved = st.session_state.dialog_modifier_selections.get(modifier['modifier_id'])
                            if saved:
                                selected_modifiers.append({
                                    'modifier_id': saved['modifier_id'],
                                    'description': saved['description'],
                                    'price':       saved['price']
                                })

            add_to_cart(product_id, product_name, price, selected_modifiers)
            st.session_state.selected_product           = None
            st.session_state.dialog_modifier_selections = {}
            st.session_state.pending_sub_modifier       = None
            st.rerun()


@st.dialog("Select Option")
def show_sub_modifier_dialog():
    """
    Dialog 2 — opens when a non-type-1 modifier button is clicked in Dialog 1.
    Presents a selectbox of Modifier_Type_Item options for that modifier's type.
    Confirm saves the choice and re-opens Dialog 1; Back discards and re-opens Dialog 1.
    """
    pending = st.session_state.pending_sub_modifier
    if not pending:
        st.rerun()
        return

    modifier_id      = pending['modifier_id']
    modifier_desc    = pending['modifier_description']
    modifier_type_id = pending['modifier_type_id']
    modifier_price   = pending['price']

    price_label = f" (+{format_price(modifier_price)})" if modifier_price > 0 else ""
    st.write(f"**{modifier_desc}**{price_label}")
    st.divider()

    type_items = get_modifier_type_items(modifier_type_id)

    # Pre-select a previous choice if it exists
    saved       = st.session_state.dialog_modifier_selections.get(modifier_id, {})
    prev_item   = saved.get('selected_item')
    options     = ["None"] + type_items
    default_idx = options.index(prev_item) if prev_item in options else 0

    selected = st.selectbox(
        f"Choose {modifier_desc}",
        options,
        index=default_idx,
        label_visibility="collapsed"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            # Discard, clear pending, re-open Dialog 1
            st.session_state.pending_sub_modifier = None
            st.session_state.reopen_main_dialog   = True
            st.rerun()
    with col2:
        if st.button("Confirm", type="primary", use_container_width=True):
            if selected != "None":
                st.session_state.dialog_modifier_selections[modifier_id] = {
                    'modifier_id':   modifier_id,
                    'description':   f"{modifier_desc}: {selected}",
                    'price':         modifier_price,
                    'selected_item': selected
                }
            else:
                st.session_state.dialog_modifier_selections.pop(modifier_id, None)
            st.session_state.pending_sub_modifier = None
            st.session_state.reopen_main_dialog   = True
            st.rerun()


def show_order_page():
    # ── Re-open Dialog 1 after Dialog 2 closes ─────────────────────────────
    if st.session_state.reopen_main_dialog and st.session_state.get('selected_product'):
        st.session_state.reopen_main_dialog = False
        show_modifier_dialog()
        return

    # ── Open Dialog 2 when a non-type-1 modifier button was clicked ────────
    if st.session_state.pending_sub_modifier:
        show_sub_modifier_dialog()
        return

    col_cart, col_menu = st.columns([1, 2])

    # Left column – Cart
    with col_cart:
        # st.subheader("Orders")

        with st.container(height=420, border=True):
            if st.session_state.cart:
                for i, item in enumerate(st.session_state.cart):
                    with st.container():
                        cart_col1, cart_col2, cart_col3 = st.columns([3, 2, 2])

                        with cart_col1:
                            st.write(f"**{item['product_name']}**")
                            st.caption(f"Base: {format_price(item['base_price'])}")
                            if item['modifiers']:
                                for modifier in item['modifiers']:
                                    mp = f" (+{format_price(modifier['price'])})" if modifier['price'] > 0 else ""
                                    st.caption(f"• {modifier['description']}{mp}")

                        with cart_col2:
                            dec_col, qty_col, inc_col = st.columns([1, 1, 1])

                            with dec_col:
                                if st.button(" ➖ ", key=f"dec_{i}", help="Decrease quantity"):
                                    update_quantity(i, -1)
                                    st.rerun()

                            with qty_col:
                                st.markdown(
                                    f"<div style='text-align:center; font-size:16px;'>{item['quantity']}</div>",
                                    unsafe_allow_html=True
                                )

                            with inc_col:
                                if st.button(" ➕ ", key=f"inc_{i}", help="Increase quantity"):
                                    update_quantity(i, 1)
                                    st.rerun()

                        with cart_col3:
                            st.write(format_price(item['price'] * item['quantity']))

                        st.divider()
            else:
                st.info("Cart is empty")

        if 'provided_name' not in st.session_state:
            st.session_state.provided_name = ''
            st.session_state.note = ''

        col1, col2 = st.columns([1, 3])
        with col1:
            st.session_state.provided_name = st.text_input("Name? 👋")
        with col2:
            st.session_state.note = st.text_input("Special request? 👋")

        subtotal = calculate_subtotal()
        st.write(f"Subtotal: {format_price(subtotal)}")

        checkout_disabled = len(st.session_state.cart) == 0
        if st.button("Checkout", type="primary", use_container_width=True, disabled=checkout_disabled):
            if create_order():
                st.success("Order created successfully!")
                st.session_state.cart = []
                st.switch_page("pages/12_Checkout.py")

    # Right column – Menu
    with col_menu:
            # st.subheader("Menu")

            with st.container(height=600, border=True):  

                # Make menu buttons tall enough for two-line text (scoped to tabs only)
                st.markdown("""
                    <style>
                    div[data-testid="stTabs"] div[data-testid="stButton"] button {
                        height: 120px;
                        white-space: pre-wrap;
                        line-height: 1.4;
                    }
                    </style>
                """, unsafe_allow_html=True)

                category = get_category()

                if category:
                    group_names = [group[1] for group in category]
                    tabs = st.tabs(group_names)

                    for i, (group_id, group_name) in enumerate(category):
                        with tabs[i]:
                            product_items = get_products(group_id)
                            cols = st.columns(3)
                            for idx, (product_id, product_name, price) in enumerate(product_items):
                                with cols[idx % 3]:
                                    if st.button(
                                        f"{product_name}\n{format_price(price)}",
                                        key=f"menu_btn_{product_id}",
                                        use_container_width=True
                                    ):
                                        st.session_state.selected_product = {
                                            'product_id':   product_id,
                                            'product_name': product_name,
                                            'price':        price
                                        }
                                        st.session_state.dialog_modifier_selections = {}
                                        st.session_state.pending_sub_modifier       = None
                                        st.session_state.reopen_main_dialog         = False
                                        show_modifier_dialog()


# Run the page
if __name__ == "__main__":
    show_order_page()
