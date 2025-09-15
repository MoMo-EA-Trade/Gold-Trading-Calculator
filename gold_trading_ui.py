import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# ---------------------------
# Constants & Helpers
# ---------------------------
CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "CHF": "Fr",
    "AUD": "A$",
    "CAD": "C$",
    "JPY": "¥"
}

st.set_page_config(page_title="Gold Trading Calculator (Full)", layout="wide")
st.title("💰 Gold Trading Calculator — Full")
st.markdown("Estimate margin, risk and average profit for a layered gold entry strategy. Simulate which levels open and which hit TP.")

@st.cache_data(ttl=30)
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
        # Return defaults on failure
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

live_prices = get_live_prices()

# ---------------------------
# Top live price display
# ---------------------------
st.subheader("📊 Live Market Prices")
c1, c2, c3, c4 = st.columns(4)
c1.metric("XAUUSD (Gold)", f"${live_prices['xauusd']:.2f}")
c2.metric("EURUSD", f"{live_prices['eurusd']:.4f}")
c3.metric("GBPUSD", f"{live_prices['gbpusd']:.4f}")
c4.metric("AUDUSD", f"{live_prices['audusd']:.4f}")
c5, c6, c7, c8 = st.columns(4)
c5.metric("USDCAD", f"{live_prices['usdcad']:.4f}")
c6.metric("USDCHF", f"{live_prices['usdchf']:.4f}")
c7.metric("USDJPY", f"{live_prices['usdjpy']:.2f}")
c8.metric("Last Update", live_prices['timestamp'].strftime('%Y-%m-%d %H:%M:%S'))
st.markdown("---")

# ---------------------------
# Sidebar - Inputs
# ---------------------------
st.sidebar.header("Trading Parameters")
num_layers = st.sidebar.slider("Number of Layers (tiers)", min_value=1, max_value=12, value=6, help="How many entry levels you will use")
lot_size_per_trade = st.sidebar.number_input("Lot Size per Trade (lots)", min_value=0.01, max_value=10.0, value=0.01, step=0.01, help="Size of each trade in lots")
pip_value = st.sidebar.number_input("Pip Value ($ per 0.01 lot)", min_value=0.01, max_value=100.0, value=0.1, step=0.01, help="Dollar value of 1 pip for a 0.01 lot trade")
sl_distance_pips = st.sidebar.number_input("SL Distance from 1st Layer (pips)", min_value=1, max_value=2000, value=80, step=1, help="Distance from your first entry to stop-loss")
tp_distance_pips = st.sidebar.number_input("TP Distance (pips)", min_value=1, max_value=2000, value=50, step=1, help="Take-profit distance (use same for all levels or adapt later)")
distance_first_to_last_layer = st.sidebar.number_input("Distance between 1st-Last Layer (pips)", min_value=0, max_value=1000, value=30, step=1, help="Price difference between your first and last entry")
account_balance = st.sidebar.number_input("Account Balance", min_value=100.0, max_value=10000000.0, value=1000.0, step=100.0)

st.sidebar.header("Margin / Account")
account_currency = st.sidebar.selectbox("Account Currency", ["EUR", "USD", "GBP", "CHF", "AUD", "CAD", "JPY"], index=0)
leverage = st.sidebar.selectbox("Account Leverage", ["1:50", "1:100", "1:200", "1:300", "1:400", "1:500", "1:1000", "1:1500", "1:2000"], index=5)
# Allow override of XAUUSD price
xauusd_price = st.sidebar.number_input("Current XAUUSD Price (override)", min_value=10.0, max_value=20000.0, value=float(live_prices['xauusd']), step=0.1)

st.sidebar.header("Current Exchange Rates (override)")
# conversion_rate_usd_to_account holds the appropriate pair value for converting USD -> account currency
conversion_rate_usd_to_account = 1.0
if account_currency == "EUR":
    conversion_rate_usd_to_account = st.sidebar.number_input("EURUSD (quote)", min_value=0.1, max_value=2.0, value=float(live_prices['eurusd']), step=0.0001, format="%.4f", help="EURUSD (1 EUR = X USD) — used to convert USD -> EUR (divide)")
