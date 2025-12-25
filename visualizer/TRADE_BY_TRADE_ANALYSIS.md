# Trade-by-Trade Impact Analysis

## Overview

The **Trade-by-Trade Impact Analysis** feature allows you to see exactly how each individual trade affects a client's portfolio, margin requirement, and expected PnL. This provides complete transparency into the incremental changes from trading activity.

## Available Analysis Tables

### 1. 🔍 Trade-by-Trade Impact Analysis (Summary)

**What it shows:**
- How each accepted trade changes the portfolio
- The margin requirement after each trade
- Cumulative margin change from initial state

**Columns:**
| Column | Description |
|--------|-------------|
| State | Stage of portfolio (Initial, After Trade N) |
| Trade | Trade number |
| Instrument | Instrument being traded |
| Amount | Trade amount (+ for buy, - for sell) |
| Portfolio (affected inst) | Before → After position for that instrument |
| Margin | Margin requirement at this state |
| Margin Change | Cumulative change in margin from initial state |

**Example:**
```
State                | Trade | Inst | Amount   | Portfolio       | Margin   | Margin Change
Initial (before)     |       |      |          |                 | 1000.00  |
After Trade 0        | 0     | 2    | +5.0000  | 10.00 → 15.00  | 1250.00  | +250.00
After Trade 1        | 1     | 0    | -3.0000  | 8.00 → 5.00    | 1100.00  | +100.00
After Trade 2        | 2     | 2    | +2.0000  | 15.00 → 17.00  | 1300.00  | +300.00
```

**Usage:** Quick overview of how trades changed the margin requirement.

---

### 2. 📊 Full Portfolio After Each Trade

**What it shows:**
- Complete portfolio snapshot after each accepted trade
- Shows ALL instruments, not just the one being traded
- Tracks evolution from initial → trade 1 → trade 2 → ... → final

**Columns:**
| Column | Description |
|--------|-------------|
| Stage | Portfolio state (Initial, After Trade N, Final) |
| Trade # | Trade number (empty for initial/final) |
| Instrument | Instrument index |
| Position | Position in this instrument at this stage |

**Example:**
```
Stage           | Trade # | Instrument | Position
Initial         |         | 0          | 10.0000
Initial         |         | 1          | -5.0000
Initial         |         | 2          | 20.0000
After Trade 0   | 0       | 0          | 10.0000  (unchanged)
After Trade 0   | 0       | 1          | -5.0000  (unchanged)
After Trade 0   | 0       | 2          | 25.0000  (changed!)
After Trade 1   | 1       | 0          | 7.0000   (changed!)
After Trade 1   | 1       | 1          | -5.0000  (unchanged)
After Trade 1   | 1       | 2          | 25.0000  (unchanged)
Final           |         | 0          | 7.0000
Final           |         | 1          | -5.0000
Final           |         | 2          | 25.0000
```

**Usage:** See the complete portfolio state evolution. Filter by instrument to track a specific instrument through all trades.

---

### 3. 📈 Margin Sensitivity Per Trade

**What it shows:**
- Margin before and after each trade
- Incremental margin change from each specific trade
- Percentage change in margin
- Identifies which trades had the biggest margin impact

**Columns:**
| Column | Description |
|--------|-------------|
| State | Stage description |
| Trade | Trade number |
| Instrument | Instrument being traded |
| Trade Amount | Amount of trade |
| Margin Before | Margin requirement before this trade |
| Margin After | Margin requirement after this trade |
| Margin Δ | Change from this specific trade |
| Margin Δ % | Percentage change |

**Example:**
```
State          | Trade | Inst | Amount   | Before   | After    | Δ        | Δ %
Initial        |       |      |          | 1000.00  | 1000.00  | 0.0000   | 0.00%
After Trade 0  | 0     | 2    | +5.0000  | 1000.00  | 1250.00  | +250.00  | +25.00%
After Trade 1  | 1     | 0    | -3.0000  | 1250.00  | 1100.00  | -150.00  | -12.00%
After Trade 2  | 2     | 2    | +2.0000  | 1100.00  | 1300.00  | +200.00  | +18.18%
```

