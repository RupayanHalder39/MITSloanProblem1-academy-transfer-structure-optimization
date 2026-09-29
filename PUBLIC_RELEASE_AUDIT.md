# Public Release Audit

## Release identity

- Project: *Sell Now or Keep a Share? Risk-Adjusted Optimization of Academy
  Transfer Structures in Football*
- MIT Sloan problem: 1
- Public author and repository maintainer: Rupayan Halder
- Repository target:
  `https://github.com/RupayanHalder39/MITSloanProblem1-academy-transfer-structure-optimization`
- Audit status: **PASS — approved for publication after final Git checks**

## Authoritative source and public paper

The authoritative four-page source PDF in the completed research project was
inspected page by page. Pages 1–2 contain the final submission. Pages 3–4
contain internal commentary and reference material and were intentionally
excluded.

The public paper was created by copying the first two PDF page objects with
`pypdf`; the source was not overwritten. No page was rasterized, cropped,
reconstructed, or reflowed.

Verification of the public copy:

- exactly two pages;
- A4 dimensions retained: 596 × 842 points on both pages;
- render comparison at 150 dpi found zero pixel differences between each
  public page and the corresponding source page;
- no clipping, reflow, or figure change was observed;
- extracted text contains none of the internal-comment phrases or names used
  in the release scan;
- no JavaScript, forms, encryption, custom metadata, or metadata stream is
  present.

## Included artifacts

- sanitized two-page final paper;
- final offer × share-sold decision-surface figure in PNG and PDF;
- final 36-exit cohort decision map in PNG and PDF;
- aggregate headline results and portfolio/sensitivity summaries;
- public-safe economic primitives and scenario engine;
- aggregate reproduction and public-release validation scripts;
- methodology, limitations, provenance, and reproduction documentation;
- citation metadata, scoped code license, dependency list, and ignore rules.

The staged PNG figures have the same SHA-256 hashes as their approved source
images.

## Intentionally excluded artifacts

- internal commentary and reference pages from the source PDF;
- working drafts, prior abstract versions, correspondence, screenshots,
  prompts, logs, and internal handoff material;
- source-data directories, caches, fitted artifacts, exploratory notebooks,
  and superseded figures;
- player-level analytical tables and recommendations;
- any file with unresolved redistribution rights.

## Data redistribution decision

Only original release materials and compact aggregate results are included.
The data audit classified published valuation and transaction data as public
source material with uncertain bulk-redistribution rights; organizational
exports and the academy workbook as restricted; and derived row-level panels,
identity maps, fitted artifacts, and player-level recommendation tables as
rights-unresolved. All were excluded.

`docs/DATA_PROVENANCE.md` records each category, its research purpose, the
reason for exclusion, and a lawful reconstruction route where one can be
described. The repository contains no raw or row-level research dataset.

## Code cleanup and reproducibility

The included economic modules preserve the completed project's calculation
logic. Public package initializers were added, and only modules that do not
depend on private loaders were retained. No algorithm or frozen parameter was
changed. Public instructions and code use repository-relative inputs and do
not read from a private or machine-specific location.

Reproducibility is **partial**:

- aggregate findings can be recomputed from the included summaries;
- economic primitives can be inspected and imported;
- end-to-end forecast fitting and player-level optimization require separately
  authorized source data and are therefore not represented as fully
  reproducible by this package.

Executed checks:

```text
python scripts/reproduce_headlines.py     PASS
python scripts/validate_public_release.py PASS
public Python-module import check         PASS
```

## Numerical verification

The public aggregate files and reproduction script verify:

- 36 modellable exits;
- 29 full-sale selections;
- seven nominal retention selections, all value-neutral ties;
- €0 additional modelled value from those ties and no workable overlap;
- player-specific portfolio: €172.37M;
- full-sale portfolio: €172.37M;
- hypothetical fixed 50/50 portfolio: €161.65M;
- difference versus fixed 50/50: €10.72M;
- relative difference: 6.63%;
- approximately €297,860 per modelled exit;
- 1,500 sensitivity configurations;
- P10 €5.5M, median €15.7M, and P90 €33.6M.

The README correctly describes the result as avoiding the modelled loss from
mechanically imposing a fixed 50/50 structure. It does not claim that retained
shares created the difference or that player-specific selection beat full
sale.

## Security, privacy, and portability scan

The complete staging tree was checked for credentials, secret-like values,
private keys, environment files, private links, unnecessary email addresses,
local absolute paths, internal names and discussion, hidden OS files, caches,
symlinks, database or model-artifact formats, restricted datasets, and files
larger than 10 MB.

Result: **PASS**. The only secret-related words found are the defensive pattern
names inside the validator itself; they are not credentials. No symlinks,
unexpected large files, raw datasets, or machine-specific paths are present.

## License scope

The MIT license applies only to original source-code files in this public
repository. It does not relicense excluded third-party data, external content,
trademarks, or materials for which the repository author does not hold rights.
The data-provenance document states this distinction explicitly.

## Repository size and publication scope

- Audited package size before Git metadata: approximately 2.9 MB.
- This file records the content, scientific, privacy, and reproducibility audit
  completed immediately before publication. Git history and the live remote
  state are verified separately as part of the publication procedure.

## Final verdict

**READY TO PUSH** following final staged-content and remote-target checks.
