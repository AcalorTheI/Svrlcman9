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
    "Client Debug Calculator",
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


def _calculate_pnl_manual(portfolio: List[float], returns: List[float]) -> float:
    """Manually calculate PnL as dot product of portfolio and returns."""
    if not portfolio or not returns or len(portfolio) != len(returns):
        return 0.0
    return sum(p * r for p, r in zip(portfolio, returns))


def _calculate_margin_manual(portfolio: List[float], scenarios: List[List[float]], alpha: float = 0.99) -> Dict[str, Any]:
    """
    Manually calculate Expected Shortfall (ES) margin.

    Returns dict with:
    - margin: the ES value
    - var: Value at Risk
    - losses: all loss values
    - tail_losses: losses in the tail
    """
    if not portfolio or not scenarios:
        return {"margin": 0.0, "var": 0.0, "losses": [], "tail_losses": []}

    # Calculate losses for each scenario (negative PnL)
    losses = []
    for scenario in scenarios:
        pnl = sum(p * r for p, r in zip(portfolio, scenario))
        loss = -pnl  # Loss is negative of PnL
        losses.append(loss)

    # Sort losses
    sorted_losses = sorted(losses)

    # Calculate VaR (Value at Risk) at alpha quantile
    var_index = int(alpha * len(sorted_losses))
    var = sorted_losses[var_index] if var_index < len(sorted_losses) else sorted_losses[-1]

    # Calculate ES (Expected Shortfall) - average of losses >= VaR
    tail_losses = [l for l in sorted_losses if l >= var]
    es = sum(tail_losses) / len(tail_losses) if tail_losses else var

    return {
        "margin": es,
        "var": var,
        "losses": sorted_losses,
        "tail_losses": tail_losses,
        "num_scenarios": len(scenarios),
        "tail_count": len(tail_losses),
    }