**Additional Feature:** Automatically highlights the top 3 trades with largest margin impact

**Usage:** Identify which trades significantly increased or decreased margin requirements.

---

### 4. 💰 Expected PnL Impact Per Trade

**What it shows:**
- How each trade affects expected PnL given today's realized returns
- Incremental PnL contribution from each specific trade
- Cumulative PnL evolution

**Columns:**
| Column | Description |
|--------|-------------|
| State | Stage description |
| Trade | Trade number |
| Instrument | Instrument being traded |
| Trade Amount | Amount of trade |
| Expected PnL | Total expected PnL at this state |
| PnL Δ from Trade | Incremental PnL from this specific trade |
| Cumulative PnL | Running total PnL |

**Calculation:**
```
PnL Δ from Trade = Trade Amount × Realized Return[Instrument]
```

**Example:**
```
State          | Trade | Inst | Amount   | Expected PnL | PnL Δ Trade | Cumulative
Initial        |       |      |          | 100.00       |             | 100.00
After Trade 0  | 0     | 2    | +5.0000  | 107.50       | +7.50       | 107.50
After Trade 1  | 1     | 0    | -3.0000  | 104.00       | -3.50       | 104.00
After Trade 2  | 2     | 2    | +2.0000  | 107.00       | +3.00       | 107.00
```

**Interpretation:**
- Trade 0: Bought 5 units of instrument 2, which had a return of 1.5%, adding 7.50 to PnL
- Trade 1: Sold 3 units of instrument 0, which had a return of 1.17%, reducing PnL by 3.50
- Trade 2: Bought 2 units of instrument 2, adding another 3.00 to PnL

**Usage:** Understand whether trades increased or decreased exposure to profitable instruments.

---

## How to Access

1. **Navigate to Client Debug Calculator tab**
2. **Select a client** from the dropdown
3. **Scroll to Section 4: Portfolio Evolution & Trades**
4. **Expand the relevant table:**
   - 🔍 View Trade-by-Trade Impact Analysis
   - 📊 View Full Portfolio After Each Trade
   - 📈 View Margin Sensitivity Per Trade
   - 💰 View Expected PnL Impact Per Trade

---

## Common Workflows

### Workflow 1: "Why did this client's margin increase so much?"

**Goal:** Identify which trades caused the margin spike

**Steps:**
1. Go to Section 4 - Portfolio Evolution & Trades
2. Open "📈 View Margin Sensitivity Per Trade"
3. Look at the "Margin Δ %" column
4. Identify trades with large positive % changes
5. Check "Trades with Largest Margin Impact" summary at bottom

**Example Result:**
```
Top 3 Margin Impacts:
1. Trade 5 (Instrument 3): +450.23 (+35.67%)
2. Trade 2 (Instrument 1): +320.15 (+28.42%)
3. Trade 8 (Instrument 3): +180.50 (+12.34%)
```

**Conclusion:** Trades in Instrument 3 are driving margin increases.

---

### Workflow 2: "Did this trade make the client's position riskier?"

**Goal:** See if a specific trade increased margin

**Steps:**
1. Note the trade number (e.g., Trade 3)
2. Open "🔍 View Trade-by-Trade Impact Analysis"
3. Find "After Trade 3" row
4. Compare "Margin" with previous row's margin
5. Check "Margin Change" to see cumulative effect

**Example:**
```
After Trade 2: Margin = 1100.00
After Trade 3: Margin = 1450.00  (+350.00)
```

**Conclusion:** Trade 3 increased margin by 350, making position riskier.

---

### Workflow 3: "What trades contributed positively to PnL?"

**Goal:** Identify profitable trades (in hindsight)

**Steps:**
1. Open "💰 View Expected PnL Impact Per Trade"
2. Sort by "PnL Δ from Trade" column (click header)
3. Trades with positive Δ contributed to profit
4. Trades with negative Δ were detrimental

