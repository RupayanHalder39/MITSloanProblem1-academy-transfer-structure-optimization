from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd

from src.optimizer.economics import (
    DEFAULT_3Y_TRANSFER_CDF,
    DEFAULT_DISCOUNT_RATE,
    DEFAULT_RISK_LAMBDA,
    calibrate_fee_anchor_multiplier,
    calibrate_fee_to_value_multiple,
    full_sale_upfront,
    projected_fee_by_year,
    yearly_transfer_masses,
)


RETENTION_GRID_OPERATIONAL = list(range(0, 81, 5))
RETENTION_GRID_EXTENDED = list(range(0, 101, 5))
VALIDITY_GRID_OPERATIONAL = [1, 2, 3, 4, 5]
VALIDITY_GRID_EXTENDED = [1, 2, 3, 4, 5, 6, 7, 8]

GAMMA_GRID = [0.50, 0.75, 1.00, 1.25, 1.50, 1.75]
BUYER_THRESHOLD_GRID = [0.00, 0.05, 0.10, 0.15, 0.20]
TRANSFER_PROB_GRID = [0.30, 0.50, 0.70]
DISCOUNT_RATE_GRID = [0.05, 0.10, 0.15]
RISK_LAMBDA_GRID = [0.20, 0.35, 0.50, 0.75]
UPFRONT_FLOOR_GRID: list[float | None] = [None, 0.20, 0.30, 0.40, 0.50, 0.60]

DURATION_EXPONENTS = {
    "LINEAR": 1.00,
    "MILD_CONVEX": 1.25,
    "CONVEX": 1.50,
    "STRONG_CONVEX": 2.00,
}


@dataclass(frozen=True)
class CalibrationConfig:
    gamma: float = 1.0
    duration_cost_form: str = "MILD_CONVEX"
    buyer_threshold: float = 0.10
    risk_lambda: float = DEFAULT_RISK_LAMBDA
    transfer_cdf_3y: float = DEFAULT_3Y_TRANSFER_CDF
    discount_rate: float = DEFAULT_DISCOUNT_RATE
    upfront_floor_alpha: float | None = None
    buyer_cost_burden_ratio: float = 0.0


@dataclass(frozen=True)
class CalibrationContext:
    fee_anchor_multiplier: float
    fee_to_value_multiple: float
    horizon_confidence_weights: dict[int, float]


def build_calibration_context(panel: pd.DataFrame, transfers: pd.DataFrame, forecast_metrics: pd.DataFrame) -> CalibrationContext:
    median_v0 = float(panel.loc[panel["main_modeled_cohort_flag"], "value_at_exit"].dropna().median())
    if not np.isfinite(median_v0) or median_v0 <= 0:
        median_v0 = float(panel["value_at_exit"].dropna().median())
    weights = horizon_confidence_weights(forecast_metrics, median_v0)
    return CalibrationContext(
        fee_anchor_multiplier=calibrate_fee_anchor_multiplier(panel),
        fee_to_value_multiple=calibrate_fee_to_value_multiple(transfers),
        horizon_confidence_weights=weights,
    )


def horizon_confidence_weights(forecast_metrics: pd.DataFrame, reference_value: float) -> dict[int, float]:
    reference_value = max(float(reference_value), 1.0)
    weights: dict[int, float] = {}
    for _, row in forecast_metrics.iterrows():
        horizon = int(row["horizon_years"])
        mae = float(row["mae"])
        weight = 1.0 / (1.0 + mae / reference_value)
        weights[horizon] = float(np.clip(weight, 0.15, 1.0))
    last_weight = weights.get(3, 0.25)
    weights[4] = last_weight * 0.90
    weights[5] = last_weight * 0.80
    return weights


def duration_multiplier(validity_years: int, form: str) -> float:
    exponent = DURATION_EXPONENTS[form]
    return float((max(validity_years, 1) / 3.0) ** exponent)


