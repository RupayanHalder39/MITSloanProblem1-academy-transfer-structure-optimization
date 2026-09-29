from __future__ import annotations

import pandas as pd


SCENARIO_WEIGHTS = {
    "UNDERGROWS": 0.25,
    "EXPECTED": 0.50,
    "OUTGROWS": 0.25,
}


def build_growth_scenarios(forecast_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rec in forecast_df.to_dict("records"):
        for scenario, field in [
            ("UNDERGROWS", "forecast_p25"),
            ("EXPECTED", "forecast_p50"),
            ("OUTGROWS", "forecast_p75"),
        ]:
            rows.append(
                {
                    "case_id": rec["case_id"],
                    "player": rec["player"],
                    "horizon_years": rec["horizon_years"],
                    "scenario": scenario,
                    "scenario_probability": SCENARIO_WEIGHTS[scenario],
                    "projected_value": rec[field],
                }
            )
    return pd.DataFrame(rows)