**Example:**
```
Trade 0 (Inst 2, +5.0000):  PnL Δ = +12.50  ✓ Good trade
Trade 1 (Inst 0, -3.0000):  PnL Δ = -8.20   ✗ Bad trade
Trade 2 (Inst 1, +10.0000): PnL Δ = +25.00  ✓ Good trade
```

**Conclusion:** Trades 0 and 2 were profitable given today's returns; Trade 1 was not.

---

### Workflow 4: "How did the portfolio evolve through trading?"

**Goal:** See complete portfolio transformation

**Steps:**
1. Open "📊 View Full Portfolio After Each Trade"
2. Filter by a specific instrument (optional)
3. Watch position change through stages
4. Verify final state matches expected

**Example (filtering for Instrument 2):**
```
Stage           | Instrument | Position
Initial         | 2          | 10.0000
After Trade 0   | 2          | 15.0000  (+5 from Trade 0)
After Trade 2   | 2          | 17.0000  (+2 from Trade 2)
Final           | 2          | 17.0000
```

**Conclusion:** Instrument 2 position increased from 10 → 17 through two trades.

---

## Advanced Use Cases

### Use Case 1: Margin Hedging Analysis

**Question:** "Did trades hedge the position or increase concentration?"

**Method:**
1. Check margin sensitivity per trade
2. Trades that decrease margin are hedging (reducing risk)
3. Trades that increase margin are concentrating (adding risk)

**Example:**
```
Trade 0 (Buy Inst 2):  Margin Δ = +250  → Adding risk
Trade 1 (Sell Inst 0): Margin Δ = -150  → Hedging
Trade 2 (Buy Inst 2):  Margin Δ = +200  → Adding risk again
```

**Conclusion:** Client doubled down on Instrument 2 (risky), briefly hedged with Trade 1.

---

### Use Case 2: Trade Sequencing Impact

**Question:** "Would margin have been different if trades were executed in different order?"

**Method:**
1. Note the margin changes per trade
2. Consider that margin is non-linear (not simply additive)
3. Sequence matters because each trade changes the base portfolio

**Example:**
```
Actual Sequence:
  Trade A (+5 Inst 2) → Margin: 1000 → 1250 (+250)
  Trade B (-3 Inst 0) → Margin: 1250 → 1100 (-150)
  Final Margin: 1100

Hypothetical Reverse:
  Trade B first might have: 1000 → 980 (-20)
  Trade A after:          980 → 1200 (+220)
  Final Margin: ~1200 (different!)
```

**Note:** This analysis requires re-running calculations with different sequences (not currently automated).

---

### Use Case 3: Correlation Between PnL and Margin

**Question:** "Do trades that increase PnL also increase margin?"

**Method:**
1. Open both margin sensitivity and PnL impact tables
2. Compare side-by-side for each trade
3. Look for correlation

**Example:**
```
Trade | Margin Δ | PnL Δ  | Pattern
0     | +250     | +12.50 | Increased both (risky + profitable)
1     | -150     | -8.20  | Decreased margin but lost PnL (hedge that cost money)
2     | +200     | +25.00 | Increased both (risky + profitable)
```

**Conclusion:** Client is taking profitable but risky positions.

---

## Tips and Tricks

### Tip 1: Use Streamlit's Built-in Sorting

Click any column header to sort the table by that column. Useful for:
- Finding largest margin impacts
- Sorting by instrument
- Ordering by trade number

### Tip 2: Focus on Accepted Trades Only

Tables automatically filter out rejected trades. Only accepted trades are shown because rejected trades don't affect the portfolio.

### Tip 3: Compare Initial vs Final

Every table includes initial and final states, making it easy to verify:
- Initial portfolio + all trades = Final portfolio ✓
- Initial margin + trade impacts = Final margin ✓

### Tip 4: Export to Spreadsheet

Streamlit allows you to:
1. Select table cells
2. Copy (Ctrl+C / Cmd+C)
3. Paste into Excel/Google Sheets for custom analysis

### Tip 5: Cross-Reference with Section 2

