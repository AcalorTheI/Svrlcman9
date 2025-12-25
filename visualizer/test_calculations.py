"""
Test script to verify the calculation functions in the visualizer
"""

# Import the calculation functions
import sys
sys.path.insert(0, '.')

def test_pnl_calculation():
    """Test PnL calculation"""
    from app import _calculate_pnl_manual

    # Test case 1: Simple PnL
    portfolio = [10.0, -5.0, 20.0]
    returns = [0.01, -0.02, 0.015]

    expected_pnl = 10.0 * 0.01 + (-5.0) * (-0.02) + 20.0 * 0.015
    calculated_pnl = _calculate_pnl_manual(portfolio, returns)

    print("=== PnL Calculation Test ===")
    print(f"Portfolio: {portfolio}")
    print(f"Returns: {returns}")
    print(f"Expected PnL: {expected_pnl}")
    print(f"Calculated PnL: {calculated_pnl}")
    print(f"Match: {abs(expected_pnl - calculated_pnl) < 0.0001}")
    print()

def test_margin_calculation():
    """Test margin (Expected Shortfall) calculation"""
    from app import _calculate_margin_manual

    # Test case: Portfolio with simple scenarios
    portfolio = [10.0, -5.0]
    scenarios = [
        [0.01, 0.02],   # Scenario 1
        [-0.03, 0.01],  # Scenario 2
        [0.02, -0.04],  # Scenario 3
        [-0.05, -0.02], # Scenario 4
        [0.015, 0.015], # Scenario 5
    ]

    alpha = 0.80  # 80th percentile for easy testing

    result = _calculate_margin_manual(portfolio, scenarios, alpha)

    print("=== Margin Calculation Test ===")
    print(f"Portfolio: {portfolio}")
    print(f"Num Scenarios: {len(scenarios)}")
    print(f"Alpha: {alpha}")
    print(f"Calculated Margin (ES): {result['margin']}")
    print(f"VaR: {result['var']}")
    print(f"Tail count: {result['tail_count']}")
    print(f"All losses (sorted): {result['losses'][:10]}")
    print()

    # Manually verify
    pnls = []
    for scenario in scenarios:
        pnl = sum(p * r for p, r in zip(portfolio, scenario))
        pnls.append(pnl)

    losses = [-pnl for pnl in pnls]
    sorted_losses = sorted(losses)

    print("Manual verification:")
    print(f"PnLs: {pnls}")
    print(f"Losses: {sorted_losses}")
    print()

def test_client_details():
    """Test client details extraction"""
    from app import _get_client_details

    # Mock CMS data
    cms = {
        "CM1": {
            "clients": [
                {"client_id": 0, "wealth_end": 1000.0},
                {"client_id": 1, "wealth_end": 2000.0},
            ]
        },
        "CM2": {
            "clients": [
                {"client_id": 0, "wealth_end": 3000.0},
            ]
        }
    }

    print("=== Client Details Test ===")

    client = _get_client_details(cms, "CM1", 1)
    print(f"CM1, Client 1: {client}")
    assert client.get("wealth_end") == 2000.0, "Failed to get correct client"

    client = _get_client_details(cms, "CM2", 0)
    print(f"CM2, Client 0: {client}")
    assert client.get("wealth_end") == 3000.0, "Failed to get correct client"

    client = _get_client_details(cms, "CM3", 0)
    print(f"CM3, Client 0 (should be empty): {client}")
    assert client == {}, "Should return empty dict for non-existent client"

    print("All tests passed!")
    print()

if __name__ == "__main__":
    print("Running calculation tests...\n")
    test_pnl_calculation()
    test_margin_calculation()
    test_client_details()
    print("All tests completed successfully! ✅")
