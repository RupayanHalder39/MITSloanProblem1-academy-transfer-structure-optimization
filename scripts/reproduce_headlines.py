#!/usr/bin/env python3
"""Recompute the published headline comparisons from safe aggregate totals."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "headline_results.json"


def main() -> None:
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    study = data["study"]
    portfolio = data["portfolio"]

    difference = portfolio["player_specific_eur"] - portfolio["fixed_50_50_eur"]
    relative = 100.0 * difference / portfolio["fixed_50_50_eur"]
    per_exit = difference / study["modellable_exits"]

    assert abs(difference - portfolio["difference_vs_fixed_50_50_eur"]) < 0.01
    assert abs(relative - portfolio["relative_difference_pct"]) < 0.001
    assert abs(per_exit - portfolio["difference_per_exit_eur"]) < 0.01
    assert portfolio["player_specific_eur"] == portfolio["full_sale_eur"]
    assert study["full_sale_selections"] + study["nominal_retention_selections"] == study["modellable_exits"]

    print(f"Modelled exits: {study['modellable_exits']}")
    print(f"Player-specific portfolio: €{portfolio['player_specific_eur'] / 1e6:.2f}M")
    print(f"Full-sale portfolio: €{portfolio['full_sale_eur'] / 1e6:.2f}M")
    print(f"Fixed 50/50 portfolio: €{portfolio['fixed_50_50_eur'] / 1e6:.2f}M")
    print(f"Difference: €{difference / 1e6:.2f}M ({relative:.2f}%)")
    print(f"Difference per exit: €{per_exit:,.0f}")
    print("Headline aggregate verification: PASS")


if __name__ == "__main__":
    main()
