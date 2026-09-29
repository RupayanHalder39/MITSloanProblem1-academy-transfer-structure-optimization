# Data provenance and redistribution decision

## Classification rule

Candidate files were classified as follows:

- **A — Safe to redistribute:** original documentation and release code.
- **B — Derived or aggregated and safe:** compact publication-level summaries
  that do not expose underlying rows.
- **C — Public source, redistribution uncertain:** externally published data
  for which bulk republication permission was not established.
- **D — Restricted or proprietary:** private exports or organizational data.
- **E — Unknown:** files without enough rights information to support release.

Only categories A and B are included.

## Source inventory

| Input | Research role | Classification | Public-release decision |
|---|---|---:|---|
| Published player valuation histories | Forecast trajectories and decision-date values | C | Excluded; obtain lawfully from the originating publisher or an appropriately licensed equivalent source. |
| Published transfer transaction records | Transfer timing and fee calibration | C | Excluded; reconstruct from a licensed transaction source. |
| Academy-player workbook | Cohort definition and identity reconciliation | D | Excluded; no public redistribution permission was established. |
| Club transfer export | Fee-to-value calibration and transfer context | D | Excluded; organizational export is not public release material. |
| Derived 36-exit player panel and identity map | Joined analytical cohort | E | Excluded because it preserves row-level information derived from sources with unresolved rights. |
| Forecast prediction files and model artifacts | Player-level predictions and fitted model state | E | Excluded because they derive from non-redistributed rows and are not necessary for aggregate verification. |
| Player-level recommendation and negotiation tables | Decision surfaces and recommendations | E | Excluded because player-level redistribution rights were not established. |
| Aggregate portfolio and sensitivity summaries | Verification of published findings | B | Included under `results/`. |
| Paper and final figures | Publication record | A | Included as the approved public artifacts. |

## Reconstruction outline

An authorized researcher needs dated player valuations, academy-exit records,
transaction information, and the variables defined in `METHODOLOGY.md`.
Identity resolution produces one record per academy exit with a pre-exit value.
Decision-date-safe valuation histories then produce forecast anchors and
one-, two-, and three-year targets. The forecast scenarios enter the retained-
share and validity-window grid described in the methodology.

Because the underlying inputs are absent, this repository provides **partial
reproducibility**: headline results and the economic primitives are verifiable,
while end-to-end model fitting requires separately authorized data.