def retained_value_component_weighted(
    retention_pct: float,
    validity_years: int,
    scenario_values: dict[int, float],
    transfer_cdf_3y: float,
    fee_to_value_multiple: float,
    discount_rate: float,
    base_fee_reference: float,
    confidence_weights: dict[int, float],
) -> float:
    retain_share = retention_pct / 100.0
    masses = yearly_transfer_masses(transfer_cdf_3y)
    projected_fees = projected_fee_by_year(scenario_values, fee_to_value_multiple)
    total = 0.0
    h = 1.0 - (1.0 - min(max(transfer_cdf_3y, 0.01), 0.99)) ** (1.0 / 3.0)
    last_mass_year = max(masses)
    survival_after_last = 1.0 - sum(masses.values())
    for year in range(1, validity_years + 1):
        projected_fee = projected_fees.get(year)
        if projected_fee is None:
            tail_base = projected_fees[max(projected_fees)]
            projected_fee = max(0.0, tail_base * (0.95 ** (year - max(projected_fees))))
        mass = masses.get(year)
        if mass is None:
            extra_years = year - last_mass_year - 1
            mass = survival_after_last * ((1.0 - h) ** max(extra_years, 0)) * h
        upside_only_fee = max(0.0, projected_fee - base_fee_reference)
        payout = retain_share * upside_only_fee
        total += mass * payout * confidence_weights.get(year, confidence_weights.get(3, 0.25)) / (
            (1.0 + discount_rate) ** year
        )
    return float(total)


def buyer_cost_burden(anchor: float, retention_pct: float, validity_years: int, burden_ratio: float) -> float:
    if burden_ratio <= 0:
        return 0.0
    return float(anchor * burden_ratio * (retention_pct / 100.0) * (validity_years / 5.0))


def upfront_floor(anchor: float, alpha: float | None) -> float:
    if alpha is None:
        return 0.0
    return max(0.0, float(alpha) * anchor)


def seller_upfront_from_burden(
    anchor: float,
    retention_pct: float,
    validity_years: int,
    expected_retained_value: float,
    config: CalibrationConfig,
) -> float:
    sold_share = max(0.0, 1.0 - retention_pct / 100.0)
    base_partial_upfront = anchor * sold_share
    burden = config.gamma * duration_multiplier(validity_years, config.duration_cost_form) * expected_retained_value
    return max(upfront_floor(anchor, config.upfront_floor_alpha), base_partial_upfront - burden)


def buyer_max_upfront(
    anchor: float,
    retention_pct: float,
    validity_years: int,
    expected_retained_value: float,
    config: CalibrationConfig,
) -> float:
    sold_share = max(0.0, 1.0 - retention_pct / 100.0)
    base_partial_upfront = anchor * sold_share
    duration_burden = duration_multiplier(validity_years, config.duration_cost_form) * expected_retained_value
    cost_burden = buyer_cost_burden(anchor, retention_pct, validity_years, config.buyer_cost_burden_ratio)
    return max(0.0, base_partial_upfront - duration_burden - cost_burden)


def downside_semideviation(expected_value: float, scenario_outcomes: Iterable[tuple[float, float]]) -> float:
    penalty = 0.0
    for outcome, prob in scenario_outcomes:
        penalty += prob * max(0.0, expected_value - outcome) ** 2
    return float(np.sqrt(penalty))


def risk_adjusted_value(expected_value: float, scenario_outcomes: Iterable[tuple[float, float]], risk_lambda: float) -> float:
    return float(expected_value - risk_lambda * downside_semideviation(expected_value, scenario_outcomes))


def scenario_probability(scenario_name: str) -> float:
    return {"UNDERGROWS": 0.25, "EXPECTED": 0.50, "OUTGROWS": 0.25}[scenario_name]


def bucket_from_retention(retention_pct: float) -> str:
    if retention_pct == 0:
        return "SELL ALL"
    if retention_pct <= 25:
        return "LOW RETENTION"
    if retention_pct <= 50:
        return "MEDIUM RETENTION"
    return "HIGH RETENTION"


def stability_bucket(change_rate: float) -> str:
    if change_rate <= 0.10:
        return "VERY STABLE"
    if change_rate <= 0.25:
        return "STABLE"
    if change_rate <= 0.50:
        return "SENSITIVE"
    return "HIGHLY SENSITIVE"


def default_calibration() -> CalibrationConfig:
    return CalibrationConfig()
