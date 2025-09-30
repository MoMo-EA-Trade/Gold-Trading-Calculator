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

# --- Risk Tiers for Dynamic Risk Calculation ---
start_balance = 1000
end_balance = 150000
def risk_percent(balance):
    """Calculates allowed risk percentage based on account balance."""
    # Cap balance between start_balance (10%) and end_balance (2.5%)
    balance = max(start_balance, min(balance, end_balance))
    return 0.10 - ((balance - start_balance) / (end_balance - start_balance)) * (0.10 - 0.025)

# --- Fixed Auto-Calculation Configurations (New) ---
# (Layers, Config Type, Trades Distribution List)
FIXED_CONFIGS = [
    (6, "Normal", [4, 4, 4, 4, 4, 4]),
    (6, "Effective", [4, 4, 4, 4, 8, 8]),
    (7, "Normal", [4, 4, 4, 4, 4, 4, 4]),
    (7, "Effective", [4, 4, 4, 4, 4, 8, 8]),
    (8, "Normal", [4, 4, 4, 4, 4, 4, 4, 4]),
    (8, "Effective", [4, 4, 4, 4, 4, 8, 8, 8]),
]

# Configure the page
st.set_page_config(page_title="Gold Trading Calculator", layout="wide")
st.title("💰 Gold Trading Calculator")
st.markdown("Calculate risk and margin requirements for your layered trading strategy with live prices")

