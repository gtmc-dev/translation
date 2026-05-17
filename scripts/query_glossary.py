#!/usr/bin/env python3
"""
Query the TechMC Glossary CSV by term, category, short form, or language.

Usage:
    python scripts/query_glossary.py "chunk"
    python scripts/query_glossary.py --short "ITT"
    python scripts/query_glossary.py --category "1.12.2_magic"
    python scripts/query_glossary.py --lang zh "侦测"
    python scripts/query_glossary.py "observer" --columns en,zh,ja
"""

import argparse
import csv
import difflib
import io
import json
import sys
from collections import namedtuple
from pathlib import Path


LangColumns = namedtuple("LangColumns", ["term_idx", "desc_idx", "label"])

LANG_MAP: dict[str, LangColumns] = {
    "en": LangColumns(term_idx=2, desc_idx=3, label="English"),
    "ar": LangColumns(term_idx=4, desc_idx=5, label="Arabic"),
    "zh": LangColumns(term_idx=6, desc_idx=7, label="Chinese"),
    "fr": LangColumns(term_idx=8, desc_idx=9, label="French"),
    "de": LangColumns(term_idx=10, desc_idx=11, label="German"),
    "it": LangColumns(term_idx=12, desc_idx=13, label="Italian"),
    "ja": LangColumns(term_idx=14, desc_idx=15, label="Japanese"),
    "ko": LangColumns(term_idx=16, desc_idx=17, label="Korean"),
    "pt": LangColumns(term_idx=18, desc_idx=19, label="Portugese"),
    "ru": LangColumns(term_idx=20, desc_idx=21, label="Russian"),
    "es": LangColumns(term_idx=22, desc_idx=23, label="Spanish"),
}

DEFAULT_GLOSSARY = Path(__file__).resolve().parent.parent / \
    "glossary" / "TechMC Glossary.csv"

_SUBSTRING_BONUS = 0.9
_CONTESTED_MARKER = "*"


