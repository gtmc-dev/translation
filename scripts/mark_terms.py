#!/usr/bin/env python3
"""
Mark glossary terms in a text file with <term>...</term> tags via fuzzy matching.

Reads an input text file, compares its content against the TechMC Glossary CSV,
and outputs the text with matched terms wrapped in <term> tags.

Usage:
    python scripts/mark_terms.py article.txt
    python scripts/mark_terms.py article.txt --lang zh --threshold 0.8
    python scripts/mark_terms.py article.txt -o marked.txt --verbose
"""

import argparse
import csv
import difflib
import re
import sys
from collections import namedtuple
from pathlib import Path


LangColumns = namedtuple("LangColumns", ["term_idx", "desc_idx"])

LANG_MAP: dict[str, LangColumns] = {
    "en": LangColumns(term_idx=2, desc_idx=3),
    "ar": LangColumns(term_idx=4, desc_idx=5),
    "zh": LangColumns(term_idx=6, desc_idx=7),
    "fr": LangColumns(term_idx=8, desc_idx=9),
    "de": LangColumns(term_idx=10, desc_idx=11),
    "it": LangColumns(term_idx=12, desc_idx=13),
    "ja": LangColumns(term_idx=14, desc_idx=15),
    "ko": LangColumns(term_idx=16, desc_idx=17),
    "pt": LangColumns(term_idx=18, desc_idx=19),
    "ru": LangColumns(term_idx=20, desc_idx=21),
    "es": LangColumns(term_idx=22, desc_idx=23),
}

DEFAULT_GLOSSARY = Path(__file__).resolve().parent.parent / "glossary" / "TechMC Glossary.csv"

_TERM_CHAR = re.compile(r"\S+")
_CONTESTED_TERM = re.compile(r"\*+$")
_CJK_RANGE = re.compile(r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]")


def load_glossary(csv_path: Path, target_lang: str, min_len: int = 2) -> list[str]:
    lang_cols = LANG_MAP.get(target_lang, LANG_MAP["en"])

    terms: set[str] = set()
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if not row or len(row) < 3:
                continue

            candidates: list[str] = []
            full = row[2].strip() if len(row) > 2 else ""
            if full:
                candidates.append(full)
            short = row[1].strip() if len(row) > 1 else ""
            if short:
                candidates.append(short)
            if target_lang != "en" and len(row) > lang_cols.term_idx:
                translated = row[lang_cols.term_idx].strip()
                if translated:
                    candidates.append(translated)

            for t in candidates:
                cleaned = _CONTESTED_TERM.sub("", t).strip()
                if cleaned and len(cleaned) >= min_len:
                    terms.add(cleaned)

    return sorted(terms, key=len, reverse=True)


def _tokenize(text: str) -> list[tuple[str, int, int]]:
    tokens: list[tuple[str, int, int]] = []
    for m in _TERM_CHAR.finditer(text):
        tokens.append((m.group(), m.start(), m.end()))
    return tokens


def _cjk_char_ngrams(
    token_text: str, token_start: int, min_n: int = 2, max_n: int = 8
) -> list[tuple[str, int, int]]:
    ngrams: list[tuple[str, int, int]] = []
    for n in range(min_n, min(max_n, len(token_text)) + 1):
        for i in range(len(token_text) - n + 1):
            ngram_text = token_text[i : i + n]
            start = token_start + i
            end = token_start + i + n
            ngrams.append((ngram_text, start, end))
    return ngrams


