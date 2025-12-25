# Line-by-Line Calculation Tables

## Overview

The Client Debug Calculator now includes **detailed line-by-line tables** for every calculation, allowing you to inspect and verify each step of the simulation's financial computations.

## Available Tables

### 1. PnL Contribution Table

**Location:** Section 1 - PnL Calculation Breakdown

**What it shows:**
- Each instrument's position
- Each instrument's return
- Each instrument's contribution to total PnL
- Sum of all contributions = Total PnL

**Columns:**
| Column | Description |
|--------|-------------|
| Instrument | Instrument index (0, 1, 2, ...) |
| Position | Client's position in this instrument |
| Return | Actual return for this instrument this day |
| Contribution | Position × Return |

**Example:**
```
Instrument | Position | Return   | Contribution
0          | 10.0000  | 0.0100   | 0.1000
1          | -5.0000  | -0.0200  | 0.1000
2          | 20.0000  | 0.0150   | 0.3000
                         TOTAL PnL: 0.5000
```

**Usage:** Verify which instruments contributed gains vs losses to the client's PnL.

---

### 2. Scenario-by-Scenario Loss Calculation Table

**Location:** Section 2 - Margin Calculation Breakdown → 📊 View Line-by-Line Scenario Calculations

**What it shows:**
- PnL for every scenario
- Loss (negative of PnL) for every scenario
- Whether each scenario is in the tail (≥ VaR)

**Columns:**
| Column | Description |
|--------|-------------|
| Scenario # | Scenario index |
| PnL | Portfolio · Scenario returns |
| Loss (-PnL) | Negative of PnL |
| In Tail (≥VaR) | ✓ if this loss is in the tail used for ES |

**Example:**
```
Scenario # | PnL       | Loss (-PnL) | In Tail (≥VaR)
0          | 0.0000    | -0.0000     |
1          | -0.3500   | 0.3500      | ✓
2          | 0.4000    | -0.4000     |
3          | -0.4000   | 0.4000      | ✓
4          | 0.0750    | -0.0750     |
```

**Usage:** See which scenarios produced the worst losses and contributed to the ES margin.

---

### 3. Sorted Losses Table

**Location:** Section 2 - Margin Calculation Breakdown → 📊 View Line-by-Line Scenario Calculations

**What it shows:**
- All losses sorted from lowest to highest
- Percentile ranking of each loss
- VaR threshold location
- Which losses are in the tail for ES calculation

**Columns:**
| Column | Description |
|--------|-------------|
| Rank | Position in sorted list (0 = lowest loss) |
| Loss | Loss value |
| Percentile | What % of scenarios have losses ≤ this |
| VaR Level | Marks the VaR threshold |
| In Tail | ✓ if this loss ≥ VaR (used in ES avg) |

**Example (α=0.80):**
```
Rank | Loss      | Percentile | VaR Level | In Tail
0    | -0.4000   | 0.00%      |           |
1    | -0.0750   | 20.00%     |           |
2    | -0.0000   | 40.00%     |           |
3    | 0.3500    | 60.00%     |           |
4    | 0.4000    | 80.00%     | ← VaR     | ✓
```

**Usage:** Understand the loss distribution and identify the VaR/ES cutoff point.

---

### 4. Instrument Contributions by Scenario Table

**Location:** Section 2 - Margin Calculation Breakdown → 🔍 View Instrument Contributions by Scenario

**What it shows:**
- For each scenario (first 20 shown)
- For each instrument
- Position, return, and contribution to PnL
- Total PnL for that scenario

**Columns:**
| Column | Description |
|--------|-------------|
| Scenario | Scenario index |
| Instrument | Instrument index (or "TOTAL") |
| Position | Client's position |
| Return | Scenario return for this instrument |
| Contribution | Position × Return |

**Example:**
```
Scenario | Instrument | Position | Return    | Contribution
0        | 0          | 10.0000  | 0.0100    | 0.1000
0        | 1          | -5.0000  | 0.0200    | -0.1000
0        | TOTAL      |          |           | 0.0000
1        | 0          | 10.0000  | -0.0300   | -0.3000
1        | 1          | -5.0000  | 0.0100    | -0.0500
1        | TOTAL      |          |           | -0.3500
```