elif account_currency == "GBP":
    conversion_rate_usd_to_account = st.sidebar.number_input("GBPUSD (quote)", min_value=0.1, max_value=2.0, value=float(live_prices['gbpusd']), step=0.0001, format="%.4f", help="GBPUSD (1 GBP = X USD) — used to convert USD -> GBP (divide)")
elif account_currency == "AUD":
    conversion_rate_usd_to_account = st.sidebar.number_input("AUDUSD (quote)", min_value=0.1, max_value=2.0, value=float(live_prices['audusd']), step=0.0001, format="%.4f", help="AUDUSD (1 AUD = X USD) — used to convert USD -> AUD (divide)")
elif account_currency == "CAD":
    conversion_rate_usd_to_account = st.sidebar.number_input("USDCAD (quote)", min_value=0.1, max_value=5.0, value=float(live_prices['usdcad']), step=0.0001, format="%.4f", help="USDCAD (1 USD = X CAD) — used to convert USD -> CAD (multiply)")
elif account_currency == "CHF":
    conversion_rate_usd_to_account = st.sidebar.number_input("USDCHF (quote)", min_value=0.1, max_value=5.0, value=float(live_prices['usdchf']), step=0.0001, format="%.4f", help="USDCHF (1 USD = X CHF) — used to convert USD -> CHF (multiply)")
elif account_currency == "JPY":
    conversion_rate_usd_to_account = st.sidebar.number_input("USDJPY (quote)", min_value=10.0, max_value=500.0, value=float(live_prices['usdjpy']), step=0.1, format="%.1f", help="USDJPY (1 USD = X JPY) — used to convert USD -> JPY (multiply)")

# ---------------------------
# Trades per layer (configured)
# ---------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Configured Trades per Layer (planned)")
trades_per_layer_list = []
default_trades = [4, 4, 4, 4, 8, 8]  # same defaults as earlier
for i in range(num_layers):
    default_value = default_trades[i] if i < len(default_trades) else 4
    t = st.sidebar.slider(f"Layer {i+1}: Planned trades", min_value=0, max_value=30, value=default_value, key=f"trades_l{i+1}", help="How many identical trades you plan for this layer")
    trades_per_layer_list.append(t)

# ---------------------------
# Simulation / Which actually opened / TP hits
# ---------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Simulation: Which opened & which TP hit")
opened_trades_per_layer = []
tp_hits_per_layer = []

