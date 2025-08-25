import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# Configure the page
st.set_page_config(page_title="Gold Trading Calculator", layout="wide")
st.title("💰 Gold Trading Calculator")
st.markdown("Calculate risk and margin requirements for your layered trading strategy with live prices")

# Function to get live prices from Yahoo Finance
@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_live_prices():
    try:
        # Get XAUUSD (Gold) price
        gold = yf.Ticker("GC=F")
        gold_data = gold.history(period="1d", interval="1m")
        gold_price = gold_data['Close'].iloc[-1] if not gold_data.empty else 1950.0
        
        # Get currency rates
        eurusd = yf.Ticker("EURUSD=X")
        eurusd_data = eurusd.history(period="1d", interval="1m")
        eurusd_rate = eurusd_data['Close'].iloc[-1] if not eurusd_data.empty else 1.08
        
        gbpusd = yf.Ticker("GBPUSD=X")
        gbpusd_data = gbpusd.history(period="1d", interval="1m")
        gbpusd_rate = gbpusd_data['Close'].iloc[-1] if not gbpusd_data.empty else 1.26
        
        audusd = yf.Ticker("AUDUSD=X")
        audusd_data = audusd.history(period="1d", interval="1m")
        audusd_rate = audusd_data['Close'].iloc[-1] if not audusd_data.empty else 0.65
        
        usdcad = yf.Ticker("CAD=X")
        usdcad_data = usdcad.history(period="1d", interval="1m")
        usdcad_rate = usdcad_data['Close'].iloc[-1] if not usdcad_data.empty else 1.35
        
        usdchf = yf.Ticker("CHF=X")
        usdchf_data = usdchf.history(period="1d", interval="1m")
        usdchf_rate = usdchf_data['Close'].iloc[-1] if not usdchf_data.empty else 0.88
        
        usdjpy = yf.Ticker("JPY=X")
        usdjpy_data = usdjpy.history(period="1d", interval="1m")
        usdjpy_rate = usdjpy_data['Close'].iloc[-1] if not usdjpy_data.empty else 148.0
        
        return {
            'xauusd': gold_price,
            'eurusd': eurusd_rate,
            'gbpusd': gbpusd_rate,
            'audusd': audusd_rate,
            'usdcad': usdcad_rate,
            'usdchf': usdchf_rate,
            'usdjpy': usdjpy_rate,
            'timestamp': datetime.now()
        }
    except Exception as e:
        st.error(f"Error fetching live prices: {e}")
        # Return default values if API fails
        return {
            'xauusd': 1950.0,
            'eurusd': 1.08,
            'gbpusd': 1.26,
            'audusd': 0.65,
            'usdcad': 1.35,
            'usdchf': 0.88,
            'usdjpy': 148.0,
            'timestamp': datetime.now()
        }

# Get live prices
live_prices = get_live_prices()

# Display live prices dashboard
st.subheader("📊 Live Market Prices")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("XAUUSD (Gold)", f"${live_prices['xauusd']:.2f}")
with col2:
    st.metric("EURUSD", f"{live_prices['eurusd']:.4f}")
with col3:
    st.metric("GBPUSD", f"{live_prices['gbpusd']:.4f}")
with col4:
    st.metric("AUDUSD", f"{live_prices['audusd']:.4f}")

col5, col6, col7, col8 = st.columns(4)
with col5:
    st.metric("USDCAD", f"{live_prices['usdcad']:.4f}")
with col6:
    st.metric("USDCHF", f"{live_prices['usdchf']:.4f}")
with col7:
    st.metric("USDJPY", f"{live_prices['usdjpy']:.2f}")
with col8:
    st.metric("Last Update", live_prices['timestamp'].strftime('%H:%M:%S'))

st.markdown("---")

# User inputs in sidebar
st.sidebar.header("Trading Parameters")

# Input fields
num_layers = st.sidebar.slider("Number of Layers", min_value=1, max_value=12, value=6, 
                              help="How many entry levels you will use")

trades_per_layer = st.sidebar.slider("Trades per Layer", min_value=1, max_value=10, value=4,
                                    help="How many trades you'll execute at each level")

lot_size_per_trade = st.sidebar.number_input("Lot Size per Trade", min_value=0.01, max_value=10.0, 
                                           value=0.01, step=0.01, 
                                           help="Size of each trade in lots")

pip_value = st.sidebar.number_input("Pip Value ($ per 0.01 lot)", min_value=0.01, max_value=10.0,
                                  value=1.0, step=0.1,
                                  help="Dollar value of 1 pip movement for a 0.01 lot trade")

sl_distance_pips = st.sidebar.number_input("SL Distance from 1st Layer (pips)", 
                                         min_value=1, max_value=50, value=6,
                                         help="Distance from your first entry to stop-loss")