# Function to get live prices from Yahoo Finance
@st.cache_data(ttl=30) # Cache for 30 seconds
def get_live_prices():
    try:
        # Fetch Gold (GC=F) and relevant FX pairs
        tickers = ["GC=F", "EURUSD=X", "GBPUSD=X", "AUDUSD=X", "CAD=X", "CHF=X", "JPY=X"]
        
        # We fetch all at once to potentially improve performance, though yf.download can sometimes be slow in environments like Streamlit Cloud
        data = yf.download(tickers, period="1d", interval="1m", progress=False)['Close']

        # Extract latest close prices, falling back to safe defaults
        gold_price = data['GC=F'].iloc[-1] if 'GC=F' in data.columns and not data['GC=F'].empty else 3000.0
        eurusd_rate = data['EURUSD=X'].iloc[-1] if 'EURUSD=X' in data.columns and not data['EURUSD=X'].empty else 1.08
        gbpusd_rate = data['GBPUSD=X'].iloc[-1] if 'GBPUSD=X' in data.columns and not data['GBPUSD=X'].empty else 1.26
        audusd_rate = data['AUDUSD=X'].iloc[-1] if 'AUDUSD=X' in data.columns and not data['AUDUSD=X'].empty else 0.65
        usdcad_rate = data['CAD=X'].iloc[-1] if 'CAD=X' in data.columns and not data['CAD=X'].empty else 1.35
        usdchf_rate = data['CHF=X'].iloc[-1] if 'CHF=X' in data.columns and not data['CHF=X'].empty else 0.88
        usdjpy_rate = data['JPY=X'].iloc[-1] if 'JPY=X' in data.columns and not data['JPY=X'].empty else 148.0
        
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
        st.error(f"Error fetching live prices (using default mock data): {e}")
        return {
            'xauusd': 3000.0,
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

num_layers = st.sidebar.slider("Number of Layers", 1, 8, 8)
lot_size_per_trade = st.sidebar.number_input("Lot Size per Trade", 0.01, 10.0, 0.02, 0.01)
pip_value = st.sidebar.number_input("Pip Value ($ per 0.01 lot)", 0.1, 10.0, 0.1, 0.1)
sl_distance_pips = st.sidebar.number_input("SL Distance from 1st Layer (pips)", 10, 500, 80, 10)
distance_first_to_last_layer = st.sidebar.number_input("Distance between 1st-Last Layer (pips)", 10, 50, 40, 10)
account_balance = st.sidebar.number_input("Account Balance", 100, 1000000, 4500, 100)

st.sidebar.header("Margin Calculation")
account_currency = st.sidebar.selectbox("Account Currency", ["EUR", "USD", "GBP", "CHF", "AUD", "CAD", "JPY"], 0)
leverage = st.sidebar.selectbox("Account Leverage", ["1:50","1:100","1:200","1:300","1:400","1:500","1:1000","1:1500","1:2000"], 5)
xauusd_price = st.sidebar.number_input("Current XAUUSD Price", 100.0, 10000.0, float(live_prices['xauusd']), 0.1)

st.sidebar.header("Current Exchange Rates (you can override)")
conversion_rate_usd_to_account = 1.0
# Logic to handle currency conversion rate input
if account_currency == "EUR":
    conversion_rate_usd_to_account = st.sidebar.number_input("EURUSD Rate (USD per EUR)", 0.5, 2.0, float(live_prices['eurusd']), 0.0001, format="%.4f")
elif account_currency == "GBP":
    conversion_rate_usd_to_account = st.sidebar.number_input("GBPUSD Rate (USD per GBP)", 0.5, 2.0, float(live_prices['gbpusd']), 0.0001, format="%.4f")
elif account_currency == "AUD":
    conversion_rate_usd_to_account = st.sidebar.number_input("AUDUSD Rate (USD per AUD)", 0.5, 2.0, float(live_prices['audusd']), 0.0001, format="%.4f")
elif account_currency == "CAD":
    conversion_rate_usd_to_account = st.sidebar.number_input("USDCAD Rate (CAD per USD)", 0.5, 2.5, float(live_prices['usdcad']), 0.0001, format="%.4f")
elif account_currency == "CHF":
    conversion_rate_usd_to_account = st.sidebar.number_input("USDCHF Rate (CHF per USD)", 0.5, 2.0, float(live_prices['usdchf']), 0.0001, format="%.4f")
elif account_currency == "JPY":
    conversion_rate_usd_to_account = st.sidebar.number_input("USDJPY Rate (JPY per USD)", 50.0, 200.0, float(live_prices['usdjpy']), 0.1, format="%.1f")
else:
    conversion_rate_usd_to_account = 1.0

st.sidebar.markdown("---")
st.sidebar.subheader("Trades per Layer")
trades_per_layer_list = []
default_trades = [4, 4, 4, 4, 4, 8, 8, 8] # Default effective distribution
for i in range(num_layers):
    default_value = default_trades[i] if i < len(default_trades) else 4
    trades = st.sidebar.slider(f"Layer {i+1} Trades", 1, 10, default_value, key=f'trades_l{i+1}')
    trades_per_layer_list.append(trades)

# --- Calculations for User's Custom Plan ---
price_gap_pips = distance_first_to_last_layer / (num_layers - 1) if num_layers > 1 else 0
distance_to_sl_per_layer = [sl_distance_pips - (i * price_gap_pips) for i in range(num_layers)]
loss_per_trade_per_layer_usd = [max(0, distance) * pip_value * (lot_size_per_trade / 0.01) for distance in distance_to_sl_per_layer]
total_loss_usd = sum([loss_per_trade_per_layer_usd[i] * trades_per_layer_list[i] for i in range(num_layers)])

# Convert USD losses to account currency
if account_currency in ["EUR","GBP","AUD"]:
    # conversion_rate_usd_to_account is USD per account_currency (USD/EUR, USD/GBP, USD/AUD)
    total_loss = total_loss_usd / conversion_rate_usd_to_account if conversion_rate_usd_to_account else total_loss_usd
elif account_currency in ["CAD","CHF","JPY"]:
    # conversion_rate_usd_to_account is account_currency per USD (CAD/USD, CHF/USD, JPY/USD)
    total_loss = total_loss_usd * conversion_rate_usd_to_account
else:
    total_loss = total_loss_usd

allowed_risk_percentage = risk_percent(account_balance) * 100
actual_risk_percentage = (total_loss / account_balance) * 100 if account_balance else 0

# Margin calculation
leverage_ratio = int(leverage.split(":")[1])
total_lots = sum([trades * lot_size_per_trade for trades in trades_per_layer_list])
contract_size = 100 # Standard for XAUUSD CFDs per 1.0 lot
margin_required_usd = (total_lots * contract_size * xauusd_price) / leverage_ratio
if account_currency in ["EUR","GBP","AUD"]:
    margin_required = margin_required_usd / conversion_rate_usd_to_account if conversion_rate_usd_to_account else margin_required_usd
elif account_currency in ["CAD","CHF","JPY"]:
    margin_required = margin_required_usd * conversion_rate_usd_to_account
else:
    margin_required = margin_required_usd

margin_usage_percentage = (margin_required / account_balance) * 100 if account_balance else 0
currency_symbol = CURRENCY_SYMBOLS.get(account_currency, "$")

# Expected Profit Function (kept as is)
def calculate_expected_profit(lot_size, trades_per_layer, num_layers, price_gap_pips, base_profit=100):
    total_trades = sum(trades_per_layer)
    lot_multiplier = lot_size / 0.01
    trades_multiplier = total_trades / 32 # baseline 32 trades for default 6 layers [4,4,4,4,8,8]
    complexity_factor = 1 + ((num_layers - 6) * 0.05) + ((price_gap_pips / 30) * 0.1)
    complexity_factor = max(0.5, complexity_factor)
    return base_profit * lot_multiplier * trades_multiplier * complexity_factor

# Conversion function (kept as is)
def convert_eur_to(amount_eur, account_currency, live_prices, conv_rate_usd_to_account):
    """Convert amount expressed in EUR to target account_currency."""
    try:
        eurusd = float(live_prices.get('eurusd', 1.08))
    except Exception:
        eurusd = 1.08

    if account_currency == "EUR":
        return amount_eur
    if account_currency == "USD":
        return amount_eur * eurusd

    # Use live prices as fallback if the user input (conv_rate_usd_to_account) is missing/falsy
    current_conv_rate = conv_rate_usd_to_account
    if not current_conv_rate:
        if account_currency == "GBP":
            current_conv_rate = live_prices.get('gbpusd', 1.25)
        elif account_currency == "AUD":
            current_conv_rate = live_prices.get('audusd', 0.65)
        elif account_currency == "CAD":
            current_conv_rate = live_prices.get('usdcad', 1.35)
        elif account_currency == "CHF":
            current_conv_rate = live_prices.get('usdchf', 0.88)
        elif account_currency == "JPY":
            current_conv_rate = live_prices.get('usdjpy', 148.0)

    try:
        current_conv_rate = float(current_conv_rate)
        # currencies quoted as USD per CUR (GBP, AUD)
        if account_currency in ["GBP", "AUD"]:
            rate = eurusd / current_conv_rate
            return amount_eur * rate
        # currencies quoted as CUR per USD (CAD, CHF, JPY)
        elif account_currency in ["CAD", "CHF", "JPY"]:
            rate = eurusd * current_conv_rate
            return amount_eur * rate
    except Exception:
        pass

    return amount_eur

expected_profit_eur = calculate_expected_profit(
    lot_size_per_trade,
    trades_per_layer_list,
    num_layers,
    price_gap_pips,
    base_profit=100
)

expected_profit_converted = convert_eur_to(expected_profit_eur, account_currency, live_prices, conversion_rate_usd_to_account)

# --- NEW Function for Auto-Calculation Logic ---
def calculate_layer_metrics(balance, lot_size, pip_val, sl_pips, distance_to_last, account_currency, conversion_rate):
    """Calculates risk for the fixed trade configurations."""
    suggestions = []
    for layers, config_type, trades_distribution in FIXED_CONFIGS:
        price_gap = distance_to_last / (layers - 1) if layers > 1 else 0
        dist_to_sl = [sl_pips - (i * price_gap) for i in range(layers)]

        # Calculate loss in USD
        loss_per_layer_usd = [
            max(0, d) * pip_val * (lot_size / 0.01) * trades_distribution[i]
            for i, d in enumerate(dist_to_sl)
        ]
        total_loss_usd = sum(loss_per_layer_usd)

        # Convert loss to account currency
        if account_currency in ["EUR", "GBP", "AUD"]:
            total_loss = total_loss_usd / conversion_rate if conversion_rate else total_loss_usd
        elif account_currency in ["CAD", "CHF", "JPY"]:
            total_loss = total_loss_usd * conversion_rate
        else:
            total_loss = total_loss_usd

        # Risk percentage
        risk_pct = (total_loss / balance) * 100 if balance else 0
        allowed_risk_pct = risk_percent(balance) * 100

        suggestions.append({
            "layers": layers,
            "config_type": config_type,
            "trades_distribution": trades_distribution,
            "total_trades": sum(trades_distribution),
            "total_loss": total_loss,
            "risk_pct": risk_pct,
            "allowed_risk_pct": allowed_risk_pct
        })
    return suggestions

# --- Tabs ---
tab1, tab2, tab_auto, tab3 = st.tabs(
    ["📊 Trading Plan", "💰 Margin Analysis", "⚙️ Auto Calculation", "📈 Visualizations"]
)


with tab1:
    st.subheader("📊 Trading Plan (Custom Configuration)")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Trades", f"{sum(trades_per_layer_list)}")
        st.metric("Total Lot Size", f"{total_lots:.2f} lots")
        st.metric(f"Expected Daily Profit ({account_currency})", f"{currency_symbol}{expected_profit_converted:.2f}")
        st.caption(f"(Base: €{expected_profit_eur:.2f} — converted using live/override rates)")
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


with tab_auto:
    st.subheader("⚙️ Auto Trade Layer Calculation")
    st.markdown("Compare risk for pre-defined 6, 7, and 8-layer configurations using your current Lot Size, Pip Value, and SL distance parameters.")

    auto_balance = st.number_input("Enter Account Balance for Auto Suggestion", 100, 1000000, account_balance, 100, key='auto_balance_input')

    # Generate suggestions using the new fixed logic
    auto_suggestions = calculate_layer_metrics(
        auto_balance,
        lot_size_per_trade,
        pip_value,
        sl_distance_pips,
        distance_first_to_last_layer,
        account_currency,
        conversion_rate_usd_to_account
    )

    st.write("### Suggested Trade Configurations & Risk Assessment")
    
    # Display results in two columns for better comparison
    col_normal, col_effective = st.columns(2)

    # Filter and display Normal configurations
    with col_normal:
        st.markdown("#### Normal Distribution (Equal Trades)")
        for s in [s for s in auto_suggestions if s['config_type'] == 'Normal']:
            st.markdown(f"**{s['layers']} Layers (Normal)**")
            st.caption(f"Trades: {s['trades_distribution']}")
            st.write(f"- Total Trades: **{s['total_trades']}**")
            st.write(f"- Max Loss: **{currency_symbol}{s['total_loss']:.2f}**")
            st.write(f"- Risk: **{s['risk_pct']:.2f}%** (Allowed: {s['allowed_risk_pct']:.2f}%)")

            if s["risk_pct"] > s["allowed_risk_pct"]:
                st.error("🚨 Risk too high for this configuration!")
            elif s["risk_pct"] > s["allowed_risk_pct"] * 0.75:
                st.warning("⚠️ Close to max risk for this configuration.")
            else:
                st.success("✅ Within safe risk level.")
            st.markdown("---")

    # Filter and display Effective configurations
    with col_effective:
        st.markdown("#### Effective Distribution (Layered Trades)")
        for s in [s for s in auto_suggestions if s['config_type'] == 'Effective']:
            st.markdown(f"**{s['layers']} Layers (Effective)**")
            st.caption(f"Trades: {s['trades_distribution']}")
            st.write(f"- Total Trades: **{s['total_trades']}**")
            st.write(f"- Max Loss: **{currency_symbol}{s['total_loss']:.2f}**")
            st.write(f"- Risk: **{s['risk_pct']:.2f}%** (Allowed: {s['allowed_risk_pct']:.2f}%)")

            if s["risk_pct"] > s["allowed_risk_pct"]:
                st.error("🚨 Risk too high for this configuration!")
            elif s["risk_pct"] > s["allowed_risk_pct"] * 0.75:
                st.warning("⚠️ Close to max risk for this configuration.")
            else:
                st.success("✅ Within safe risk level.")
            st.markdown("---")


with tab3:
    st.subheader("📈 Visual Risk Representation")
    col1, col2 = st.columns(2)
    with col1:
        risk_chart_data = pd.DataFrame({
            'Layer': [f'Layer {i+1}' for i in range(num_layers)],
            'Risk per Layer (USD)': [loss_per_trade_per_layer_usd[i] * trades_per_layer_list[i] for i in range(num_layers)]
        })
        st.bar_chart(risk_chart_data.set_index('Layer'), use_container_width=True)
        st.caption("Risk per Layer (in USD) for your Custom Configuration")
    with col2:
        comparison_data = pd.DataFrame({
            'Metric': ['Margin Required', 'Maximum Risk (account currency)'],
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