for i in range(num_layers):
    planned = trades_per_layer_list[i]
    opened = st.sidebar.slider(f"Layer {i+1} — Opened trades", min_value=0, max_value=planned, value=planned, key=f"opened_l{i+1}")
    tp_hits = st.sidebar.slider(f"Layer {i+1} — TP hits", min_value=0, max_value=opened, value=min(opened, planned//2 if planned>0 else 0), key=f"tp_l{i+1}")
    opened_trades_per_layer.append(opened)
    tp_hits_per_layer.append(tp_hits)

# ---------------------------
# Core calculations
# ---------------------------
# price gap between layers
price_gap_pips = distance_first_to_last_layer / (num_layers - 1) if num_layers > 1 else 0.0
distance_to_sl_per_layer = [sl_distance_pips - (i * price_gap_pips) for i in range(num_layers)]
# Profit and loss per trade (USD)
# pip_value = $ per 0.01 lot, so scale by lot_size_per_trade / 0.01
scale = (lot_size_per_trade / 0.01) if lot_size_per_trade > 0 else 0.0
loss_per_trade_usd_per_layer = [max(0.0, d) * pip_value * scale for d in distance_to_sl_per_layer]  # ensure non-negative distances
profit_per_trade_usd = tp_distance_pips * pip_value * scale  # same for all layers (we use same TP distance)

# Theoretical max loss (if all planned trades lose)
theoretical_max_loss_usd = sum(loss_per_trade_usd_per_layer[i] * trades_per_layer_list[i] for i in range(num_layers))

# Realized (simulated) P/L based on opened trades and tp hits
layer_records = []
total_profit_usd = 0.0
total_realized_loss_usd = 0.0
total_configured_lots = sum([trades_per_layer_list[i] * lot_size_per_trade for i in range(num_layers)])
total_opened_trades = sum(opened_trades_per_layer)
total_tp_hits = sum(tp_hits_per_layer)
total_sl_hits = 0

for i in range(num_layers):
    planned = trades_per_layer_list[i]
    opened = opened_trades_per_layer[i]
    tp_hits = tp_hits_per_layer[i]
    sl_hits = opened - tp_hits
    total_sl_hits += sl_hits

    layer_profit_usd = tp_hits * profit_per_trade_usd
    layer_loss_usd_realized = sl_hits * loss_per_trade_usd_per_layer[i]
    layer_max_loss_usd = planned * loss_per_trade_usd_per_layer[i]

    total_profit_usd += layer_profit_usd
    total_realized_loss_usd += layer_loss_usd_realized

    layer_records.append({
        "layer": i + 1,
        "planned_trades": planned,
        "opened_trades": opened,
        "tp_hits": tp_hits,
        "sl_hits": sl_hits,
        "profit_per_trade_usd": round(profit_per_trade_usd, 4),
        "loss_per_trade_usd": round(loss_per_trade_usd_per_layer[i], 4),
        "layer_profit_usd": round(layer_profit_usd, 4),
        "layer_realized_loss_usd": round(layer_loss_usd_realized, 4),
        "layer_max_loss_usd": round(layer_max_loss_usd, 4)
    })

# Closed trades count (we assume opened trades were closed either TP or SL)
closed_trades_count = total_opened_trades
net_realized_pl_usd = total_profit_usd - total_realized_loss_usd
average_profit_per_closed_trade_usd = net_realized_pl_usd / closed_trades_count if closed_trades_count > 0 else 0.0

# ---------------------------
# Currency conversion helpers
# ---------------------------
def usd_to_account_currency(amount_usd: float) -> float:
    """Convert USD amount to account currency using the user-provided quote."""
    if account_currency in ["EUR", "GBP", "AUD"]:
        # conversion_rate_usd_to_account is the pair like EURUSD (1 EUR = X USD) -> divide USD by X to get EUR
        if conversion_rate_usd_to_account == 0:
            return 0.0
        return amount_usd / conversion_rate_usd_to_account
    elif account_currency in ["CAD", "CHF", "JPY"]:
        # conversion_rate_usd_to_account is USDCAD / USDCHF / USDJPY (1 USD = X account currency) -> multiply
        return amount_usd * conversion_rate_usd_to_account
    else:  # USD
        return amount_usd

def format_ccy(amount: float) -> str:
    symbol = CURRENCY_SYMBOLS.get(account_currency, "$")
    return f"{symbol}{amount:,.2f}"

# Convert realized and theoretical numbers to account currency for display
theoretical_max_loss_account = usd_to_account_currency(theoretical_max_loss_usd)
realized_loss_account = usd_to_account_currency(total_realized_loss_usd)
total_profit_account = usd_to_account_currency(total_profit_usd)
net_realized_pl_account = usd_to_account_currency(net_realized_pl_usd)
avg_profit_account = usd_to_account_currency(average_profit_per_closed_trade_usd)

# ---------------------------
# Dynamic risk % (linear scaling)
# ---------------------------
start_balance = 1000.0
end_balance = 100000.0
def risk_percent(balance):
    balance = max(start_balance, min(balance, end_balance))
    return 0.10 - ((balance - start_balance) / (end_balance - start_balance)) * (0.10 - 0.025)

allowed_risk_percentage = risk_percent(account_balance) * 100.0  # percent
# two risk metrics:
theoretical_max_risk_percentage = (theoretical_max_loss_account / account_balance) * 100.0 if account_balance else 0.0
realized_risk_percentage = (realized_loss_account / account_balance) * 100.0 if account_balance else 0.0

# ---------------------------
# Margin calculation
# ---------------------------
leverage_ratio = int(leverage.split(":")[1])
contract_size = 100  # ounces per standard lot
margin_required_usd = (total_configured_lots * contract_size * xauusd_price) / leverage_ratio
margin_required_account = usd_to_account_currency(margin_required_usd)
margin_usage_percentage = (margin_required_account / account_balance) * 100.0 if account_balance else 0.0
free_margin_account = account_balance - margin_required_account

# ---------------------------
# Tabs / UI Output
# ---------------------------
tab1, tab2, tab3 = st.tabs(["📊 Trading Plan & Simulation", "💰 Margin Analysis", "📈 Visualizations"])

with tab1:
    st.subheader("Trading Plan Summary")
    left, right = st.columns(2)
    with left:
        st.metric("Configured Total Trades", f"{sum(trades_per_layer_list)}")
        st.metric("Configured Total Lots", f"{total_configured_lots:.2f} lots")
        st.metric("Total Opened Trades (simulated)", f"{total_opened_trades}")
        st.metric("Total TP Hits (simulated)", f"{total_tp_hits}")
    with right:
        st.metric("Total Realized Profit", format_ccy(total_profit_account))
        st.metric("Total Realized Loss", format_ccy(realized_loss_account))
        st.metric("Net Realized P/L", format_ccy(net_realized_pl_account if net_realized_pl_account is not None else 0.0))

    st.markdown("**Average profit per closed trade (realized)**")
    st.metric("Average Profit / Closed Trade", format_ccy(avg_profit_account), help="Net realized P/L divided by number of closed (opened) trades")

    st.markdown("----")
    st.subheader("Risk Assessment (planned vs realized)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Allowed Risk % (by balance)", f"{allowed_risk_percentage:.2f}%")
    with col2:
        st.metric("Theoretical Max Risk %", f"{theoretical_max_risk_percentage:.2f}%")
    with col3:
        st.metric("Realized Risk % (sim)", f"{realized_risk_percentage:.2f}%")

    # Warnings / assessments
    if theoretical_max_risk_percentage > allowed_risk_percentage:
        st.error("🚨 Planned/theoretical max risk exceeds allowed risk percentage — reduce positions or increase balance.")
    elif realized_risk_percentage > allowed_risk_percentage:
        st.warning("⚠️ Your realized losses (simulated) exceed allowed risk. Consider adjustments.")
    elif realized_risk_percentage > allowed_risk_percentage * 0.75:
        st.warning("⚠️ Realized losses are approaching allowed risk threshold.")
    else:
        st.success("✅ Risk within allowed boundaries (simulated).")

    st.markdown("---")
    st.subheader("Per-Layer Breakdown (USD)")
    df_layers = pd.DataFrame(layer_records)
    # Add account-currency fields to table for easier reading
    df_layers["layer_profit_account"] = df_layers["layer_profit_usd"].apply(usd_to_account_currency).map(lambda x: round(x, 2))
    df_layers["layer_realized_loss_account"] = df_layers["layer_realized_loss_usd"].apply(usd_to_account_currency).map(lambda x: round(x, 2))
    df_layers["layer_max_loss_account"] = df_layers["layer_max_loss_usd"].apply(usd_to_account_currency).map(lambda x: round(x, 2))
    st.dataframe(df_layers[[
        "layer", "planned_trades", "opened_trades", "tp_hits", "sl_hits",
        "profit_per_trade_usd", "loss_per_trade_usd",
        "layer_profit_usd", "layer_realized_loss_usd", "layer_max_loss_usd",
        "layer_profit_account", "layer_realized_loss_account", "layer_max_loss_account"
    ]], use_container_width=True)

with tab2:
    st.subheader("💰 Margin Analysis")
    a, b = st.columns(2)
    with a:
        st.metric("Account Currency", account_currency)
        st.metric("Account Leverage", leverage)
        st.metric("XAUUSD Price", f"${xauusd_price:.2f}")
    with b:
        st.metric("Total Margin Required", format_ccy(margin_required_account))
        st.metric("Margin Usage", f"{margin_usage_percentage:.2f}%")
        st.metric("Free Margin", format_ccy(free_margin_account))

    # Margin messages
    if margin_usage_percentage > 50:
        st.error("🚨 Margin usage too high! You may face margin calls.")
    elif margin_usage_percentage > 30:
        st.warning("⚠️ High margin usage. Monitor positions closely.")
    elif margin_usage_percentage > 10:
        st.info("ℹ️ Moderate margin usage.")
    else:
        st.success("✅ Healthy margin usage.")

    with st.expander("📋 Margin Calculation Details"):
        st.write(f"""
        **Calculation Formula:**
        - Total Lots (configured): {total_configured_lots:.2f} lots
        - Contract Size: {contract_size} oz per standard lot
        - XAUUSD Price: ${xauusd_price:.2f}
        - Leverage: {leverage}
        - Base Margin (USD): ({total_configured_lots:.2f} × {contract_size} × {xauusd_price:.2f}) / {leverage_ratio} = ${margin_required_usd:.2f}
        - Converted to {account_currency}: {format_ccy(margin_required_account)}
        """)

with tab3:
    st.subheader("📈 Visualizations")
    # Risk per layer: theoretical vs realized
    viz_df = pd.DataFrame({
        "Layer": [f"Layer {r['layer']}" for r in layer_records],
        "Layer Max Loss (USD)": [r["layer_max_loss_usd"] for r in layer_records],
        "Layer Realized Loss (USD)": [r["layer_realized_loss_usd"] for r in layer_records],
        "Layer Profit (USD)": [r["layer_profit_usd"] for r in layer_records]
    }).set_index("Layer")
    st.bar_chart(viz_df, use_container_width=True)
    st.caption("Per-layer: theoretical max loss (planned), realized loss (sim), and realized profit (sim) — USD amounts")

    # Margin vs worst-case risk
    comp_df = pd.DataFrame({
        "Metric": ["Margin Required", "Theoretical Max Loss", "Realized Loss (sim)", "Net Realized P/L"],
        "Amount (account currency)": [margin_required_account, theoretical_max_loss_account, realized_loss_account, net_realized_pl_account]
    }).set_index("Metric")
    st.bar_chart(comp_df, use_container_width=True)
    st.caption("Comparison (converted to account currency)")

    # Risk curve (balance vs allowed risk %) for context
    st.markdown("**Risk % vs Balance (context)**")
    balances = np.arange(1000, 100000 + 1, 1000)
    def risk_pct(balance):
        b = max(start_balance, min(balance, end_balance))
        return 0.10 - ((b - start_balance) / (end_balance - start_balance)) * (0.10 - 0.025)
    risk_curve = pd.DataFrame({
        "Balance": balances,
        "Allowed Risk %": [risk_pct(b) * 100 for b in balances]
    }).set_index("Balance")
    st.line_chart(risk_curve, use_container_width=True)
    st.caption("Allowed risk % decreases linearly from 10% at 1,000 to 2.5% at 100,000")

# ---------------------------
# Insights & Recommendations
# ---------------------------
st.markdown("---")
st.subheader("💡 Insights & Recommendations")

if theoretical_max_risk_percentage > allowed_risk_percentage or margin_usage_percentage > 50:
    st.write("""
    **To reduce risk and margin usage:**
    - Reduce number of layers
    - Reduce trades per layer
    - Use smaller lot size
    - Increase distance to SL (if it fits your strategy)
    - Consider higher leverage **carefully** (this increases risk)
    - Re-check pip value and lot sizing with your broker
    """)
else:
    st.write("""
    **Risk and margin management looks acceptable. Remember:**
    - Average profit shown is computed only across closed (opened) trades in the simulation.
    - Use stop-loss orders, and consider moving SL to breakeven where appropriate.
    - Keep margin usage below ~30% for safety.
    """)

# Refresh button
if st.button("🔄 Refresh Live Prices"):
    st.cache_data.clear()
    st.experimental_rerun()

st.markdown("---")
st.caption(f"**Disclaimer:** Live prices from Yahoo Finance. This calculator provides estimates only. "
           f"Always verify pip values and margin requirements with your broker. Prices updated: {live_prices['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
