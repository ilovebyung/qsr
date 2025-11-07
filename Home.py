import streamlit as st
import os

# Set page config
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
st.title("🏠 Welcome to QSR Home ")

# Navigation hint
st.subheader("👈 Use the sidebar to navigate")


# Input field for name
if 'name' not in st.session_state:
    st.session_state.name = ''

# st.session_state.name = st.text_input("Ask customer name", st.session_state.name)

# with st.popover("Ask customer name"):
#     st.markdown("Mave this feature to either order or checkout 👋")
#     st.session_state.name = st.text_input("What's your name?")

# Add vertical space to push the caption down
for _ in range(10):
    st.write("")

# # Display the stored name
# if st.session_state.name:
#     st.write(f"Welcome, {st.session_state.name}!") 

# Caption at the bottom
st.caption("Built with ❤️ by BADA") 