**Usage:** Drill down into specific scenarios to see exactly how each instrument contributed to that scenario's PnL.

---

### 5. Portfolio Changes Table

**Location:** Section 4 - Portfolio Evolution & Trades → 📊 View Detailed Portfolio Changes

**What it shows:**
- Starting position for each instrument
- Trade amounts executed
- Ending position for each instrument
- Verification that End = Start + Trades

**Columns:**
| Column | Description |
|--------|-------------|
| Instrument | Instrument index |
| Start Position | Position at beginning of day |
| Trade Amount | Sum of accepted trades for this instrument |
| End Position | Position at end of day |
| Change | End - Start |
| Match | ✓ if Change = Trade Amount |

**Example:**
```
Instrument | Start Position | Trade Amount | End Position | Change   | Match
0          | 10.0000        | 5.0000       | 15.0000      | 5.0000   | ✓
1          | -5.0000        | 0.0000       | -5.0000      | 0.0000   | ✓
2          | 20.0000        | -10.0000     | 10.0000      | -10.0000 | ✓
```

**Usage:** Verify that portfolio changes match accepted trades exactly.

---

### 6. Wealth Evolution Table

**Location:** Section 5 - Wealth Tracking → 📊 View Line-by-Line Wealth Calculation

**What it shows:**
- Step-by-step calculation of wealth changes
- Running total after each operation
- Final wealth verification

**Columns:**
| Column | Description |
|--------|-------------|
| Step | Description of this step |
| Operation | +, -, or = |
| Amount | Amount added/subtracted |
| Running Total | Cumulative wealth after this step |

**Example:**
```
Step                      | Operation | Amount   | Running Total
1. Starting Wealth        |           | 10000.00 | 10000.00
2. Add PnL               | +         | 150.00   | 10150.00
3. Add Income            | +         | Applied  | Included
4. Subtract Margin Call  | -         | 500.00   | 9650.00
5. Final Wealth          | =         |          | 9650.00
```

**Usage:** Track exactly how wealth changed through PnL, income, and margin calls.

---

### 7. Collateral Evolution Table

**Location:** Section 5 - Wealth Tracking → 📊 View Collateral Evolution

**What it shows:**
- Starting collateral
- Margin call contributions (if accepted)
- Ending collateral

**Columns:**
| Column | Description |
|--------|-------------|
| Step | Description of collateral change |
| Amount | Collateral amount |

**Example:**
```
Step                           | Amount
Starting Collateral            | 0.0000
Add Margin Call Contribution   | +500.0000
Ending Collateral             | 500.0000
```

**Usage:** Verify collateral increases when margin calls are accepted.

---

## How to Use These Tables

### Step 1: Identify the Calculation to Verify

Example: "I want to verify the margin calculation for Client 1"

### Step 2: Navigate to the Relevant Section

Go to Section 2 - Margin Calculation Breakdown

### Step 3: Open the Appropriate Table

Click "📊 View Line-by-Line Scenario Calculations"

### Step 4: Inspect the Data

- **Scenario-by-Scenario Table**: See all PnLs and losses
- **Sorted Losses Table**: Find VaR threshold and tail scenarios
- **Instrument Contributions**: Drill into specific worst-case scenarios

### Step 5: Verify the Result

Compare the calculated ES margin with the reported margin. If they match (✅), the calculation is correct!

---

## Common Debugging Workflows

### Workflow 1: "Why is this client's margin so high?"

1. Go to Section 2 - Margin Calculation
2. Open "📊 View Line-by-Line Scenario Calculations"
3. Look at the **Sorted Losses Table**
4. Find scenarios marked "In Tail"
5. Open "🔍 View Instrument Contributions by Scenario"
6. Check those tail scenarios to see which instruments are driving the losses

**Result:** You'll see exactly which instruments in which scenarios created the tail risk.

### Workflow 2: "Did this client's trades execute correctly?"

