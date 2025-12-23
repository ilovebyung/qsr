import streamlit as st
import streamlit.components.v1 as components
import base64
import datetime

# # Format price from integer to dollar format
# def format_price(price_cents):
#     if price_cents is None:
#         return "$ 0.00"
#     return f"$ {abs(price_cents) / 100:.2f}"

def format_timestamp(timestamp_str):
    """Format timestamp for better display"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str
    
# # Calculate split amounts
# def calculate_split_amounts(total_amount, split_count):
#     if split_count <= 1:
#         return [total_amount]
    
#     base_amount = total_amount // split_count
#     remainder = total_amount % split_count
    
#     amounts = [base_amount] * split_count
    
#     # Distribute remainder starting from the last amounts
#     for i in range(remainder):
#         amounts[-(i+1)] += 1
    
#     return amounts

# Format price helper
def format_price(cents):
    return f"${cents / 100:.2f}"

# Calculate split amounts
def calculate_split_amounts(total, split_count):
    base_amount = total // split_count
    remainder = total % split_count
    
    amounts = [base_amount] * split_count
    for i in range(remainder):
        amounts[i] += 1
    
    return amounts



def play_background_audio(file):
    with open(file, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        
    # HTML/JS to trigger playback without a visible player
    md = f"""
        <audio id="audio-tag" autoplay>
            <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
        </audio>
        <script>
            var audio = document.getElementById('audio-tag');
            audio.volume = 0.5; // Optional: Adjust volume
            audio.play();
        </script>
    """
    components.html(md, height=0, width=0)

# Make sidebar hidden and collapsed
def hide_sidebar():
    st.set_page_config(initial_sidebar_state="collapsed")
    # Completely hide the sidebar
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)
