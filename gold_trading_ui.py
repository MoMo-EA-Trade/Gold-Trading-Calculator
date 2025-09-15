import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# --- Constants & Helper Functions ---
CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "CHF": "Fr",
    "AUD": "A$",
    "CAD": "C$",
    "JPY": "¥"
}

# Configure the page
st.set_page_config(page_title="Gold Trading Calculator", layout="wide")
st.title("💰 Gold Trading Calculator")
st.markdown("Calculate risk and margin requirements for your layered trading strategy with live prices")

# Function to get live prices from Yahoo Finance
@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_live_prices():
    try:
        gold = yf.Ticker("GC=F")
        gold_data = gold.history(period="1d", interval="1m")
        gold_price = gold_data['Close'].iloc[-1] if not gold_data.empty else 1950.0
        
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

num_layers = st.sidebar.slider("Number of Layers", 1, 12, 6)
lot_size_per_trade = st.sidebar.number_input("Lot Size per Trade", 0.01, 10.0, 0.01, 0.01)
pip_value = st.sidebar.number_input("Pip Value ($ per 0.01 lot)", 0.1, 10.0, 0.1, 0.1)
sl_distance_pips = st.sidebar.number_input("SL Distance from 1st Layer (pips)", 10, 500, 80, 10)
distance_first_to_last_layer = st.sidebar.number_input("Distance between 1st-Last Layer (pips)", 10, 50, 30, 10)
account_balance = st.sidebar.number_input("Account Balance", 100, 1000000, 1000, 100)

st.sidebar.header("Margin Calculation")
account_currency = st.sidebar.selectbox("Account Currency", ["EUR", "USD", "GBP", "CHF", "AUD", "CAD", "JPY"], 0)
leverage = st.sidebar.selectbox("Account Leverage", ["1:50","1:100","1:200","1:300","1:400","1:500","1:1000","1:1500","1:2000"], 5)
xauusd_price = st.sidebar.number_input("Current XAUUSD Price", 100.0, 10000.0, float(live_prices['xauusd']), 0.1)

st.sidebar.header("Current Exchange Rates")
conversion_rate_usd_to_account = 1.0
if account_currency == "EUR":
    conversion_rate_usd_to_account = st.sidebar.number_input("EURUSD Rate", 0.5, 2.0, float(live_prices['eurusd']), 0.0001, format="%.4f")
elif account_currency == "GBP":
    conversion_rate_usd_to_account = st.sidebar.number_input("GBPUSD Rate", 0.5, 2.0, float(live_prices['gbpusd']), 0.0001, format="%.4f")
elif account_currency == "AUD":
    conversion_rate_usd_to_account = st.sidebar.number_input("AUDUSD Rate", 0.5, 2.0, float(live_prices['audusd']), 0.0001, format="%.4f")
elif account_currency == "CAD":
    conversion_rate_usd_to_account = st.sidebar.number_input("USDCAD Rate", 0.5, 2.0, float(live_prices['usdcad']), 0.0001, format="%.4f")
elif account_currency == "CHF":
    conversion_rate_usd_to_account = st.sidebar.number_input("USDCHF Rate", 0.5, 2.0, float(live_prices['usdchf']), 0.0001, format="%.4f")
elif account_currency == "JPY":
    conversion_rate_usd_to_account = st.sidebar.number_input("USDJPY Rate", 50.0, 200.0, float(live_prices['usdjpy']), 0.1, format="%.1f")

st.sidebar.markdown("---")
st.sidebar.subheader("Trades per Layer")
trades_per_layer_list = []
default_trades = [4, 4, 4, 4, 8, 8]
for i in range(num_layers):
    default_value = default_trades[i] if i < len(default_trades) else 4
    trades = st.sidebar.slider(f"Layer {i+1} Trades", 1, 10, default_value, key=f'trades_l{i+1}')
    trades_per_layer_list.append(trades)

# --- Calculations ---
price_gap_pips = distance_first_to_last_layer / (num_layers - 1) if num_layers > 1 else 0
distance_to_sl_per_layer = [sl_distance_pips - (i * price_gap_pips) for i in range(num_layers)]
loss_per_trade_per_layer_usd = [distance * pip_value * (lot_size_per_trade / 0.01) for distance in distance_to_sl_per_layer]
total_loss_usd = sum([loss_per_trade_per_layer_usd[i] * trades_per_layer_list[i] for i in range(num_layers)])

if account_currency in ["EUR","GBP","AUD"]:
    total_loss = total_loss_usd / conversion_rate_usd_to_account
elif account_currency in ["CAD","CHF","JPY"]:
    total_loss = total_loss_usd * conversion_rate_usd_to_account
