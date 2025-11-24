import streamlit as st
import pandas as pd
import time
from utils.util import format_price
from utils.database import  get_db_connection 
from utils.style import load_css 

# Page configuration
st.set_page_config(page_title="Settle Transactions", page_icon="📒", layout="wide")
# st.title("📒 Settle Transactions")
# st.markdown("---")

# to be updated with data entry tips content in the future
st.info("Data Entry Tips content will be added here in the future.")