# Methodology

## Study cohort

The final cohort contains 36 modellable academy-player exits with sufficiently
resolved identity information and a pre-exit market-value observation.

## Forecasting layer

Approximately 9,000 historical valuation trajectories provide decision-date-
safe training anchors. One- and two-year forecasts use value persistence. The
three-year forecast uses a deterministic 400-tree Extra Trees regressor with a
log-ratio target, maximum depth 8, minimum leaf size 20, and seed `20240301`.
Chronological out-of-sample three-year MAE is €13.54M, compared with €21.91M
for the preceding ridge specification.

## Offer-by-share decision

For each player, the decision grid evaluates retained economic shares from 0%
to 80% in five-percentage-point increments and validity windows from one to
five years.

- **Full-sale anchor:** decision-date value multiplied by the calibrated fee
  anchor.
- **Risk-adjusted retained component:** discounted expected retained-right
  value across undergrowth, expected, and outgrowth scenarios, penalized for
  downside variation.
- **Seller break-even upfront amount:** full-sale anchor minus the risk-adjusted
  retained component.
- **Modelled buyer ceiling:** sold-share anchor plus sold-share forecast upside,
  less duration burden, buyer cost, and target-margin buffer.
- **Feasible negotiation zone:** buyer ceiling minus seller break-even is
  non-negative.
- **Opening ask:** seller break-even plus 60% of a positive negotiation margin.

The frozen default calibration uses a convex duration cost, risk penalty 0.20,
three-year transfer CDF 0.70, discount rate 0.15, buyer target margin 0.10,
base buyer cost, and bargaining share 0.60.

The model selects the feasible structure with the highest risk-adjusted
modelled club value. Full sale and fixed retained-share rules are evaluated
on the same 36 exits.

## Sensitivity analysis

A deterministic Latin-hypercube design evaluates 1,500 configurations across
discount rate, transfer probability, buyer target margin, risk penalty,
bargaining share, buyer-cost scenario, and duration-cost form. These are
scenario checks under the model assumptions, not evidence of realised buyer
behaviour or causal effects.
