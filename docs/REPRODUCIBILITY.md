# Reproducibility

## Scope

This release supports complete verification of the published aggregate claims
and inspection of the frozen economic primitives. It does not redistribute the
row-level inputs required to refit the forecast or rerun all player decisions.
Reproducibility is therefore **partial**.

## Environment

Python 3.12 or newer is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Public verification

From the repository root:

```bash
python scripts/reproduce_headlines.py
python scripts/validate_public_release.py
```

The first command recomputes the portfolio difference, relative difference,
and per-exit value from the included aggregate totals. The validator checks the
paper, figures, metadata, result constants, links, file types, portability, and
common security/privacy hazards.

## Full analytical reconstruction

Authorized researchers must supply equivalent dated valuation histories,
academy-exit records, transfer transactions, and cohort identity information.
The required conceptual schema and transformations are described in
`DATA_PROVENANCE.md` and `METHODOLOGY.md`.

The public repository does not provide source-specific download automation.
Acquisition must comply with the originating providers' terms. No public
command silently reads from a private or machine-specific location.

## Expected aggregate output

- 36 modellable exits
- 29 full-sale selections and seven nominal retention ties
- €172.37M player-specific and €172.37M full sale
- €161.65M hypothetical fixed 50/50
- €10.72M difference, 6.63%, approximately €297,860 per exit
- 1,500 sensitivity configurations; P10 €5.5M, median €15.7M, P90 €33.6M
