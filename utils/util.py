# Custom CSS for styling
import streamlit as st
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