distance_first_to_last_layer = st.sidebar.number_input("Distance between 1st-Last Layer (pips)",
                                                     min_value=0.1, max_value=20.0, value=3.0,
                                                     help="Price difference between your first and last entry")

account_balance = st.sidebar.number_input("Account Balance", min_value=100, max_value=100000,
                                        value=1500, step=100)

# Margin calculation inputs
st.sidebar.header("Margin Calculation")

account_currency = st.sidebar.selectbox("Account Currency", 
                                       ["EUR", "USD", "GBP", "CHF", "AUD", "CAD", "JPY"],
                                       help="Currency of your trading account")

leverage = st.sidebar.selectbox("Account Leverage", 
                               ["1:50", "1:100", "1:200", "1:300", "1:400", "1:500", "1:1000", "1:1500", "1:2000"],
                               index=6,  # Default to 1:500
                               help="Your broker's leverage ratio")

# Use live prices with manual override option
xauusd_price = st.sidebar.number_input("Current XAUUSD Price", 
                                     min_value=100.0, max_value=10000.0, 
                                     value=float(live_prices['xauusd']), step=0.1,
                                     help="Current gold price in USD")

# Display current exchange rates and allow manual override if needed
st.sidebar.header("Current Exchange Rates")
if account_currency == "EUR":
    eurusd_rate = st.sidebar.number_input("EURUSD Rate", 
                                        min_value=0.5, max_value=2.0, 
                                        value=float(live_prices['eurusd']), step=0.0001,
                                        format="%.4f")
elif account_currency == "GBP":
    gbpusd_rate = st.sidebar.number_input("GBPUSD Rate", 
                                        min_value=0.5, max_value=2.0, 
                                        value=float(live_prices['gbpusd']), step=0.0001,
                                        format="%.4f")
elif account_currency == "AUD":
    audusd_rate = st.sidebar.number_input("AUDUSD Rate", 
                                        min_value=0.5, max_value=2.0, 
                                        value=float(live_prices['audusd']), step=0.0001,
                                        format="%.4f")
elif account_currency == "CAD":
    usdcad_rate = st.sidebar.number_input("USDCAD Rate", 
                                        min_value=0.5, max_value=2.0, 
                                        value=float(live_prices['usdcad']), step=0.0001,
                                        format="%.4f")
elif account_currency == "CHF":
    usdchf_rate = st.sidebar.number_input("USDCHF Rate", 
                                        min_value=0.5, max_value=2.0, 
                                        value=float(live_prices['usdchf']), step=0.0001,
                                        format="%.4f")
elif account_currency == "JPY":
    usdjpy_rate = st.sidebar.number_input("USDJPY Rate", 
                                        min_value=50.0, max_value=200.0, 
                                        value=float(live_prices['usdjpy']), step=0.1,
                                        format="%.1f")

# Main calculation logic
if num_layers > 1:
    price_gap_pips = distance_first_to_last_layer / (num_layers - 1)
else:
    price_gap_pips = 0

# Create a list of the distance to SL for each layer (in pips)
distance_to_sl_per_layer = [sl_distance_pips - (i * price_gap_pips) for i in range(num_layers)]

# Calculate the loss per TRADE at each layer (in $)
loss_per_trade_per_layer = [distance * pip_value * (lot_size_per_trade / 0.01) for distance in distance_to_sl_per_layer]

# Calculate total loss for the entire position
total_loss = sum(loss_per_trade_per_layer) * trades_per_layer
risk_percentage = (total_loss / account_balance) * 100

# Margin calculation
leverage_ratio = int(leverage.split(":")[1])  # Extract the number from "1:500"
total_lots = num_layers * trades_per_layer * lot_size_per_trade

# Standard margin formula: (Contract Size * Price) / Leverage
# For gold (XAUUSD), contract size is 100 oz per standard lot
contract_size = 100  # ounces per standard lot
margin_required_usd = (total_lots * contract_size * xauusd_price) / leverage_ratio

# Convert margin to account currency if needed
if account_currency == "EUR":
    margin_required = margin_required_usd / eurusd_rate
elif account_currency == "GBP":
    margin_required = margin_required_usd / gbpusd_rate
elif account_currency == "AUD":
    margin_required = margin_required_usd / audusd_rate
elif account_currency == "CAD":
    margin_required = margin_required_usd * usdcad_rate
elif account_currency == "CHF":
    margin_required = margin_required_usd * usdchf_rate
elif account_currency == "JPY":
    margin_required = margin_required_usd * usdjpy_rate
else:  # USD
    margin_required = margin_required_usd

# Calculate margin usage percentage
margin_usage_percentage = (margin_required / account_balance) * 100

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["📊 Trading Plan", "💰 Margin Analysis", "📈 Visualizations"])