else:
    total_loss = total_loss_usd

# --- NEW: Dynamic Risk Formula ---
start_balance = 1000
end_balance = 150000
def risk_percent(balance):
    balance = max(start_balance, min(balance, end_balance))
    return 0.10 - ((balance - start_balance) / (end_balance - start_balance)) * (0.10 - 0.025)

allowed_risk_percentage = risk_percent(account_balance) * 100
actual_risk_percentage = (total_loss / account_balance) * 100

# Margin calculation
leverage_ratio = int(leverage.split(":")[1])
total_lots = sum([trades * lot_size_per_trade for trades in trades_per_layer_list])
contract_size = 100
margin_required_usd = (total_lots * contract_size * xauusd_price) / leverage_ratio
if account_currency in ["EUR","GBP","AUD"]:
    margin_required = margin_required_usd / conversion_rate_usd_to_account
elif account_currency in ["CAD","CHF","JPY"]:
    margin_required = margin_required_usd * conversion_rate_usd_to_account
else:
    margin_required = margin_required_usd

margin_usage_percentage = (margin_required / account_balance) * 100
currency_symbol = CURRENCY_SYMBOLS.get(account_currency, "$")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Trading Plan", "💰 Margin Analysis", "📈 Visualizations"])

with tab1:
    st.subheader("📊 Trading Plan")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Trades", f"{sum(trades_per_layer_list)}")
        st.metric("Total Lot Size", f"{total_lots:.2f} lots")
    with col2:
        st.metric(f"Maximum Loss ({account_currency})", f"{currency_symbol}{total_loss:.2f}")
        st.metric("Actual Risk %", f"{actual_risk_percentage:.2f}%")
        st.metric("Allowed Risk %", f"{allowed_risk_percentage:.2f}%")
        if actual_risk_percentage > allowed_risk_percentage:
            st.error("🚨 Risk too high! Reduce position size or increase balance.")
        elif actual_risk_percentage > allowed_risk_percentage * 0.75:
            st.warning("⚠️ Close to your max allowed risk.")
        else:
            st.success("✅ Risk level within allowed range.")

with tab2:
    st.subheader("💰 Margin Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Account Currency", account_currency)
        st.metric("Account Leverage", leverage)
        st.metric("XAUUSD Price", f"${xauusd_price:.2f}")
    with col2:
        st.metric("Total Margin Required", f"{currency_symbol}{margin_required:.2f}")
        st.metric("Margin Usage", f"{margin_usage_percentage:.2f}%")
        st.metric("Free Margin", f"{currency_symbol}{account_balance - margin_required:.2f}")
    if margin_usage_percentage > 50:
        st.error("🚨 Margin usage too high!")
    elif margin_usage_percentage > 30:
        st.warning("⚠️ High margin usage.")
    elif margin_usage_percentage > 10:
        st.info("ℹ️ Moderate margin usage.")
    else:
        st.success("✅ Healthy margin usage.")

with tab3:
    st.subheader("📈 Visual Risk Representation")
    col1, col2 = st.columns(2)
    with col1:
        risk_chart_data = pd.DataFrame({
            'Layer': [f'Layer {i+1}' for i in range(num_layers)],
            'Risk per Trade ($)': [l * t for l, t in zip(loss_per_trade_per_layer_usd, trades_per_layer_list)]
        })
        st.bar_chart(risk_chart_data.set_index('Layer'), use_container_width=True)
        st.caption("Risk per Layer (in USD)")
    with col2:
        comparison_data = pd.DataFrame({
            'Metric': ['Margin Required', 'Maximum Risk'],
            'Amount': [margin_required, total_loss],
        })
        st.bar_chart(comparison_data.set_index('Metric'), use_container_width=True)
        st.caption("Margin vs Risk Comparison")

# Insights
st.subheader("💡 Insights & Recommendations")
if actual_risk_percentage > allowed_risk_percentage or margin_usage_percentage > 50:
    st.write("""
    **To reduce risk and margin usage:**
    - Reduce number of layers
    - Reduce trades per layer
    - Use smaller lot size
    - Increase distance to SL
    - Consider higher leverage (carefully!)
    """)
else:
    st.write("""
    **Risk and margin management looks good.**
    - Keep risk under control
    - Don't risk more than 2–5% per trade
    - Keep margin usage below 30%
    """)

if st.button("🔄 Refresh Live Prices"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")
st.caption(f"""
**Disclaimer:** Live prices from Yahoo Finance. This calculator provides estimates only.
Prices updated: {live_prices['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
Always verify values with your broker.
""")
