# Clearing Simulation Visualizer

An interactive web-based dashboard for visualizing and analyzing clearing simulation results.

## Features

- **Interactive Time Series Analysis**: Track system metrics over multiple simulation days
- **Client Analytics**: Wealth distribution, margin call analysis, and liquidity tracking
- **Clearing Member Comparison**: Compare performance across different clearing members
- **Trade Analysis**: View proposed vs accepted trades with acceptance rate tracking
- **Portfolio Visualization**: Analyze client positions at start and end of day
- **Multi-stage View**: Navigate through different simulation stages
- **🆕 Client Debug Calculator**: Manually verify and debug PnL, margin, shortfall, and wealth calculations for individual clients ([Learn more](CLIENT_DEBUG_CALCULATOR.md))

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Generating Simulation Data

Before using the visualizer, you need simulation output data. You have two options:

### Option 1: Run the Actual Simulation

From the parent directory (clearing_simulation):
```bash
python clearing_simulation.py --output visualizer/simulation_output.json --days 30
```

This will run the clearing simulation and save the output to a JSON file.

### Option 2: Generate Sample Data (for testing)

If you just want to test the visualizer without running a full simulation:
```bash
cd visualizer
python generate_sample_data.py
```

This creates a `sample_simulation_output.json` file with mock data.

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## How to Use

1. **Upload Data**: Click "Browse files" in the sidebar to upload your simulation output JSON file
   - Note: The files in `models/run_1/` are model training metrics, not simulation output
   - You need to run the simulation first (see "Generating Simulation Data" above)
2. **Select Day**: Use the slider to navigate through different simulation days
3. **Choose View**: Click on different view tabs to explore:
   - **Overview**: High-level metrics and visualizations
   - **Market State**: Current market conditions
   - **Proposed Trades**: All trade proposals
   - **Accepted Trades**: Successfully accepted trades
   - **Margin Calls**: Margin call analysis and client status
   - **PnL & Returns**: Profit/loss and return calculations
   - **Portfolios**: Client portfolio positions
   - **Time Series Analysis**: Multi-day trends and patterns
   - **🆕 Client Debug Calculator**: Manually verify calculations for any client
     - Select a client from the dropdown
     - See step-by-step PnL calculation (portfolio × returns)
     - Review margin calculation (Expected Shortfall with configurable α)
     - Analyze shortfall and margin calls
     - Track wealth evolution
     - Compare calculated vs reported values
     - See [full documentation](CLIENT_DEBUG_CALCULATOR.md)

## Data Format

The visualizer expects JSON files with the following structure:

```json
{
  "metrics": [
    {
      "market_index": 0,
      "system": {
        "total_client_collateral": 1000000,
        "avg_client_collateral": 50000,
        "total_cm_funds": 500000,
        "num_active_trades": 100,
        "num_accepted_trades": 85
      },
      "cms": { ... },
      "ccps": { ... },
      "details": { ... }
    }
  ]
}
```

## Visualizations

### Overview Tab
- Client wealth distribution histogram
- Margin call pie chart
- Clearing member comparison bar chart

### Time Series Analysis
- Collateral metrics over time
- CM funds trends
- Trading activity patterns
- Trade acceptance rate evolution

### Individual Stage Views
- Detailed tables with filtering and sorting
- Stage-specific charts and metrics
- CM and CCP summaries

## Customization

You can modify the visualization settings in `app.py`:
- Color schemes in Plotly chart definitions
- Number of histogram bins
- Chart layouts and sizes
- Metrics displayed in overview cards

## Requirements

- Python 3.8+
- streamlit >= 1.28.0
- pandas >= 2.0.0
- plotly >= 5.17.0
- numpy >= 1.24.0

## Troubleshooting

**"No simulation metrics found"**: This means you uploaded model training data instead of simulation output. You need to:
- Run the simulation first: `python clearing_simulation.py --output visualizer/simulation_output.json`
- Or generate sample data: `python generate_sample_data.py`

**File upload issues**: Ensure your JSON file is properly formatted and contains a "metrics" array

**Charts not displaying**: Check that your data contains the expected fields

**Performance issues**: For very large datasets, consider filtering the data before visualization

## Quick Start

```bash
# 1. Navigate to visualizer directory
cd visualizer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate sample data (for testing)
python generate_sample_data.py

# 4. Run the visualizer
streamlit run app.py

# 5. Upload sample_simulation_output.json in the browser
```

## License

This project is part of the clearing simulation suite.