with tab1:
    st.subheader("📊 Trading Plan")
    
    # Create a table for layer details
    layer_data = []
    for i, distance in enumerate(distance_to_sl_per_layer):
        layer_data.append({
            'Layer': i+1,
            'Distance to SL (pips)': f"{distance:.2f}",
            'Risk per Trade ($)': f"${loss_per_trade_per_layer[i]:.2f}"
        })
    
    st.table(pd.DataFrame(layer_data))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Trades", f"{num_layers * trades_per_layer}")
        st.metric("Total Lot Size", f"{total_lots:.2f} lots")
        
    with col2:
        st.metric("Maximum Loss", f"${total_loss:.2f}")
        
        # Color code the risk percentage
        risk_color = "green" if risk_percentage <= 2 else "orange" if risk_percentage <= 5 else "red"
        st.metric("Risk Percentage", f"{risk_percentage:.2f}%", delta=None, 
                  delta_color="off", help=f"Of your {account_balance} {account_currency} account")
        
        # Risk assessment
        if risk_percentage > 5:
            st.error("🚨 Risk too high! Consider reducing position size.")
        elif risk_percentage > 2:
            st.warning("⚠️ Moderate risk level. Proceed with caution.")
        else:
            st.success("✅ Risk level acceptable.")

with tab2:
    st.subheader("💰 Margin Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Account Currency", account_currency)
        st.metric("Account Leverage", leverage)
        st.metric("XAUUSD Price", f"${xauusd_price:.2f}")
        
    with col2:
        st.metric("Total Margin Required", f"{margin_required:.2f} {account_currency}")
        st.metric("Margin Usage", f"{margin_usage_percentage:.2f}%")
        st.metric("Free Margin", f"{account_balance - margin_required:.2f} {account_currency}")
    
    # Margin usage assessment
    if margin_usage_percentage > 50:
        st.error("🚨 Margin usage too high! You may face margin calls.")
    elif margin_usage_percentage > 30:
        st.warning("⚠️ High margin usage. Monitor your positions closely.")
    elif margin_usage_percentage > 10:
        st.info("ℹ️ Moderate margin usage.")
    else:
        st.success("✅ Healthy margin usage.")
    
    # Margin calculation details
    with st.expander("📋 Margin Calculation Details"):
        st.write(f"""
        **Calculation Formula:**
        - Total Lots: {total_lots:.2f}
        - Contract Size: 100 oz per standard lot
        - XAUUSD Price: ${xauusd_price:.2f}
        - Leverage: {leverage}
        - Base Margin (USD): ({total_lots:.2f} × 100 × {xauusd_price:.2f}) / {leverage_ratio} = ${margin_required_usd:.2f}
        """)
        
        if account_currency != "USD":
            conversion_rate = margin_required / margin_required_usd
            st.write(f"""
            **Currency Conversion:**
            - USD to {account_currency} conversion rate: {conversion_rate:.4f}
            - Final Margin: ${margin_required_usd:.2f} × {conversion_rate:.4f} = {margin_required:.2f} {account_currency}
            """)

with tab3:
    st.subheader("📈 Visual Risk Representation")
    
    # Create charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk per layer chart
        risk_chart_data = pd.DataFrame({
            'Layer': [f'Layer {i+1}' for i in range(num_layers)],
            'Risk per Trade ($)': loss_per_trade_per_layer
        })
        st.bar_chart(risk_chart_data.set_index('Layer'), use_container_width=True)
        st.caption("Risk per Trade by Layer")
    
    with col2:
        # Margin vs Risk chart
        comparison_data = pd.DataFrame({
            'Metric': ['Margin Required', 'Maximum Risk'],
            'Amount': [margin_required, total_loss],
            'Currency': [account_currency, account_currency]
        })
        st.bar_chart(comparison_data.set_index('Metric'), use_container_width=True)
        st.caption("Margin vs Risk Comparison")

# Additional insights
st.subheader("💡 Insights & Recommendations")

if risk_percentage > 5 or margin_usage_percentage > 50:
    st.write("""
    **To reduce risk and margin usage:**
    - Reduce number of layers
    - Reduce trades per layer  
    - Use smaller lot size
    - Increase distance to SL
    - Consider higher leverage (but be cautious!)
    - Wait for better entry price
    """)
else:
    st.write("""
    **Risk and margin management looks good. Remember:**
    - Always use stop-loss orders
    - Consider moving SL to breakeven after some profit
    - Don't risk more than 2-5% of account per trade
    - Keep margin usage below 30% for safety
    - Monitor currency exchange rates if trading with non-USD account
    """)

# Auto-refresh button
if st.button("🔄 Refresh Live Prices"):
    st.cache_data.clear()
    st.rerun()

# Footer with disclaimer
st.markdown("---")
st.caption(f"""
**Disclaimer:** Live prices from Yahoo Finance. This calculator provides estimates only. 
Actual trading results and margin requirements may vary. Prices updated: {live_prices['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
Always verify pip values and margin requirements with your broker. Practice proper risk management.
""")
