import streamlit as st
import os

# Set page config
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
st.title("🏠 Welcome to QSR Home ")

# Navigation hint
st.subheader("👈 Use the sidebar to navigate")


# Add vertical space to push the caption down
for _ in range(20):
    st.write("")

# Caption at the bottom
st.caption("Built with ❤️ by BADA") 
