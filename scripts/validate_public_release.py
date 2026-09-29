#!/usr/bin/env python3
"""Validate the publication package without accessing private project files."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "Problem1_Sell_Now_or_Keep_a_Share_Risk_Adjusted_Optimization_of_Academy_Transfer_Structures_in_Football.pdf"

REQUIRED = [
    "README.md", "PUBLIC_RELEASE_AUDIT.md", "LICENSE", "CITATION.cff", "requirements.txt",
    "paper/Problem1_Sell_Now_or_Keep_a_Share_Risk_Adjusted_Optimization_of_Academy_Transfer_Structures_in_Football.pdf",
    "figures/figure_1_offer_share_decision_surface.png",
    "figures/figure_2_cohort_decision_map.png",
    "results/headline_results.json", "results/portfolio_benchmarks.csv",
    "results/sensitivity_summary.csv", "data/README.md",
    "docs/DATA_PROVENANCE.md", "docs/METHODOLOGY.md",
    "docs/REPRODUCIBILITY.md", "docs/LIMITATIONS.md",
    "scripts/reproduce_headlines.py", "scripts/validate_public_release.py",
]

TEXT_SUFFIXES = {".md", ".py", ".json", ".csv", ".cff", ".txt"}
DISALLOWED_DATA_SUFFIXES = {".parquet", ".joblib", ".pkl", ".pickle", ".sqlite", ".sqlite3", ".db"}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def local_markdown_links(text: str) -> list[str]:
    links = re.findall(r"!?(?:\[[^\]]*\])\(([^)]+)\)", text)
    return [link.split("#", 1)[0] for link in links if link and not re.match(r"(?:https?|mailto):", link)]


def main() -> int:
    errors: list[str] = []

    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            fail(errors, f"Missing required file: {relative}")

    if PAPER.exists():
        reader = PdfReader(str(PAPER))
        if len(reader.pages) != 2:
            fail(errors, f"Public paper has {len(reader.pages)} pages; expected 2")
        paper_text = "\n".join((page.extract_text() or "") for page in reader.pages)
        forbidden_pdf = [
            "I like this " + "graph",
            "I dont " + "understand",
            "I will drop some " + "screenshots",
            "Ale" + "jandro",
            "Ru" + "ben",
        ]
        for phrase in forbidden_pdf:
            if phrase.lower() in paper_text.lower():
                fail(errors, f"Forbidden internal phrase found in public PDF: {phrase}")

    result_path = ROOT / "results" / "headline_results.json"
    if result_path.exists():
        d = json.loads(result_path.read_text(encoding="utf-8"))
        s, p, r = d["study"], d["portfolio"], d["sensitivity"]
        checks = {
            "modellable exits": s["modellable_exits"] == 36,
            "full sales": s["full_sale_selections"] == 29,
            "retention ties": s["nominal_retention_ties"] == 7,
            "retention value": s["retention_additional_value_eur"] == 0,
            "player-specific": abs(p["player_specific_eur"] - 172369112.92) < 0.01,
            "full sale": abs(p["full_sale_eur"] - 172369112.92) < 0.01,
            "fixed 50/50": abs(p["fixed_50_50_eur"] - 161646170.80) < 0.01,
            "difference": abs(p["difference_vs_fixed_50_50_eur"] - 10722942.12) < 0.01,
            "relative difference": abs(p["relative_difference_pct"] - 6.6336) < 0.0001,
            "per exit": abs(p["difference_per_exit_eur"] - 297859.50) < 0.01,
            "sensitivity runs": r["configurations"] == 1500,
            "p10": abs(r["difference_eur_p10"] - 5527556.81) < 0.01,
            "median": abs(r["difference_eur_median"] - 15716313.64) < 0.01,
            "p90": abs(r["difference_eur_p90"] - 33550827.08) < 0.01,
        }
        for label, passed in checks.items():
            if not passed:
                fail(errors, f"Headline mismatch: {label}")

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8") if (ROOT / "CITATION.cff").exists() else ""
    for expected in ["family-names: Halder", "given-names: Rupayan", "year: 2026"]:
        if expected not in citation:
            fail(errors, f"Citation metadata missing: {expected}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").exists() else ""
    for link in local_markdown_links(readme):
        if not (ROOT / link).exists():
            fail(errors, f"Broken README link: {link}")

    forbidden_path = "/Users/" + "rupayan"
    forbidden_names = ["Ale" + "jandro", "Ru" + "ben"]
    secret_patterns = [
        re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
        re.compile(r"(?i)(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}"),
        re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    ]

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if path.suffix.lower() in DISALLOWED_DATA_SUFFIXES:
            fail(errors, f"Disallowed data/model artifact: {rel}")
        if path.name.startswith(".env") or path.name == ".DS_Store" or "__pycache__" in path.parts:
            fail(errors, f"Disallowed temporary/private file: {rel}")
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"README.md", "LICENSE", ".gitignore"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if forbidden_path in text:
            fail(errors, f"Machine-specific absolute path in {rel}")
        for name in forbidden_names:
            if name.lower() in text.lower():
                fail(errors, f"Internal person name in {rel}")
        for pattern in secret_patterns:
            if pattern.search(text):
                fail(errors, f"Possible credential in {rel}: {pattern.pattern}")

    with (ROOT / "results" / "portfolio_benchmarks.csv").open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 3:
        fail(errors, "Unexpected portfolio benchmark row count")

    if errors:
        print("PUBLIC RELEASE VALIDATION: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PUBLIC RELEASE VALIDATION: PASS")
    print("Paper pages: 2")
    print("Headline values: PASS")
    print("README links: PASS")
    print("Portability/security scan: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