def find_matches(
    text: str,
    glossary_terms: list[str],
    threshold: float = 0.85,
) -> list[tuple[int, int, str, float]]:
    tokens = _tokenize(text)
    matches: list[tuple[int, int, str, float]] = []

    terms_lower = [(t, t.lower()) for t in glossary_terms]
    use_cjk = _CJK_RANGE.search(text) is not None

    for n in range(1, min(6, len(tokens) + 1)):
        for i in range(len(tokens) - n + 1):
            phrase = " ".join(tok[0] for tok in tokens[i : i + n])
            phrase_lower = phrase.lower()
            span_start = tokens[i][1]
            span_end = tokens[i + n - 1][2]

            for term, term_lower in terms_lower:
                if phrase_lower == term_lower:
                    matches.append((span_start, span_end, term, 1.0))
                    continue

                ratio = difflib.SequenceMatcher(None, phrase_lower, term_lower).ratio()
                if ratio >= threshold:
                    matches.append((span_start, span_end, term, ratio))

    if use_cjk:
        for tok_text, tok_start, _tok_end in tokens:
            if len(tok_text) < 3:
                continue
            for ngram_text, ng_start, ng_end in _cjk_char_ngrams(tok_text, tok_start):
                ngram_lower = ngram_text.lower()
                for term, term_lower in terms_lower:
                    if ngram_lower == term_lower:
                        matches.append((ng_start, ng_end, term, 1.0))
                        continue
                    ratio = difflib.SequenceMatcher(
                        None, ngram_lower, term_lower
                    ).ratio()
                    if ratio >= threshold:
                        matches.append((ng_start, ng_end, term, ratio))

    return matches


def resolve_overlaps(
    matches: list[tuple[int, int, str, float]],
) -> list[tuple[int, int, str, float]]:
    if not matches:
        return []

    sorted_matches = sorted(matches, key=lambda m: ((m[1] - m[0]), m[3]), reverse=True)

    selected: list[tuple[int, int, str, float]] = []
    occupied: list[tuple[int, int]] = []

    for start, end, term, ratio in sorted_matches:
        overlap = any(
            start < occ_end and end > occ_start for occ_start, occ_end in occupied
        )
        if not overlap:
            selected.append((start, end, term, ratio))
            occupied.append((start, end))
            continue

        for j, (occ_start, occ_end) in enumerate(occupied):
            if start >= occ_start and end <= occ_end and ratio >= selected[j][3] + 0.05:
                selected[j] = (start, end, term, ratio)
                occupied[j] = (start, end)
                break

    return sorted(selected, key=lambda m: m[0])


def mark_text(text: str, spans: list[tuple[int, int, str, float]]) -> str:
    if not spans:
        return text

    result: list[str] = []
    pos = 0
    for start, end, _term, _ratio in spans:
        result.append(text[pos:start])
        result.append("<term>")
        result.append(text[start:end])
        result.append("</term>")
        pos = end
    result.append(text[pos:])
    return "".join(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mark glossary terms in a text file with <term> tags",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input text file to scan",
    )
    parser.add_argument(
        "--lang",
        default="zh",
        choices=list(LANG_MAP.keys()),
        help="Target language for glossary matching (default: zh)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Fuzzy matching similarity threshold 0.0–1.0 (default: 0.85)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--glossary",
        type=Path,
        default=DEFAULT_GLOSSARY,
        help="Path to TechMC Glossary.csv",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print matched terms to stderr",
    )
    parser.add_argument(
        "--min-len",
        type=int,
        default=2,
        help="Minimum term length to consider (default: 2)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if not args.glossary.exists():
        print(f"Error: glossary CSV not found: {args.glossary}", file=sys.stderr)
        sys.exit(1)

    sys.stderr.write(f"Loading glossary ({args.lang})...\n")
    terms = load_glossary(args.glossary, args.lang, args.min_len)
    sys.stderr.write(f"Loaded {len(terms)} unique terms.\n")

    text = args.input.read_text(encoding="utf-8")

    sys.stderr.write(f"Matching with threshold {args.threshold}...\n")
    matches = find_matches(text, terms, args.threshold)
    resolved = resolve_overlaps(matches)

    if args.verbose:
        print(f"\nMatched {len(resolved)} terms:", file=sys.stderr)
        for start, end, term, ratio in resolved:
            snippet = text[start:end]
            print(f"  [{ratio:.2f}] {term!r} ← {snippet!r}", file=sys.stderr)
        print(file=sys.stderr)

    output = mark_text(text, resolved)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
        sys.stderr.write(f"Output written to {args.output}\n")
    else:
        sys.stdout.write(output)


if __name__ == "__main__":
    main()
