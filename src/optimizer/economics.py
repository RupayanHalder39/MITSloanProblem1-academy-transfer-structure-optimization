from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


RETENTION_GRID = list(range(0, 81, 5))
VALIDITY_GRID = [1, 2, 3, 4, 5]
DEFAULT_3Y_TRANSFER_CDF = 0.50
LOW_3Y_TRANSFER_CDF = 0.30
HIGH_3Y_TRANSFER_CDF = 0.70
DEFAULT_DISCOUNT_RATE = 0.10
DEFAULT_RISK_LAMBDA = 0.35
BUYER_BURDEN_MULTIPLIER = 0.25


def calibrate_fee_anchor_multiplier(panel: pd.DataFrame) -> float:
    usable = panel[(panel["initial_fee_eur"] > 0) & (panel["value_at_exit"] > 0)].copy()
    if usable.empty:
        return 0.90
    ratios = usable["initial_fee_eur"] / usable["value_at_exit"]
    ratios = ratios.replace([np.inf, -np.inf], np.nan).dropna()
    ratios = ratios[(ratios > 0.05) & (ratios < 3.0)]
    if ratios.empty:
        return 0.90
    return float(ratios.median())


def calibrate_fee_to_value_multiple(club_transfers: pd.DataFrame) -> float:
    usable = club_transfers[(club_transfers["is_loan"] == False) & club_transfers["price"].notna() & club_transfers["market_value_at_transfer"].notna()].copy()
    usable = usable[(usable["price"] > 0) & (usable["market_value_at_transfer"] > 0)]
    if usable.empty:
        return 1.0
    ratios = usable["price"] / usable["market_value_at_transfer"]
    ratios = ratios[(ratios > 0.05) & (ratios < 3.0)]
    return float(ratios.median()) if not ratios.empty else 1.0


def annual_hazard_from_cdf(total_cdf_3y: float) -> float:
    total_cdf_3y = min(max(total_cdf_3y, 0.01), 0.99)
    return 1.0 - (1.0 - total_cdf_3y) ** (1.0 / 3.0)


def yearly_transfer_masses(total_cdf_3y: float) -> dict[int, float]:
    h = annual_hazard_from_cdf(total_cdf_3y)
    masses = {}
    survival = 1.0
    for year in range(1, 6):
        masses[year] = survival * h
        survival *= 1.0 - h
    return masses


def projected_fee_by_year(scenario_values: dict[int, float], fee_to_value_multiple: float, discount_tail: float = 0.95) -> dict[int, float]:
    fees = {}
    for year in range(1, 6):
        if year <= 3 and scenario_values.get(year) is not None:
            fees[year] = max(0.0, fee_to_value_multiple * scenario_values[year])
        else:
            tail_base = fees.get(3, fee_to_value_multiple * scenario_values.get(3, 0.0))
            fees[year] = max(0.0, tail_base * (discount_tail ** max(year - 3, 0)))
    return fees


def retained_value_component(
    retention_pct: float,
    validity_years: int,
    scenario_values: dict[int, float],
    transfer_cdf_3y: float,
    fee_to_value_multiple: float,
    discount_rate: float,
    base_fee_reference: float,
) -> float:
    retain_share = retention_pct / 100.0
    masses = yearly_transfer_masses(transfer_cdf_3y)
    projected_fees = projected_fee_by_year(scenario_values, fee_to_value_multiple)
    total = 0.0
    for year in range(1, validity_years + 1):
        upside_only_fee = max(0.0, projected_fees[year] - base_fee_reference)
        payout = retain_share * upside_only_fee
        total += masses[year] * payout / ((1.0 + discount_rate) ** year)
    return float(total)


def full_sale_upfront(value_at_exit: float, fee_anchor_multiplier: float) -> float:
    return max(0.0, value_at_exit * fee_anchor_multiplier)


def buyer_feasible_upfront(
    value_at_exit: float,
    fee_anchor_multiplier: float,
    retention_pct: float,
    validity_years: int,
    scenario_values_expected: dict[int, float],
    transfer_cdf_3y: float,
    fee_to_value_multiple: float,
    discount_rate: float,
) -> float:
    anchor = full_sale_upfront(value_at_exit, fee_anchor_multiplier)
    sold_share = max(0.0, 1.0 - retention_pct / 100.0)
    base_partial_upfront = anchor * sold_share
    upfront_floor = 0.25 * base_partial_upfront
    burden = BUYER_BURDEN_MULTIPLIER * retained_value_component(
        retention_pct,
        validity_years,
        scenario_values_expected,
        transfer_cdf_3y,
        fee_to_value_multiple,
        discount_rate,
        anchor,
    )
    return max(upfront_floor, base_partial_upfront - burden)


def downside_semideviation(expected_value: float, scenario_outcomes: list[tuple[float, float]]) -> float:
    penalty = 0.0
    for outcome, prob in scenario_outcomes:
        penalty += prob * max(0.0, expected_value - outcome) ** 2
    return float(np.sqrt(penalty))


def risk_adjusted_value(expected_value: float, scenario_outcomes: list[tuple[float, float]], risk_lambda: float) -> float:
    return float(expected_value - risk_lambda * downside_semideviation(expected_value, scenario_outcomes))


def minimum_acceptable_upfront(target_risk_adjusted_value: float, retained_component_risk_adjusted: float) -> float:
    return max(0.0, target_risk_adjusted_value - retained_component_risk_adjusted)