The margin values in trade-by-trade analysis use the same alpha (confidence level) as Section 2. Adjust the alpha slider to see how trade impact changes at different confidence levels.

---

## Calculation Details

### Margin Calculation Per Trade

For each trade, the margin is recalculated using Expected Shortfall (ES):

```python
portfolio_after_trade = portfolio_before + trade_amount
margin_after = ES(portfolio_after_trade, scenarios, alpha)
margin_delta = margin_after - margin_before
```

This is computationally expensive for large scenario sets, so analysis is done on-demand when you expand the tables.

### PnL Calculation Per Trade

The incremental PnL from a trade is straightforward:

```python
pnl_delta = trade_amount × realized_return[instrument]
```

This shows what the trade contributed to today's PnL given today's actual returns.

---

## Performance Notes

### Large Number of Trades

If a client has 20+ trades:
- Tables may take a few seconds to calculate
- Streamlit will show a loading spinner
- All trades are shown (no limit)

### Many Scenarios

If you have 1000+ scenarios:
- Margin calculations take longer (ES requires sorting all scenarios)
- Each trade's margin calculation is independent
- Expect ~1-2 seconds per trade for large scenario sets

### Optimization

Tables use list comprehensions and lazy evaluation for efficiency. They only calculate when you expand them, keeping the UI responsive.

---

## Example: Complete Analysis

**Scenario:** Client 1 executed 3 trades today. Let's analyze them.

### Step 1: View Trade Summary

```
Trades Executed This Day:
Trade # | Instrument | Amount    | Accepted
0       | 2          | +5.0000   | ✓ Yes
1       | 0          | -3.0000   | ✓ Yes
2       | 2          | +2.0000   | ✓ Yes
```

### Step 2: Trade Impact Summary

```
State                | Margin   | Margin Change
Initial              | 1000.00  |
After Trade 0        | 1250.00  | +250.00
After Trade 1        | 1100.00  | +100.00
After Trade 2        | 1300.00  | +300.00
```

**Observation:** Net margin increased by 300 (30% increase)

### Step 3: Margin Sensitivity

```
Trade | Inst | Amount   | Margin Δ | Margin Δ %
0     | 2    | +5.0000  | +250.00  | +25.00%
1     | 0    | -3.0000  | -150.00  | -12.00%
2     | 2    | +2.0000  | +200.00  | +18.18%
```

**Top Margin Impact:** Trade 0 (+25%)

**Observation:**
- Trades 0 and 2 increased risk significantly (buying Inst 2)
- Trade 1 partially offset (selling Inst 0)

### Step 4: PnL Impact

```
Trade | Inst | Amount   | PnL Δ   | Cumulative
0     | 2    | +5.0000  | +7.50   | 107.50
1     | 0    | -3.0000  | -4.50   | 103.00
2     | 2    | +2.0000  | +3.00   | 106.00
```

**Observation:**
- Instrument 2 trades added 10.50 to PnL
- Instrument 0 trade reduced PnL by 4.50
- Net PnL impact: +6.00

### Conclusion

Client 1's trading strategy:
- ✓ Increased exposure to Instrument 2 (profitable today: +10.50 PnL)
- ✗ Reduced exposure to Instrument 0 (cost 4.50 PnL)
- ⚠️ Significantly increased margin requirement (+30%)
- 📊 Risk/reward: +6 PnL for +300 margin = 2% return on margin increase

**Assessment:** Trades were profitable but significantly increased risk exposure.

---

## Summary

The Trade-by-Trade Impact Analysis provides:

✅ **Complete transparency** into how each trade affects the portfolio
✅ **Margin sensitivity** showing risk changes per trade
✅ **PnL attribution** identifying profitable vs unprofitable trades
✅ **Full portfolio evolution** tracking all instruments through trading
✅ **Sorting and filtering** for custom analysis
✅ **Export capability** for external analysis

Use this tool to debug trading activity, understand risk accumulation, and verify that trades had their intended effect on the portfolio.

---

**Happy Trading Analysis! 📊💹**