def _get_client_details(cms: Dict[str, Any], cm_name: str, client_id: int) -> Dict[str, Any]:
    """Extract detailed client information for debugging."""
    cm_data = cms.get(cm_name, {})
    for client in cm_data.get("clients", []):
        if client.get("client_id") == client_id:
            return client
    return {}


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

    elif stage == "Client Debug Calculator":
        st.subheader("Client Debug Calculator")
        st.markdown("**Manually verify PnL, margin, and wealth calculations for any client**")

        # Get all clients for selection
        client_options = []
        for cm_name, cm_data in cms.items():
            for client in cm_data.get("clients", []):
                client_id = client.get("client_id")
                client_options.append(f"{cm_name} - Client {client_id}")

        if not client_options:
            st.warning("No clients found in this day's data.")
        else:
            selected = st.selectbox("Select Client to Debug", client_options)

            if selected:
                # Parse selection
                cm_name, client_part = selected.split(" - Client ")
                client_id = int(client_part)

                # Get client details
                client = _get_client_details(cms, cm_name, client_id)

                if not client:
                    st.error("Client not found")
                else:
                    # Display client overview
                    st.markdown("---")
                    st.markdown("### Client Overview")

                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Client ID", client_id)
                    col2.metric("VIP Status", client.get("vip_status", "N/A"))
                    col3.metric("Liquidity Status", client.get("liquidity_status_end", "N/A"))
                    col4.metric("CM", cm_name)

                    # Get data for calculations
                    portfolio_start = client.get("portfolio_start", [])
                    portfolio_end = client.get("portfolio_end", [])
                    real_returns = details.get("real_returns", [])
                    scenarios = details.get("scenarios", [])

                    # Section 1: PnL Calculation
                    st.markdown("---")
                    st.markdown("### 1. PnL Calculation Breakdown")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Portfolio at Start**")
                        portfolio_df = pd.DataFrame({
                            "Instrument": range(len(portfolio_start)),
                            "Position": portfolio_start
                        })
                        st.dataframe(portfolio_df, use_container_width=True)

                    with col2:
                        st.markdown("**Real Returns**")
                        if real_returns:
                            returns_df = pd.DataFrame({
                                "Instrument": range(len(real_returns)),
                                "Return": real_returns
                            })
                            st.dataframe(returns_df, use_container_width=True)
                        else:
                            st.warning("No real returns data available")

                    # Calculate PnL manually
                    if real_returns and portfolio_start:
                        calculated_pnl = _calculate_pnl_manual(portfolio_start, real_returns)
                        reported_pnl = client.get("pnl", 0.0)

                        st.markdown("**PnL Calculation:**")
                        st.code(f"PnL = Σ(position[i] × return[i])")

                        # Show detailed calculation
                        calc_details = []
                        for i, (pos, ret) in enumerate(zip(portfolio_start, real_returns)):
                            contrib = pos * ret
                            calc_details.append({
                                "Instrument": i,
                                "Position": pos,
                                "Return": ret,
                                "Contribution": contrib
                            })

                        calc_df = pd.DataFrame(calc_details)
                        st.dataframe(calc_df, use_container_width=True)

                        col1, col2, col3 = st.columns(3)
                        col1.metric("Calculated PnL", f"{calculated_pnl:.4f}")
                        col2.metric("Reported PnL", f"{reported_pnl:.4f}")
                        diff = abs(calculated_pnl - reported_pnl)
                        col3.metric("Difference", f"{diff:.6f}", delta=None if diff < 0.01 else f"⚠️ {diff:.6f}")

                        if diff < 0.01:
                            st.success("✅ PnL calculation matches!")
                        else:
                            st.warning(f"⚠️ PnL difference: {diff:.6f}")

                    # Section 2: Margin Calculation
                    st.markdown("---")
                    st.markdown("### 2. Margin Calculation Breakdown")

                    alpha = st.slider("Alpha (confidence level)", min_value=0.90, max_value=0.99, value=0.99, step=0.01)

                    if scenarios and portfolio_end:
                        st.markdown(f"**Using {len(scenarios)} scenarios for Expected Shortfall (ES) calculation**")

                        margin_calc = _calculate_margin_manual(portfolio_end, scenarios, alpha)

                        calculated_margin = margin_calc["margin"]
                        reported_margin = client.get("margin", 0.0)

                        st.markdown("**Margin Calculation Process:**")
                        st.code(f"""
1. Calculate PnL for each scenario
2. Convert to losses (loss = -PnL)
3. Sort losses
4. Find VaR at {alpha} quantile
5. ES = Average of losses >= VaR
                        """)

                        col1, col2, col3 = st.columns(3)
                        col1.metric("VaR", f"{margin_calc['var']:.4f}")
                        col2.metric("Calculated Margin (ES)", f"{calculated_margin:.4f}")
                        col3.metric("Reported Margin", f"{reported_margin:.4f}")

                        col1, col2 = st.columns(2)
                        col1.metric("Num Scenarios", margin_calc["num_scenarios"])
                        col2.metric("Tail Count", margin_calc["tail_count"])

                        diff = abs(calculated_margin - reported_margin)
                        if diff < 0.01:
                            st.success("✅ Margin calculation matches!")
                        else:
                            st.warning(f"⚠️ Margin difference: {diff:.4f}")

                        # Detailed line-by-line scenario calculations
                        with st.expander("📊 View Line-by-Line Scenario Calculations"):
                            st.markdown("**Step 1: Calculate PnL and Loss for Each Scenario**")

                            # Build detailed scenario table
                            scenario_details = []
                            for i, scenario in enumerate(scenarios):
                                # Calculate PnL for this scenario
                                pnl = sum(p * r for p, r in zip(portfolio_end, scenario))
                                loss = -pnl

                                # Check if in tail
                                in_tail = loss >= margin_calc['var']

                                scenario_details.append({
                                    "Scenario #": i,
                                    "PnL": f"{pnl:.6f}",
                                    "Loss (-PnL)": f"{loss:.6f}",
                                    "In Tail (≥VaR)": "✓" if in_tail else "",
                                })

                            scenario_df = pd.DataFrame(scenario_details)
                            st.dataframe(scenario_df, use_container_width=True, height=400)

                            st.markdown("**Step 2: Sorted Losses**")
                            sorted_detail = []
                            for i, loss in enumerate(margin_calc["losses"]):
                                is_var = (i == int(alpha * len(margin_calc["losses"])))
                                in_tail = loss >= margin_calc['var']

                                sorted_detail.append({
                                    "Rank": i,
                                    "Loss": f"{loss:.6f}",
                                    "Percentile": f"{(i / len(margin_calc['losses']) * 100):.2f}%",
                                    "VaR Level": "← VaR" if is_var else "",
                                    "In Tail": "✓" if in_tail else "",
                                })

                            sorted_df = pd.DataFrame(sorted_detail)
                            st.dataframe(sorted_df, use_container_width=True, height=400)

                            st.markdown("**Step 3: Tail Statistics**")
                            st.code(f"""
VaR Index: {int(alpha * len(margin_calc['losses']))}
VaR Value: {margin_calc['var']:.6f}
Tail Count: {margin_calc['tail_count']} scenarios
Tail Losses: {[f"{l:.4f}" for l in margin_calc['tail_losses'][:10]]}{'...' if len(margin_calc['tail_losses']) > 10 else ''}
ES (Average of tail): {calculated_margin:.6f}
                            """)

                        # Show loss distribution
                        with st.expander("📈 View Loss Distribution Chart"):
                            losses_df = pd.DataFrame({
                                "Scenario": range(len(margin_calc["losses"])),
                                "Loss": margin_calc["losses"]
                            })

                            fig = px.histogram(
                                losses_df,
                                x="Loss",
                                nbins=50,
                                title="Loss Distribution"
                            )
                            fig.add_vline(x=margin_calc["var"], line_dash="dash", line_color="red",
                                        annotation_text=f"VaR ({alpha})")
                            fig.add_vline(x=calculated_margin, line_dash="dash", line_color="green",
                                        annotation_text="ES (Margin)")
                            st.plotly_chart(fig, use_container_width=True)

                        # Detailed instrument contribution to each scenario
                        with st.expander("🔍 View Instrument Contributions by Scenario (First 20 scenarios)"):
                            st.markdown("**See how each instrument contributes to PnL in each scenario**")

                            scenario_limit = min(20, len(scenarios))
                            instrument_contrib_data = []

                            for scenario_idx in range(scenario_limit):
                                scenario = scenarios[scenario_idx]
                                total_pnl = 0

                                for inst_idx, (pos, ret) in enumerate(zip(portfolio_end, scenario)):
                                    contrib = pos * ret
                                    total_pnl += contrib

                                    instrument_contrib_data.append({
                                        "Scenario": scenario_idx,
                                        "Instrument": inst_idx,
                                        "Position": f"{pos:.4f}",
                                        "Return": f"{ret:.6f}",
                                        "Contribution": f"{contrib:.6f}",
                                    })

                                # Add total row for this scenario
                                instrument_contrib_data.append({
                                    "Scenario": scenario_idx,
                                    "Instrument": "TOTAL",
                                    "Position": "",
                                    "Return": "",
                                    "Contribution": f"{total_pnl:.6f}",
                                })

                            contrib_df = pd.DataFrame(instrument_contrib_data)
                            st.dataframe(contrib_df, use_container_width=True, height=600)

                    else:
                        st.warning("No scenarios data available for margin calculation")

                    # Section 3: Shortfall and Margin Call
                    st.markdown("---")
                    st.markdown("### 3. Shortfall & Margin Call")

                    reported_collateral = client.get("collateral_end", 0.0)
                    reported_margin = client.get("margin", 0.0)
                    reported_shortfall = client.get("shortfall", 0.0)

                    calculated_shortfall = max(0.0, reported_margin - reported_collateral)

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Collateral", f"{reported_collateral:.4f}")
                    col2.metric("Margin Required", f"{reported_margin:.4f}")
                    col3.metric("Shortfall", f"{reported_shortfall:.4f}")

                    st.code(f"Shortfall = max(0, Margin - Collateral) = max(0, {reported_margin:.4f} - {reported_collateral:.4f}) = {calculated_shortfall:.4f}")

                    diff = abs(calculated_shortfall - reported_shortfall)
                    if diff < 0.01:
                        st.success("✅ Shortfall calculation matches!")
                    else:
                        st.warning(f"⚠️ Shortfall difference: {diff:.4f}")

                    # Margin call details
                    margin_call = client.get("margin_call", {})
                    if margin_call.get("called"):
                        st.markdown("**Margin Call Details:**")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Called", "Yes" if margin_call.get("called") else "No")
                        col2.metric("Amount", f"{margin_call.get('amount', 0):.4f}")
                        col3.metric("Accepted", "Yes" if margin_call.get("accepted") else "No")

                        if margin_call.get("liquidated"):
                            st.error("⚠️ Client was liquidated")

                    # Section 4: Portfolio Evolution
                    st.markdown("---")
                    st.markdown("### 4. Portfolio Evolution & Trades")

                    # Show trades if any
                    trades = client.get("trades", [])
                    if trades:
                        st.markdown("**📋 Trades Executed This Day:**")

                        trade_details = []
                        for idx, t in enumerate(trades):
                            trade_details.append({
                                "Trade #": idx,
                                "Instrument": t.get("instrument", "N/A"),
                                "Amount": f"{t.get('amount', 0):.4f}",
                                "Accepted": "✓ Yes" if t.get("accepted") else "✗ No",
                            })

                        trades_df = pd.DataFrame(trade_details)
                        st.dataframe(trades_df, use_container_width=True)

                        # Trade-by-trade impact analysis
                        with st.expander("🔍 View Trade-by-Trade Impact Analysis"):
                            st.markdown("**See how each trade changes the portfolio, margin, and expected PnL**")

                            # Simulate applying trades one by one
                            current_portfolio = portfolio_start.copy()
                            trade_impacts = []

                            # Initial state
                            if scenarios:
                                initial_margin_calc = _calculate_margin_manual(current_portfolio, scenarios, alpha)
                                initial_margin = initial_margin_calc["margin"]
                            else:
                                initial_margin = 0.0

                            trade_impacts.append({
                                "State": "Initial (before trades)",
                                "Trade": "",
                                "Instrument": "",
                                "Amount": "",
                                "Portfolio (affected inst)": "",
                                "Margin": f"{initial_margin:.4f}",
                                "Margin Change": "",
                            })

                            # Process each accepted trade
                            for idx, trade in enumerate(trades):
                                if not trade.get("accepted"):
                                    continue

                                inst = trade.get("instrument")
                                amount = trade.get("amount", 0)

                                # Before trade
                                pos_before = current_portfolio[inst]

                                # Apply trade
                                current_portfolio[inst] += amount

                                # After trade
                                pos_after = current_portfolio[inst]

                                # Calculate new margin
                                if scenarios:
                                    new_margin_calc = _calculate_margin_manual(current_portfolio, scenarios, alpha)
                                    new_margin = new_margin_calc["margin"]
                                    margin_change = new_margin - initial_margin
                                else:
                                    new_margin = 0.0
                                    margin_change = 0.0

                                trade_impacts.append({
                                    "State": f"After Trade {idx}",
                                    "Trade": idx,
                                    "Instrument": inst,
                                    "Amount": f"{amount:+.4f}",
                                    "Portfolio (affected inst)": f"{pos_before:.4f} → {pos_after:.4f}",
                                    "Margin": f"{new_margin:.4f}",
                                    "Margin Change": f"{margin_change:+.4f}",
                                })

                                initial_margin = new_margin

                            trade_impact_df = pd.DataFrame(trade_impacts)
                            st.dataframe(trade_impact_df, use_container_width=True)

                            st.markdown("**Note:** Margin Change is cumulative from the initial state")

                        # Detailed trade impact with full portfolio snapshot
                        with st.expander("📊 View Full Portfolio After Each Trade"):
                            st.markdown("**Complete portfolio evolution through each accepted trade**")

                            # Start with initial portfolio
                            current_portfolio = portfolio_start.copy()
                            full_portfolio_evolution = []

                            # Add initial state for all instruments
                            for inst_idx in range(len(portfolio_start)):
                                full_portfolio_evolution.append({
                                    "Stage": "Initial",
                                    "Trade #": "",
                                    "Instrument": inst_idx,
                                    "Position": f"{portfolio_start[inst_idx]:.4f}",
                                })

                            # Apply each accepted trade
                            accepted_trade_num = 0
                            for idx, trade in enumerate(trades):
                                if not trade.get("accepted"):
                                    continue

                                inst = trade.get("instrument")
                                amount = trade.get("amount", 0)
                                current_portfolio[inst] += amount

                                # Record full portfolio state after this trade
                                for inst_idx in range(len(current_portfolio)):
                                    full_portfolio_evolution.append({
                                        "Stage": f"After Trade {accepted_trade_num}",
                                        "Trade #": accepted_trade_num,
                                        "Instrument": inst_idx,
                                        "Position": f"{current_portfolio[inst_idx]:.4f}",
                                    })

                                accepted_trade_num += 1

                            # Add final state
                            for inst_idx in range(len(portfolio_end)):
                                full_portfolio_evolution.append({
                                    "Stage": "Final",
                                    "Trade #": "",
                                    "Instrument": inst_idx,
                                    "Position": f"{portfolio_end[inst_idx]:.4f}",
                                })

                            full_port_df = pd.DataFrame(full_portfolio_evolution)
                            st.dataframe(full_port_df, use_container_width=True, height=600)

                            st.info("💡 Tip: Use Streamlit's table filtering to focus on specific instruments or stages")

                        # Margin sensitivity per trade
                        if scenarios:
                            with st.expander("📈 View Margin Sensitivity Per Trade"):
                                st.markdown("**How each trade affects the margin requirement**")

                                # Calculate margin impact of each trade
                                current_portfolio = portfolio_start.copy()
                                margin_sensitivity_data = []

                                # Initial margin
                                initial_calc = _calculate_margin_manual(current_portfolio, scenarios, alpha)
                                prev_margin = initial_calc["margin"]

                                margin_sensitivity_data.append({
                                    "State": "Initial",
                                    "Trade": "",
                                    "Instrument": "",
                                    "Trade Amount": "",
                                    "Margin Before": f"{prev_margin:.4f}",
                                    "Margin After": f"{prev_margin:.4f}",
                                    "Margin Δ": "0.0000",
                                    "Margin Δ %": "0.00%",
                                })

                                # Process each accepted trade
                                for idx, trade in enumerate(trades):
                                    if not trade.get("accepted"):
                                        continue

                                    inst = trade.get("instrument")
                                    amount = trade.get("amount", 0)

                                    # Apply trade
                                    current_portfolio[inst] += amount

                                    # Calculate new margin
                                    new_calc = _calculate_margin_manual(current_portfolio, scenarios, alpha)
                                    new_margin = new_calc["margin"]
                                    margin_delta = new_margin - prev_margin
                                    margin_delta_pct = (margin_delta / prev_margin * 100) if prev_margin != 0 else 0

                                    margin_sensitivity_data.append({
                                        "State": f"After Trade {idx}",
                                        "Trade": idx,
                                        "Instrument": inst,
                                        "Trade Amount": f"{amount:+.4f}",
                                        "Margin Before": f"{prev_margin:.4f}",
                                        "Margin After": f"{new_margin:.4f}",
                                        "Margin Δ": f"{margin_delta:+.4f}",
                                        "Margin Δ %": f"{margin_delta_pct:+.2f}%",
                                    })

                                    prev_margin = new_margin

                                margin_sens_df = pd.DataFrame(margin_sensitivity_data)
                                st.dataframe(margin_sens_df, use_container_width=True)

                                # Highlight biggest margin impacts
                                if len(margin_sensitivity_data) > 1:
                                    st.markdown("**Trades with Largest Margin Impact:**")

                                    # Sort by absolute margin delta
                                    sorted_impacts = sorted(
                                        [d for d in margin_sensitivity_data if d["Trade"] != ""],
                                        key=lambda x: abs(float(x["Margin Δ"].replace("+", ""))),
                                        reverse=True
                                    )

                                    if sorted_impacts:
                                        top_3 = sorted_impacts[:3]
                                        for i, impact in enumerate(top_3, 1):
                                            st.write(f"{i}. Trade {impact['Trade']} (Instrument {impact['Instrument']}): {impact['Margin Δ']} ({impact['Margin Δ %']})")

                        # Expected PnL change per trade
                        if real_returns:
                            with st.expander("💰 View Expected PnL Impact Per Trade"):
                                st.markdown("**How each trade would affect PnL given today's realized returns**")

                                current_portfolio = portfolio_start.copy()
                                pnl_impact_data = []

                                # Initial expected PnL
                                initial_expected_pnl = _calculate_pnl_manual(current_portfolio, real_returns)

                                pnl_impact_data.append({
                                    "State": "Initial",
                                    "Trade": "",
                                    "Instrument": "",
                                    "Trade Amount": "",
                                    "Expected PnL": f"{initial_expected_pnl:.4f}",
                                    "PnL Δ from Trade": "",
                                    "Cumulative PnL": f"{initial_expected_pnl:.4f}",
                                })

                                cumulative_pnl = initial_expected_pnl

                                # Process each accepted trade
                                for idx, trade in enumerate(trades):
                                    if not trade.get("accepted"):
                                        continue

                                    inst = trade.get("instrument")
                                    amount = trade.get("amount", 0)

                                    # Calculate PnL impact of this specific trade
                                    # Impact = amount × return[instrument]
                                    trade_pnl_impact = amount * real_returns[inst]

                                    # Apply trade
                                    current_portfolio[inst] += amount

                                    # New expected PnL
                                    new_expected_pnl = _calculate_pnl_manual(current_portfolio, real_returns)
                                    cumulative_pnl = new_expected_pnl

                                    pnl_impact_data.append({
                                        "State": f"After Trade {idx}",
                                        "Trade": idx,
                                        "Instrument": inst,
                                        "Trade Amount": f"{amount:+.4f}",
                                        "Expected PnL": f"{new_expected_pnl:.4f}",
                                        "PnL Δ from Trade": f"{trade_pnl_impact:+.4f}",
                                        "Cumulative PnL": f"{cumulative_pnl:.4f}",
                                    })

                                pnl_impact_df = pd.DataFrame(pnl_impact_data)
                                st.dataframe(pnl_impact_df, use_container_width=True)

                                st.info("💡 'PnL Δ from Trade' shows the incremental PnL from that specific trade given today's returns")

                        # Detailed portfolio change analysis
                        with st.expander("📊 View Detailed Portfolio Changes"):
                            st.markdown("**Line-by-Line Portfolio Evolution**")

                            portfolio_changes = []
                            for i in range(len(portfolio_start)):
                                start_pos = portfolio_start[i]
                                end_pos = portfolio_end[i]
                                change = end_pos - start_pos

                                # Find trades for this instrument
                                trade_amount = 0
                                for t in trades:
                                    if t.get("instrument") == i and t.get("accepted"):
                                        trade_amount += t.get("amount", 0)

                                portfolio_changes.append({
                                    "Instrument": i,
                                    "Start Position": f"{start_pos:.4f}",
                                    "Trade Amount": f"{trade_amount:.4f}",
                                    "End Position": f"{end_pos:.4f}",
                                    "Change": f"{change:.4f}",
                                    "Match": "✓" if abs(change - trade_amount) < 0.01 else "⚠️",
                                })

                            portfolio_change_df = pd.DataFrame(portfolio_changes)
                            st.dataframe(portfolio_change_df, use_container_width=True)

                            st.markdown("**Formula:** `End Position = Start Position + Accepted Trades`")

                    else:
                        st.info("No trades executed for this client on this day")

                        # Still show portfolio comparison
                        with st.expander("📊 View Portfolio Comparison"):
                            portfolio_comparison = []
                            for i in range(len(portfolio_start)):
                                portfolio_comparison.append({
                                    "Instrument": i,
                                    "Start Position": f"{portfolio_start[i]:.4f}",
                                    "End Position": f"{portfolio_end[i]:.4f}",
                                    "Change": f"{portfolio_end[i] - portfolio_start[i]:.4f}",
                                })

                            comp_df = pd.DataFrame(portfolio_comparison)
                            st.dataframe(comp_df, use_container_width=True)

                    # Section 5: Wealth Tracking
                    st.markdown("---")
                    st.markdown("### 5. Wealth Tracking")

                    wealth_start = client.get("start", {}).get("wealth", 0.0)
                    wealth_end = client.get("wealth_end", 0.0)
                    pnl = client.get("pnl", 0.0)
                    income_applied = client.get("income_applied", False)

                    st.markdown("**Wealth Evolution:**")

                    # Try to reconstruct wealth
                    margin_call_amount = margin_call.get("amount", 0) if margin_call.get("accepted") else 0

                    st.code(f"""
Wealth Start: {wealth_start:.4f}
+ PnL:        {pnl:.4f}
+ Income:     {'Applied' if income_applied else 'Not Applied'}
- Margin Call: {margin_call_amount:.4f}
= Wealth End: {wealth_end:.4f}
                    """)

                    col1, col2 = st.columns(2)
                    col1.metric("Wealth Start", f"{wealth_start:.4f}")
                    col2.metric("Wealth End", f"{wealth_end:.4f}")

                    # Detailed wealth calculation table
                    with st.expander("📊 View Line-by-Line Wealth Calculation"):
                        st.markdown("**Step-by-Step Wealth Changes:**")

                        wealth_steps = []

                        # Step 1: Starting wealth
                        running_wealth = wealth_start
                        wealth_steps.append({
                            "Step": "1. Starting Wealth",
                            "Operation": "",
                            "Amount": f"{wealth_start:.4f}",
                            "Running Total": f"{running_wealth:.4f}",
                        })

                        # Step 2: Add PnL
                        running_wealth += pnl
                        wealth_steps.append({
                            "Step": "2. Add PnL",
                            "Operation": "+",
                            "Amount": f"{pnl:.4f}",
                            "Running Total": f"{running_wealth:.4f}",
                        })

                        # Step 3: Add income if applied
                        if income_applied:
                            # We don't have the income amount in the output, but we can note it
                            wealth_steps.append({
                                "Step": "3. Add Income",
                                "Operation": "+",
                                "Amount": "Applied",
                                "Running Total": "Included",
                            })

                        # Step 4: Subtract margin call
                        if margin_call_amount > 0:
                            running_wealth -= margin_call_amount
                            wealth_steps.append({
                                "Step": "4. Subtract Margin Call",
                                "Operation": "-",
                                "Amount": f"{margin_call_amount:.4f}",
                                "Running Total": f"{running_wealth:.4f}",
                            })

                        # Final step
                        wealth_steps.append({
                            "Step": "5. Final Wealth",
                            "Operation": "=",
                            "Amount": "",
                            "Running Total": f"{wealth_end:.4f}",
                        })

                        wealth_df = pd.DataFrame(wealth_steps)
                        st.dataframe(wealth_df, use_container_width=True)

                        # Verification
                        if abs(running_wealth - wealth_end) < 0.01:
                            st.success("✅ Wealth calculation verified!")
                        else:
                            st.warning(f"⚠️ Wealth difference detected. This may be due to income or other factors not shown in detail.")

                    # Collateral evolution
                    with st.expander("📊 View Collateral Evolution"):
                        st.markdown("**Collateral Changes:**")

                        collateral_start = client.get("start", {}).get("collateral", 0.0)
                        collateral_end = client.get("collateral_end", 0.0)

                        collateral_steps = []
                        collateral_steps.append({
                            "Step": "Starting Collateral",
                            "Amount": f"{collateral_start:.4f}",
                        })

                        if margin_call.get("accepted"):
                            collateral_steps.append({
                                "Step": "Add Margin Call Contribution",
                                "Amount": f"+{margin_call.get('amount', 0):.4f}",
                            })

                        collateral_steps.append({
                            "Step": "Ending Collateral",
                            "Amount": f"{collateral_end:.4f}",
                        })

                        collateral_df = pd.DataFrame(collateral_steps)
                        st.dataframe(collateral_df, use_container_width=True)

                    # Section 6: Raw Client Data
                    with st.expander("View Raw Client Data"):
                        st.json(client)

    elif stage == "Time Series Analysis":
        st.subheader("Time Series Analysis")

        if day_count > 1:
            st.plotly_chart(_plot_system_metrics_over_time(metrics), use_container_width=True)
            st.plotly_chart(_plot_trade_acceptance_rate(metrics), use_container_width=True)
        else:
            st.info("Time series analysis requires multiple days of data.")

    # Always show CM and CCP summaries at bottom
    if stage not in ["Overview", "Time Series Analysis", "Client Debug Calculator"]:
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