1. Go to Section 4 - Portfolio Evolution & Trades
2. Check the **Trades Executed This Day** table
3. Open "📊 View Detailed Portfolio Changes"
4. Verify each instrument's change matches the trade amount
5. Look for ✓ in the "Match" column

**Result:** You'll confirm whether portfolio changes match accepted trades.

### Workflow 3: "Where did this client's wealth go?"

1. Go to Section 5 - Wealth Tracking
2. Open "📊 View Line-by-Line Wealth Calculation"
3. Review each step (starting wealth, PnL, income, margin calls)
4. Check the running total after each operation

**Result:** You'll see exactly how wealth evolved through the day.

### Workflow 4: "Which scenario was the worst for this client?"

1. Go to Section 2 - Margin Calculation
2. Open "📊 View Line-by-Line Scenario Calculations"
3. Look at the **Scenario-by-Scenario Table**
4. Sort by "Loss (-PnL)" to find the highest loss
5. Note the scenario number
6. Open "🔍 View Instrument Contributions by Scenario"
7. Find that scenario number in the table
8. See which instruments contributed to the massive loss

**Result:** You'll identify the worst-case scenario and the instruments responsible.

---

## Table Features

### Sortable Columns

All tables in Streamlit are sortable - click column headers to sort by that column.

### Scrollable

Large tables have scroll bars - useful for 100+ scenarios or many instruments.

### Height Limits

Most tables are limited to 400-600px height to prevent page clutter. Use scroll to see all rows.

### Formatted Numbers

All numbers are formatted with 4-6 decimal places for precision.

### Visual Indicators

- ✓ = Match/Success
- ✗ = No/Rejected
- ⚠️ = Warning/Mismatch

---

## Performance Notes

### Large Scenario Sets

If you have 1000+ scenarios, the tables will:
- Show all scenarios (may take a few seconds to render)
- Instrument contributions limited to first 20 scenarios (configurable)

### Many Instruments

If you have 100+ instruments:
- All instruments shown in contribution tables
- Use sort/filter to focus on specific instruments

---

## Customization

You can modify table limits in `app.py`:

```python
# Line 771: Limit scenarios shown in instrument contributions
scenario_limit = min(20, len(scenarios))  # Change 20 to show more

# Line 720: Height of scenario table
st.dataframe(scenario_df, use_container_width=True, height=400)  # Adjust height
```

---

## Example: Complete Margin Verification

**Goal:** Verify margin calculation for Client 1 at α=0.99

**Steps:**

1. Select "CM - Client 1"
2. Set alpha slider to 0.99
3. Note: Calculated Margin = 4054.81, Reported Margin = 4054.81 ✅
4. Open "📊 View Line-by-Line Scenario Calculations"
5. Check **Scenario-by-Scenario Table**:
   - 1000 scenarios total
   - Losses range from -500 to +8000
6. Check **Sorted Losses Table**:
   - VaR at rank 990 (99th percentile) = 5200.00
   - Tail count = 10 scenarios
   - Tail losses: [5200, 5300, 5500, 5600, 5800, 6000, 6200, 6500, 7000, 8000]
7. Calculate ES manually: (5200+5300+...+8000) / 10 = 4054.81 ✅
8. Open "🔍 View Instrument Contributions by Scenario"
9. Find scenarios 990-999 (the tail)
10. See that Instrument 2 has huge negative contribution in these scenarios

**Conclusion:**
- Margin calculation is correct ✅
- High margin is due to tail risk in Instrument 2
- Worst case: Scenario 999 has loss of 8000 due to Instrument 2 losing 80 per unit

---

## Tips

1. **Start broad, then drill down**: Review summary metrics first, then open tables for details
2. **Use expanders wisely**: Keep tables collapsed until needed to avoid information overload
3. **Compare across clients**: Use the same alpha for multiple clients to compare risk profiles
4. **Export data**: Streamlit allows copying table data - select and copy to spreadsheet
5. **Verify calculations**: Use tables to manually reproduce margin/PnL calculations

---

**Happy Debugging! 🔍📊**