def load_glossary(csv_path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if not row:
                continue
            record: dict[str, str] = {
                "category": row[0].strip() if len(row) > 0 else "",
                "short": row[1].strip() if len(row) > 1 else "",
                "en": row[2].strip() if len(row) > 2 else "",
                "en_desc": row[3].strip() if len(row) > 3 else "",
            }
            for code, col in LANG_MAP.items():
                if code == "en":
                    continue
                term_val = row[col.term_idx].strip() if len(
                    row) > col.term_idx else ""
                desc_val = row[col.desc_idx].strip() if len(
                    row) > col.desc_idx else ""
                record[code] = term_val
                record[f"{code}_desc"] = desc_val
            rows.append(record)
    return rows


def search_term(
    glossary: list[dict[str, str]], query: str, threshold: float = 0.75
) -> list[tuple[dict[str, str], float]]:
    results: list[tuple[dict[str, str], float]] = []
    query_lower = query.lower()
    for row in glossary:
        term = row["en"].lower()
        ratio = difflib.SequenceMatcher(None, query_lower, term).ratio()
        if query_lower in term:
            ratio = max(ratio, _SUBSTRING_BONUS)
        if ratio >= threshold:
            results.append((row, ratio))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def search_short(glossary: list[dict[str, str]], short_form: str) -> list[dict[str, str]]:
    query = short_form.strip().upper()
    return [row for row in glossary if row["short"].upper() == query]


def filter_category(glossary: list[dict[str, str]], category: str) -> list[dict[str, str]]:
    target = category.strip()
    return [row for row in glossary if row["category"] == target]


def search_language(
    glossary: list[dict[str, str]], query: str, lang: str, threshold: float = 0.75
) -> list[tuple[dict[str, str], float]]:
    results: list[tuple[dict[str, str], float]] = []
    query_lower = query.lower()
    for row in glossary:
        text = row.get(lang, "").lower()
        if not text:
            continue
        ratio = difflib.SequenceMatcher(None, query_lower, text).ratio()
        if query_lower in text:
            ratio = max(ratio, _SUBSTRING_BONUS)
        if ratio >= threshold:
            results.append((row, ratio))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def _strip_contested(text: str) -> str:
    return text.rstrip(_CONTESTED_MARKER).strip()


def format_tsv(
    rows: list[tuple[dict[str, str], float]] | list[dict[str, str]],
    columns: list[str],
    has_score: bool = False,
) -> str:
    """Tab-separated values with header row."""
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(columns)
    for item in rows:
        if has_score:
            row_dict, score = item  # type: ignore[misc]
        else:
            row_dict = item  # type: ignore[assignment]
            score = None
        row_out: list[str] = []
        for col in columns:
            if col == "score" and has_score:
                row_out.append(f"{score:.2f}")
            elif col in LANG_MAP or col.endswith("_desc"):
                row_out.append(_strip_contested(row_dict.get(col, "")))
            else:
                row_out.append(row_dict.get(col, ""))
        writer.writerow(row_out)
    return buf.getvalue()


def format_json(
    rows: list[tuple[dict[str, str], float]] | list[dict[str, str]],
    columns: list[str],
    has_score: bool = False,
) -> str:
    """Compact JSON array (backward-compatible)."""
    out_list: list[dict[str, str | float]] = []
    for item in rows:
        if has_score:
            row_dict, score = item  # type: ignore[misc]
        else:
            row_dict = item  # type: ignore[assignment]
            score = None
        obj: dict[str, str | float] = {}
        for col in columns:
            if col == "score" and has_score:
                obj[col] = round(score, 2)  # type: ignore[arg-type]
            elif col in LANG_MAP or col.endswith("_desc"):
                obj[col] = _strip_contested(row_dict.get(col, ""))
            else:
                obj[col] = row_dict.get(col, "")
        out_list.append(obj)
    return json.dumps(out_list, separators=(",", ":"), ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query the TechMC Glossary CSV",
    )
    parser.add_argument(
        "query",
        nargs="?",
        default=None,
        help="Search term for fuzzy matching (English by default, or use --lang)",
    )
    parser.add_argument(
        "--short",
        default=None,
        help="Exact match on short form / abbreviation (e.g., ITT, BUD)",
    )
    parser.add_argument(
        "--category",
        default=None,
        help="Filter by category (e.g., 1.12.2_magic)",
    )
    parser.add_argument(
        "--lang",
        default=None,
        choices=list(LANG_MAP.keys()),
        help="Search in a specific language column instead of English",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Fuzzy matching threshold 0.0–1.0 (default: 0.75)",
    )
    parser.add_argument(
        "--columns",
        default="category,en,zh",
        help="Comma-separated columns to display (default: category,en,zh). "
             "Available: category, short, en, en_desc, ar, ar_desc, zh, zh_desc, "
             "fr, fr_desc, de, de_desc, it, it_desc, ja, ja_desc, "
             "ko, ko_desc, pt, pt_desc, ru, ru_desc, es, es_desc, score",
    )
    parser.add_argument(
        "--glossary",
        type=Path,
        default=DEFAULT_GLOSSARY,
        help="Path to TechMC Glossary.csv",
    )
    parser.add_argument(
        "--format",
        default="tsv",
        choices=["tsv", "json"],
        help="Output format: tsv (default, tab-separated) or json (compact array)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of rows to display (default: no limit; "
             "table output defaults to 50 when results exceed 50)",
    )
    args = parser.parse_args()

    if not any([args.query, args.short, args.category]):
        parser.error(
            "At least one of QUERY, --short, or --category is required")

    if not args.glossary.exists():
        print(
            f"Error: glossary CSV not found: {args.glossary}", file=sys.stderr)
        sys.exit(1)

    glossary = load_glossary(args.glossary)
    columns = [c.strip() for c in args.columns.split(",")]

    results: list[tuple[dict[str, str], float]] | list[dict[str, str]]
    has_score = False

    working_set = glossary
    if args.category:
        working_set = filter_category(glossary, args.category)
        if not working_set:
            print(f"No entries found for category '{args.category}'")
            sys.exit(0)

    if args.short:
        results = search_short(working_set, args.short)
    elif args.lang:
        results = search_language(
            working_set, args.query or "", args.lang, args.threshold)
        has_score = True
    else:
        results = search_term(working_set, args.query or "", args.threshold)
        has_score = True

    if args.limit is not None and len(results) > args.limit:
        results = results[: args.limit]

    if args.format == "tsv":
        formatted = format_tsv(results, columns, has_score)
    else:
        formatted = format_json(results, columns, has_score)

    if formatted:
        print(formatted)


if __name__ == "__main__":
    main()
