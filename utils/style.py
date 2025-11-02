import streamlit as st

def load_css():
    """
    Loads all custom CSS styles for the Streamlit application.
    Includes styling for buttons, forms, cards, tables, alerts, and responsive design.
    """
    st.markdown("""
    <style>
    /* ============================================
       GLOBAL AND CORE STYLING
       ============================================ */
    :root {
        --primary-color: #3498db;
        --secondary-color: #28a745;
        --background-color: #f0f2f6;
        --card-background: #ffffff;
        --text-color: #2c3e50;
        --subtext-color: #6c757d;
        --accent-color: #e74c3c;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: var(--text-color);
        background-color: var(--background-color);
    }
    
    /* Remove Streamlit's default top padding/margin */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: none !important;
    }
    
    /* Target the main content area */
    .stApp > header {
        height: 0;
    }
    
    /* Reduce top spacing in main container */
    .main > div {
        padding: 0.5rem 1rem !important;
    }
    
    /* Remove top margin from first element */
    .main > div > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* ============================================
       PAGE TITLE AND HEADER STYLING
       ============================================ */
    .main h1 {
        color: var(--text-color);
        border-bottom: 3px solid var(--primary-color);
        padding-bottom: 10px;
        margin-top: 0 !important;
        margin-bottom: 20px;
        font-weight: bold;
    }

    /* ============================================
       BUTTON STYLING
       ============================================ */
    /* Regular Button Styling */
    div.stButton > button {
        width: 100%;
        height: auto;
        min-height: 50px;
        white-space: pre-line;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 12px;
        border: 3px solid;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        cursor: pointer;
    }

    /* Service Area Button Specific Styling */
    div.stButton > button[data-testid="baseButton-secondary"] {
        background-color: var(--card-background);
        color: var(--text-color);
        border-color: var(--secondary-color);
        min-height: 120px;
        padding: 2rem;
    }

    /* Button State Classes */
    .active-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: #667eea !important;
    }
    
    .available-button {
        background: var(--card-background) !important;
        color: var(--text-color) !important;
        border-color: var(--secondary-color) !important;
    }
    
    /* Confirm Order Button */
    .stButton > button:has-text("Confirm Order") {
        background: var(--accent-color);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 6px 16px;
        font-weight: 500;
        font-size: 12px;
        min-height: 28px;
        margin-top: 8px;
    }

    .stButton > button:has-text("Confirm Order"):hover {
        background: #e04146;
        transform: translateY(-1px);
        box-shadow: 0 3px 8px rgba(255, 90, 95, 0.3);
    }

    /* Secondary Button */
    .stButton > button[kind="secondary"] {
        height: 40px;
        background-color: #1f77b4;
        color: white;
        border: 2px solid #1f77b4;
    }

    .stButton > button[kind="secondary"]:hover {
        background-color: #0d5aa7;
        border-color: #0d5aa7;
    }

    /* Disabled Button */
    .stButton > button:disabled {
        background-color: #ff4444;
        color: white;
        opacity: 0.7;
        cursor: not-allowed;
    }

    /* ============================================
       FORM SUBMIT BUTTON STYLING
       ============================================ */
    .stFormSubmitButton > button {
        width: 100%;
        height: auto;
        min-height: 45px;
        font-size: 1rem;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        background: linear-gradient(135deg, var(--primary-color) 0%, #2980b9 100%);
        color: white;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
    }

    .stFormSubmitButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(52, 152, 219, 0.4);
        background: linear-gradient(135deg, #2980b9 0%, #1f618d 100%);
        cursor: pointer;
    }

    .stFormSubmitButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(52, 152, 219, 0.3);
    }

    /* ============================================
       CARD AND CONTAINER STYLING
       ============================================ */
    /* Cart Container */
    .cart-container {
        background-color: var(--card-background);
        border: 2px solid #dee2e6;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Order Card */
    .order-card {
        background: var(--card-background);
        border: 2px solid #e1e5e9;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        overflow: hidden;
        animation: slideIn 0.5s ease-out;
    }
    
    .order-card:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    /* Order Header */
    .order-header {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 12px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 600;
        font-size: 14px;
    }
    
    .order-header span {
        padding: 4px 8px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 6px;
        font-size: 12px;
    }

    /* ============================================
       TABLE STYLING
       ============================================ */
    .product-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 12px;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        overflow: hidden;
    }

    .table-header {
        background-color: #f8f9fa;
        color: #495057;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 10px 12px;
        border-bottom: 2px solid #dee2e6;
        text-align: left;
    }

    .product-name {
        padding: 12px;
        border-bottom: 1px solid #f1f3f4;
        font-size: 14px;
        color: #2c3e50;
        line-height: 1.4;
    }

    .quantity-cell {
        padding: 12px;
        border-bottom: 1px solid #f1f3f4;
        text-align: center;
        font-weight: 600;
        font-size: 16px;
        color: var(--accent-color);
        background-color: #fef9f9;
        width: 100px;
    }

    /* ============================================
       MESSAGE AND ALERT STYLING
       ============================================ */
    .stSuccess {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
        border-radius: 8px;
    }
    
    .stAlert > div {
        border-radius: 10px;
        padding: 15px;
        font-weight: 500;
    }
    
    .stInfo > div {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 8px;
        padding: 15px;
        color: #0c5460;
        font-weight: 500;
    }

    /* ============================================
       ANIMATIONS
       ============================================ */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* ============================================
       RESPONSIVE DESIGN
       ============================================ */
    @media (max-width: 768px) {
        .main > div {
            padding: 0.25rem !important;
        }
        
        .main .block-container {
            padding-top: 0.5rem !important;
        }
        
        div.stButton > button {
            min-height: 100px;
            font-size: 1rem;
        }

        .stFormSubmitButton > button {
            min-height: 40px;
            font-size: 0.95rem;
        }
        
        .order-card {
            margin-bottom: 15px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
