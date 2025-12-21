"""
Generate sample simulation data for testing the visualizer.
This creates a mock simulation output without running the full simulation.
"""
import json
import random


def generate_sample_metrics(n_days=10, n_clients_per_cm=5, n_cms=2):
    """Generate sample clearing simulation metrics."""
    metrics = []

    for day in range(n_days):
        # System-level metrics
        total_collateral = random.uniform(800000, 1200000)
        avg_collateral = total_collateral / (n_clients_per_cm * n_cms)
        total_cm_funds = random.uniform(400000, 600000)
        num_active = random.randint(50, 150)
        num_accepted = int(num_active * random.uniform(0.7, 0.95))

        system = {
            "total_client_collateral": total_collateral,
            "avg_client_collateral": avg_collateral,
            "min_client_collateral": random.uniform(10000, 30000),
            "total_cm_funds": total_cm_funds,
            "avg_client_margin": random.uniform(15000, 25000),
            "total_client_margin": random.uniform(150000, 250000),
            "num_active_trades": num_active,
            "num_accepted_trades": num_accepted,
            "num_zero_collateral_clients": random.randint(0, 2),
        }

        # Clearing members
        cms = {}
        for cm_idx in range(n_cms):
            cm_name = f"CM_{cm_idx + 1}"
            cm_funds = random.uniform(200000, 300000)

            clients = []
            for client_idx in range(n_clients_per_cm):
                client_id = cm_idx * n_clients_per_cm + client_idx
                wealth = random.uniform(40000, 100000)
                collateral = random.uniform(20000, 60000)
                margin = random.uniform(15000, 30000)
                shortfall = max(0, margin - collateral)
                margin_called = shortfall > 0

                # Generate some trades
                trades = []
                n_trades = random.randint(5, 15)
                for _ in range(n_trades):
                    trades.append({
                        "instrument": random.randint(0, 9),
                        "amount": random.uniform(-500, 500),
                        "accepted": random.random() > 0.2
                    })

                client = {
                    "client_id": client_id,
                    "vip_status": random.choice(["REGULAR", "VIP"]),
                    "liquidity_status_end": random.choice(["LIQUID", "ILLIQUID"]),
                    "wealth_end": wealth,
                    "collateral_end": collateral,
                    "margin": margin,
                    "shortfall": shortfall,
                    "pnl": random.uniform(-5000, 5000),
                    "income_applied": random.choice([True, False]),
                    "margin_call": {
                        "called": margin_called,
                        "amount": shortfall if margin_called else 0,
                        "accepted": random.choice([True, False]) if margin_called else None,
                        "liquidated": False
                    },
                    "trades": trades,
                    "portfolio_start": [random.uniform(-100, 100) for _ in range(10)],
                    "portfolio_end": [random.uniform(-100, 100) for _ in range(10)],
                }
                clients.append(client)

            cms[cm_name] = {
                "cm_funds": cm_funds,
                "cm_pnl": random.uniform(-10000, 10000),
                "default_shortfall": random.uniform(0, 5000),
                "total_client_collateral": sum(c["collateral_end"] for c in clients),
                "avg_client_collateral": sum(c["collateral_end"] for c in clients) / len(clients),
                "min_client_collateral": min(c["collateral_end"] for c in clients),
                "avg_client_margin": sum(c["margin"] for c in clients) / len(clients),
                "total_client_margin": sum(c["margin"] for c in clients),
                "num_active_trades": random.randint(20, 80),
                "num_accepted_trades": random.randint(15, 70),
                "num_zero_collateral_clients": 0,
                "clients": clients,
            }

        # CCPs
        ccps = {
            "CCP_1": {
                "ccp_margin": random.uniform(300000, 500000),
                "cm_margins": {f"CM_{i+1}": random.uniform(100000, 200000) for i in range(n_cms)},
                "cm_funds": {f"CM_{i+1}": random.uniform(200000, 300000) for i in range(n_cms)},
                "cm_shortfalls": {f"CM_{i+1}": random.uniform(0, 5000) for i in range(n_cms)},
            }
        }

        # Details
        details = {
            "market_state": [random.uniform(-1, 1) for _ in range(10)],
            "real_returns": [random.uniform(-0.05, 0.05) for _ in range(10)],
        }

        day_metrics = {
            "day": day,
            "market_index": random.randint(0, 100),
            "system": system,
            "cms": cms,
            "ccps": ccps,
            "details": details,
        }

        metrics.append(day_metrics)

    return {"metrics": metrics}


if __name__ == "__main__":
    print("Generating sample simulation data...")
    data = generate_sample_metrics(n_days=30, n_clients_per_cm=10, n_cms=3)

    output_file = "sample_simulation_output.json"
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Sample data saved to: {output_file}")
    print(f"Generated {len(data['metrics'])} days of simulation data")
    print(f"Total clients: {sum(len(cm['clients']) for cm in data['metrics'][0]['cms'].values())}")
    print("\nYou can now upload this file to the visualizer!")
