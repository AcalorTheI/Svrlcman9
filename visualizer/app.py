from __future__ import annotations

import json
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


STAGES = [
    "Overview",
    "Market State",
    "Proposed Trades",
    "Accepted Trades",
    "Margin Calls",
    "PnL & Returns",
    "Portfolios",
    "Time Series Analysis",
]


def _load_payload(uploaded_file) -> Dict[str, Any]:
    """Load and parse JSON payload from uploaded file."""
    raw = uploaded_file.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("utf-8")
    return json.loads(text)


def _metrics_list(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract metrics list from payload."""
    # Handle wrapped metrics format: {"metrics": [...]}
    if isinstance(payload, dict) and "metrics" in payload:
        return payload["metrics"]
    # Handle direct list format: [...]
    if isinstance(payload, list):
        return payload
    # Handle training data format (has 'epoch', 'train_free_energy', etc.)
    if isinstance(payload, dict) and "epoch" in payload:
        return []
    # Handle test metrics format (has 'test_metrics', etc.)
    if isinstance(payload, dict) and "test_metrics" in payload:
        return []
    return []


def _client_table(cms: Dict[str, Any]) -> pd.DataFrame:
    """Build client-level table from CM data."""
    rows: List[Dict[str, Any]] = []
    for cm_name, cm_data in cms.items():
        for client in cm_data.get("clients", []):
            row = {
                "cm": cm_name,
                "client_id": client.get("client_id"),
                "vip_status": client.get("vip_status"),
                "liquidity_status_end": client.get("liquidity_status_end"),
                "wealth_end": client.get("wealth_end"),
                "collateral_end": client.get("collateral_end"),
                "margin": client.get("margin"),
                "shortfall": client.get("shortfall"),
                "pnl": client.get("pnl"),
                "income_applied": client.get("income_applied"),
            }
            margin_call = client.get("margin_call", {})
            row["margin_called"] = margin_call.get("called")
            row["margin_call_amount"] = margin_call.get("amount")
            row["margin_call_accepted"] = margin_call.get("accepted")
            row["margin_call_liquidated"] = margin_call.get("liquidated")
            rows.append(row)
    return pd.DataFrame(rows)


def _cm_table(cms: Dict[str, Any]) -> pd.DataFrame:
    """Build clearing member table."""
    rows = []
    for name, data in cms.items():
        rows.append(
            {
                "cm": name,
                "cm_funds": data.get("cm_funds"),
                "cm_pnl": data.get("cm_pnl"),
                "default_shortfall": data.get("default_shortfall"),
                "total_client_collateral": data.get("total_client_collateral"),
                "avg_client_collateral": data.get("avg_client_collateral"),
                "min_client_collateral": data.get("min_client_collateral"),
                "avg_client_margin": data.get("avg_client_margin"),
                "total_client_margin": data.get("total_client_margin"),
                "num_active_trades": data.get("num_active_trades"),
                "num_accepted_trades": data.get("num_accepted_trades"),
                "num_zero_collateral_clients": data.get("num_zero_collateral_clients"),
            }
        )
    return pd.DataFrame(rows)


def _ccp_table(ccps: Dict[str, Any]) -> pd.DataFrame:
    """Build CCP table."""
    rows = []
    for name, data in ccps.items():
        rows.append(
            {
                "ccp": name,
                "ccp_margin": data.get("ccp_margin"),
                "cm_margins": data.get("cm_margins"),
                "cm_funds": data.get("cm_funds"),
                "cm_shortfalls": data.get("cm_shortfalls"),
            }
        )
    return pd.DataFrame(rows)


def _trades_table(cms: Dict[str, Any], accepted_only: bool) -> pd.DataFrame:
    """Build trades table."""
    rows: List[Dict[str, Any]] = []
    for cm_name, cm_data in cms.items():
        for client in cm_data.get("clients", []):
            for trade in client.get("trades", []):
                if accepted_only and not trade.get("accepted", False):
                    continue
                rows.append(
                    {
                        "cm": cm_name,
                        "client_id": client.get("client_id"),
                        "instrument": trade.get("instrument"),
                        "amount": trade.get("amount"),
                        "accepted": trade.get("accepted"),
                    }
                )
    return pd.DataFrame(rows)


def _portfolio_table(cms: Dict[str, Any], key: str) -> pd.DataFrame:
    """Build portfolio table."""
    rows: List[Dict[str, Any]] = []
    for cm_name, cm_data in cms.items():
        for client in cm_data.get("clients", []):
            portfolio = client.get(key)
            if portfolio is None:
                continue
            for idx, value in enumerate(portfolio):
                rows.append(
                    {
                        "cm": cm_name,
                        "client_id": client.get("client_id"),
                        "instrument": idx,
                        "position": value,
                    }
                )
    return pd.DataFrame(rows)


def _plot_system_metrics_over_time(metrics: List[Dict[str, Any]]) -> go.Figure:
    """Create time series plot of system-level metrics."""
    days = list(range(len(metrics)))

    total_collateral = [m.get("system", {}).get("total_client_collateral", 0) for m in metrics]
    avg_collateral = [m.get("system", {}).get("avg_client_collateral", 0) for m in metrics]
    total_cm_funds = [m.get("system", {}).get("total_cm_funds", 0) for m in metrics]
    active_trades = [m.get("system", {}).get("num_active_trades", 0) for m in metrics]
    accepted_trades = [m.get("system", {}).get("num_accepted_trades", 0) for m in metrics]

    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("Collateral Metrics", "CM Funds", "Trading Activity"),
        vertical_spacing=0.12,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]]
    )

    # Collateral metrics
    fig.add_trace(
        go.Scatter(x=days, y=total_collateral, name="Total Collateral",
                   line=dict(color="royalblue", width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=days, y=avg_collateral, name="Avg Collateral",
                   line=dict(color="lightblue", width=2)),
        row=1, col=1
    )

    # CM Funds
    fig.add_trace(
        go.Scatter(x=days, y=total_cm_funds, name="Total CM Funds",
                   line=dict(color="green", width=2)),
        row=2, col=1
    )

    # Trading Activity
    fig.add_trace(
        go.Scatter(x=days, y=active_trades, name="Active Trades",
                   line=dict(color="orange", width=2)),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=days, y=accepted_trades, name="Accepted Trades",
                   line=dict(color="darkgreen", width=2)),
        row=3, col=1
    )

    fig.update_xaxes(title_text="Day", row=3, col=1)
    fig.update_yaxes(title_text="Amount", row=1, col=1)
    fig.update_yaxes(title_text="Funds", row=2, col=1)
    fig.update_yaxes(title_text="Count", row=3, col=1)

    fig.update_layout(height=900, showlegend=True)

    return fig


def _plot_client_wealth_distribution(cms: Dict[str, Any]) -> go.Figure:
    """Plot distribution of client wealth."""
    client_df = _client_table(cms)
    if client_df.empty:
        return go.Figure()

    fig = px.histogram(
        client_df,
        x="wealth_end",
        nbins=30,
        title="Client Wealth Distribution",
        labels={"wealth_end": "Wealth at End of Day"},
        color_discrete_sequence=["steelblue"]
    )
    fig.update_layout(showlegend=False)
    return fig


def _plot_margin_call_analysis(cms: Dict[str, Any]) -> go.Figure:
    """Visualize margin call statistics."""
    client_df = _client_table(cms)
    if client_df.empty:
        return go.Figure()

    margin_called_count = client_df["margin_called"].sum() if "margin_called" in client_df else 0
    total_clients = len(client_df)

    labels = ["Margin Called", "No Margin Call"]
    values = [margin_called_count, total_clients - margin_called_count]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
    fig.update_layout(title_text="Margin Calls Distribution")

    return fig


def _plot_cm_comparison(cms: Dict[str, Any]) -> go.Figure:
    """Compare clearing members across key metrics."""
    cm_df = _cm_table(cms)
    if cm_df.empty:
        return go.Figure()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=cm_df["cm"],
        y=cm_df["cm_funds"],
        name="CM Funds",
        marker_color="lightblue"
    ))

    fig.add_trace(go.Bar(
        x=cm_df["cm"],
        y=cm_df["total_client_collateral"],
        name="Total Client Collateral",
        marker_color="steelblue"
    ))

    fig.update_layout(
        title="Clearing Member Comparison",
        xaxis_title="Clearing Member",
        yaxis_title="Amount",
        barmode="group"
    )

    return fig


def _plot_trade_acceptance_rate(metrics: List[Dict[str, Any]]) -> go.Figure:
    """Plot trade acceptance rate over time."""
    days = list(range(len(metrics)))

    acceptance_rates = []
    for m in metrics:
        active = m.get("system", {}).get("num_active_trades", 0)
        accepted = m.get("system", {}).get("num_accepted_trades", 0)
        rate = (accepted / active * 100) if active > 0 else 0
        acceptance_rates.append(rate)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days,
        y=acceptance_rates,
        mode="lines+markers",
        name="Acceptance Rate",
        line=dict(color="purple", width=2),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title="Trade Acceptance Rate Over Time",
        xaxis_title="Day",
        yaxis_title="Acceptance Rate (%)",
        yaxis=dict(range=[0, 105])
    )

    return fig


def main() -> None:
    st.set_page_config(page_title="Clearing Simulation Visualizer", layout="wide")

    st.title("Clearing Simulation Visualizer")
    st.markdown("Interactive dashboard for analyzing clearing simulation results")

    with st.sidebar:
        st.header("Configuration")
        uploaded = st.file_uploader("Upload metrics.json or history.json", type=["json"])
        st.markdown("---")

        if uploaded:
            st.success(f"Loaded: {uploaded.name}")

        st.markdown("---")
        show_raw = st.checkbox("Show raw JSON", value=False)

        st.markdown("---")
        st.markdown("### About")
        st.markdown("This tool visualizes clearing simulation data with interactive charts and analysis.")

    if not uploaded:
        st.info("Upload a metrics.json or history.json file to begin visualization.")
        st.markdown("### Features")
        st.markdown("""
        - Interactive time series analysis
        - Client wealth and margin call analytics
        - Clearing member comparisons
        - Trade acceptance tracking
        - Portfolio position analysis
        - Detailed stage-by-stage views
        """)
        return

    payload = _load_payload(uploaded)
    metrics = _metrics_list(payload)

    if not metrics:
        st.error("No simulation metrics found in uploaded file.")
        st.warning("""
        This file appears to be training/model metrics, not clearing simulation output.

        To generate simulation data:
        1. Run the clearing simulation: `python clearing_simulation.py --output simulation_output.json`
        2. Upload the generated `simulation_output.json` file here

        Expected file format: `{"metrics": [{"day": 0, "system": {...}, "cms": {...}, "ccps": {...}}, ...]}`
        """)

        # Show what kind of file was uploaded
        if isinstance(payload, dict):
            st.info(f"Detected file type: {', '.join(list(payload.keys())[:5])}")
        return

    day_count = len(metrics)

    # Day selector
    day_index = st.slider("Select Day", min_value=0, max_value=day_count - 1, value=0, step=1)

    # Stage selector
    stage = st.radio("View", STAGES, horizontal=True)

    day_data = metrics[day_index]
    system = day_data.get("system", {})
    cms = day_data.get("cms", {})
    ccps = day_data.get("ccps", {})
    details = day_data.get("details", {})

    # Debug info (optional - can be removed later)
    with st.expander("Debug Info (click to expand)"):
        st.write(f"Selected stage: {stage}")
        st.write(f"Day data keys: {list(day_data.keys())}")
        st.write(f"Number of CMs: {len(cms)}")
        st.write(f"System metrics available: {bool(system)}")

    # Overview Section
    if stage == "Overview":
        st.subheader(f"Day {day_index} Overview")

        cols = st.columns(5)
        cols[0].metric("Total Collateral", f"{system.get('total_client_collateral', 0):,.2f}")
        cols[1].metric("Avg Collateral", f"{system.get('avg_client_collateral', 0):,.2f}")
        cols[2].metric("Total CM Funds", f"{system.get('total_cm_funds', 0):,.2f}")
        cols[3].metric("Active Trades", system.get("num_active_trades", 0))
        cols[4].metric("Accepted Trades", system.get("num_accepted_trades", 0))

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            try:
                fig1 = _plot_client_wealth_distribution(cms)
                if fig1 and fig1.data:
                    st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.info("No client wealth data available for this day")
            except Exception as e:
                st.error(f"Error plotting wealth distribution: {str(e)}")

            try:
                fig2 = _plot_cm_comparison(cms)
                if fig2 and fig2.data:
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No CM comparison data available")
            except Exception as e:
                st.error(f"Error plotting CM comparison: {str(e)}")

        with col2:
            try:
                fig3 = _plot_margin_call_analysis(cms)
                if fig3 and fig3.data:
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.info("No margin call data available")
            except Exception as e:
                st.error(f"Error plotting margin calls: {str(e)}")

    elif stage == "Market State":
        st.subheader("Market State")

        col1, col2 = st.columns(2)
        col1.metric("Market Index", day_data.get("market_index", "N/A"))

        market_state = details.get("market_state", [])
        if market_state:
            st.write("Market State Values:")
            market_df = pd.DataFrame({"Instrument": range(len(market_state)), "Value": market_state})
            st.dataframe(market_df, use_container_width=True)

            fig = px.line(market_df, x="Instrument", y="Value", title="Market State by Instrument")
            st.plotly_chart(fig, use_container_width=True)

    elif stage == "Proposed Trades":
        st.subheader("Proposed Trades")
        trades_df = _trades_table(cms, accepted_only=False)
        st.dataframe(trades_df, use_container_width=True)

        if not trades_df.empty:
            fig = px.histogram(trades_df, x="instrument", title="Trade Distribution by Instrument")
            st.plotly_chart(fig, use_container_width=True)

    elif stage == "Accepted Trades":
        st.subheader("Accepted Trades")
        trades_df = _trades_table(cms, accepted_only=True)
        st.dataframe(trades_df, use_container_width=True)

        if not trades_df.empty:
            fig = px.scatter(trades_df, x="instrument", y="amount", color="cm",
                           title="Accepted Trades by CM")
            st.plotly_chart(fig, use_container_width=True)

    elif stage == "Margin Calls":
        st.subheader("Margin Calls")
        client_df = _client_table(cms)
        st.dataframe(client_df, use_container_width=True)

        if not client_df.empty and "margin_called" in client_df.columns:
            margin_called_df = client_df[client_df["margin_called"] == True]
            st.write(f"Total margin calls: {len(margin_called_df)} out of {len(client_df)} clients")

    elif stage == "PnL & Returns":
        st.subheader("PnL & Returns")
        client_df = _client_table(cms)
        st.dataframe(client_df, use_container_width=True)

        real_returns = details.get("real_returns", [])
        if real_returns:
            st.write("Real Returns:")
            returns_df = pd.DataFrame({"Instrument": range(len(real_returns)), "Return": real_returns})
            st.dataframe(returns_df, use_container_width=True)

            fig = px.bar(returns_df, x="Instrument", y="Return", title="Real Returns by Instrument")
            st.plotly_chart(fig, use_container_width=True)

    elif stage == "Portfolios":
        st.subheader("Client Portfolios")

        st.write("Portfolios at Start of Day:")
        portfolio_start = _portfolio_table(cms, "portfolio_start")
        st.dataframe(portfolio_start, use_container_width=True)

        st.write("Portfolios at End of Day:")
        portfolio_end = _portfolio_table(cms, "portfolio_end")
        st.dataframe(portfolio_end, use_container_width=True)

    elif stage == "Time Series Analysis":
        st.subheader("Time Series Analysis")

        if day_count > 1:
            st.plotly_chart(_plot_system_metrics_over_time(metrics), use_container_width=True)
            st.plotly_chart(_plot_trade_acceptance_rate(metrics), use_container_width=True)
        else:
            st.info("Time series analysis requires multiple days of data.")

    # Always show CM and CCP summaries at bottom
    if stage not in ["Overview", "Time Series Analysis"]:
        st.markdown("---")
        st.subheader("CM Summary")
        st.dataframe(_cm_table(cms), use_container_width=True)

        st.subheader("CCP Summary")
        st.dataframe(_ccp_table(ccps), use_container_width=True)

    if show_raw:
        st.markdown("---")
        st.subheader("Raw JSON")
        st.json(day_data)


if __name__ == "__main__":
    main()
