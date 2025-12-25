# Client Debug Calculator

## Overview

The **Client Debug Calculator** is a new interactive tab in the clearing simulation visualizer that allows you to manually verify and debug all financial calculations for individual clients. This tool helps you understand exactly how PnL, margins, shortfalls, and wealth are calculated in the simulation.

## Features

### 1. **PnL (Profit & Loss) Calculation Breakdown**

- **Visual Display**: Shows portfolio positions and real returns side-by-side
- **Step-by-Step Calculation**: Displays each instrument's contribution to PnL
- **Formula**: `PnL = Σ(position[i] × return[i])`
- **Verification**: Compares calculated PnL vs reported PnL from simulation
- **Detailed Table**: Shows position, return, and contribution for each instrument

### 2. **Margin Calculation Breakdown**

- **Method**: Expected Shortfall (ES) at configurable confidence level (α)
- **Interactive Alpha Slider**: Adjust confidence level from 90% to 99%
- **Process Visualization**:
  1. Calculate PnL for each scenario
  2. Convert to losses (loss = -PnL)
  3. Sort losses
  4. Find Value at Risk (VaR) at α quantile
  5. Calculate ES as average of tail losses (losses ≥ VaR)
- **Metrics Displayed**:
  - VaR (Value at Risk)
  - Calculated Margin (ES)
  - Reported Margin
  - Number of scenarios
  - Tail count
- **Loss Distribution Chart**: Interactive histogram showing:
  - Full loss distribution
  - VaR threshold (red dashed line)
  - Expected Shortfall / Margin (green dashed line)

### 3. **Shortfall & Margin Call Analysis**

- **Formula**: `Shortfall = max(0, Margin - Collateral)`
- **Displays**:
  - Current collateral
  - Margin required
  - Calculated vs reported shortfall
- **Margin Call Details**:
  - Whether margin call was made
  - Amount requested
  - Whether client accepted
  - Liquidation status

### 4. **Wealth Tracking**

- **Evolution Display**:
  ```
  Wealth Start
  + PnL
  + Income (if applied)
  - Margin Call (if accepted)
  = Wealth End
  ```
- **Side-by-side comparison**: Start wealth vs End wealth

### 5. **Raw Data Inspector**

- Expandable section showing complete raw JSON data for the selected client
- Useful for debugging edge cases or examining fields not displayed in the UI

## How to Use

### Step 1: Navigate to the Tab

1. Start the visualizer: `streamlit run app.py`
2. Upload your simulation output JSON file
3. Select a day using the day slider
4. Click on **"Client Debug Calculator"** in the view tabs

### Step 2: Select a Client

Use the dropdown to select a client in format: `{CM_NAME} - Client {CLIENT_ID}`

Example: `CM - Client 1`

### Step 3: Review Calculations

The page will automatically display:

1. **Client Overview**: ID, VIP status, liquidity status, clearing member
2. **PnL Breakdown**: Portfolio × Returns with detailed contribution table
3. **Margin Breakdown**: ES calculation with configurable alpha
4. **Shortfall Analysis**: Margin vs collateral comparison
5. **Wealth Tracking**: Complete wealth evolution

### Step 4: Verify Results

Each calculation section includes:
- ✅ **Green checkmark** if calculated value matches reported value (difference < 0.01)
- ⚠️ **Warning** if there's a discrepancy

## Calculation Formulas

### PnL Calculation

```python
PnL = Σ(position[i] × return[i]) for all instruments i
```

**Example:**
```
Portfolio: [10, -5, 20]
Returns:   [0.01, -0.02, 0.015]

PnL = 10×0.01 + (-5)×(-0.02) + 20×0.015
    = 0.10 + 0.10 + 0.30
    = 0.50
```

### Margin Calculation (Expected Shortfall)

```python
For each scenario:
  loss[i] = -(portfolio · scenario[i])

Sort losses in ascending order
VaR = losses[int(α × num_scenarios)]
ES = mean(losses where loss >= VaR)
Margin = ES
```

**Example (α = 0.99):**
```
Portfolio: [10, -5]
5 scenarios → PnLs → Losses (sorted): [-0.4, -0.075, 0.0, 0.35, 0.4]

VaR at 0.80 (80th percentile, index 4) = 0.4
Tail losses (>= 0.4) = [0.4]
ES = mean([0.4]) = 0.4
Margin = 0.4
```

### Shortfall Calculation

```python
Shortfall = max(0, Margin - Collateral)
```

**Example:**
```
Margin:      1000.0
Collateral:   800.0
Shortfall:    200.0  (client needs to post 200 more)
```

### Wealth Evolution

```python
Wealth_end = Wealth_start + PnL + Income - Margin_call_accepted
```

**Example:**
```
Wealth Start:     10000.0
+ PnL:              150.0
+ Income:             0.0  (not applied this day)
- Margin Call:      500.0  (accepted)
= Wealth End:      9650.0
```

## Understanding the Metrics

### Expected Shortfall (ES)

ES is a risk measure that estimates the expected loss in the worst α% of scenarios. For α=0.99:
- We look at the worst 1% of outcomes
- ES is the average loss in that tail
- This is the margin required to cover potential losses with 99% confidence

### Value at Risk (VaR)

VaR is the threshold loss at the α quantile. For α=0.99:
- 99% of scenarios have losses below VaR
- 1% of scenarios have losses at or above VaR
- ES is always ≥ VaR because it's the average of the tail

### Shortfall

Shortfall occurs when a client's margin requirement exceeds their posted collateral:
- **Shortfall = 0**: Client has sufficient collateral
- **Shortfall > 0**: Client must post additional collateral (margin call)

## Common Use Cases

### 1. Debugging PnL Discrepancies

If you notice unexpected PnL values:
1. Navigate to Client Debug Calculator
2. Select the client
3. Review the PnL breakdown table
4. Check which instruments contributed most to PnL
5. Verify portfolio positions match expectations
6. Verify returns are correct

### 2. Understanding Margin Calls

If a client received a margin call:
1. Find the client in the debug calculator
2. Check the **Margin Calculation** section
3. Adjust alpha slider to see how margin changes with confidence level
4. View the loss distribution to understand tail risk
5. Check **Shortfall** section to see the gap between margin and collateral

### 3. Investigating Liquidations

If a client was liquidated:
1. Select the liquidated client
2. Review their **Margin Call Details**
3. Check if the margin call was rejected (client couldn't/wouldn't pay)
4. Review wealth to see if they had insufficient funds
5. Check PnL to see if losses depleted their wealth

### 4. Validating Simulation Logic

To ensure the simulation is calculating correctly:
1. Pick a random client
2. Manually verify each calculation matches
3. All sections should show ✅ checkmarks
4. If warnings appear, investigate the discrepancy

## Technical Details

### Calculation Functions

The following functions power the debug calculator:

- `_calculate_pnl_manual(portfolio, returns)`: Computes dot product
- `_calculate_margin_manual(portfolio, scenarios, alpha)`: Computes ES
- `_get_client_details(cms, cm_name, client_id)`: Extracts client data

### Test Coverage

Run tests with:
```bash
python3 test_calculations_standalone.py
```

This validates:
- PnL calculations
- Margin/ES calculations
- Shortfall calculations
- Wealth evolution logic

## Tips and Best Practices

1. **Start with Simple Clients**: Debug clients with few positions first
2. **Use Raw Data**: When confused, expand "View Raw Client Data" to see everything
3. **Compare Across Days**: Use the day slider to track how a client's metrics evolve
4. **Adjust Alpha**: Try different confidence levels (90%, 95%, 99%) to understand sensitivity
5. **Check Loss Distribution**: The histogram reveals if tail risk is symmetric or skewed

## Troubleshooting

### "No scenarios data available"

The simulation output may not include detailed scenario data. Ensure you're using output generated with `include_details=True` in the simulation config.

### "Margin difference detected"

Small differences (< 0.01) are usually due to floating-point precision. Larger differences may indicate:
- Different alpha values used
- Different scenario sets
- Bug in calculation

### Missing Fields

If certain fields show "N/A" or 0.0, check the raw client data to see what's actually available in your simulation output.

## Future Enhancements

Potential additions:
- Multi-day tracking for a single client
- CM-level aggregation debugging
- Export calculation breakdown to CSV
- Compare multiple clients side-by-side
- Scenario contribution analysis (which scenarios hurt most)

## Feedback

If you find bugs or have suggestions for improvements, please add them to the project issues.

---

**Happy Debugging! 🐛🔍**
