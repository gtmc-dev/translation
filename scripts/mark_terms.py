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
from dataclasses import dataclass
import difflib
import re
import sys
from collections import defaultdict, namedtuple
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
_WORD_CHAR = re.compile(r"[A-Za-z0-9_]+")
_CONTESTED_TERM = re.compile(r"\*+$")
_CJK_RANGE = re.compile(r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]")
_LATIN_RANGE = re.compile(r"[A-Za-z]")
_LATIN_BOUNDARY = re.compile(r"(?<![A-Za-z0-9_]){}(?![A-Za-z0-9_])")
_EXISTING_TERM = re.compile(r"<term>.*?</term>", re.DOTALL)
_HTML_TAG = re.compile(r"</?[^>]+>")
_INLINE_CODE = re.compile(r"`+[^`]*`+")
_URL = re.compile(r"https?://[^\s)]+")
_MARKDOWN_LINK_DESTINATION = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


@dataclass(frozen=True)
class GlossaryTerm:
    text: str
    source: str


@dataclass(frozen=True)
class TermIndex:
    exact_terms: tuple[GlossaryTerm, ...]
    fuzzy_terms_by_word_count: dict[int, tuple[GlossaryTerm, ...]]


def _clean_term(term: str) -> str:
    return _CONTESTED_TERM.sub("", term).strip()


def _term_variants(term: str) -> list[str]:
    variants = [term]
    if "/" in term:
        variants.extend(part.strip() for part in term.split("/") if part.strip())
    return variants


def load_glossary(
    csv_path: Path, target_lang: str, min_len: int = 2
) -> list[GlossaryTerm]:
    lang_cols = LANG_MAP.get(target_lang, LANG_MAP["en"])

    terms: dict[tuple[str, str], GlossaryTerm] = {}
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if not row or len(row) < 3:
                continue

            candidates: list[tuple[str, str]] = []
            full = row[2].strip() if len(row) > 2 else ""
            if full:
                candidates.append((full, "en"))
            short = row[1].strip() if len(row) > 1 else ""
            if short:
                candidates.append((short, "short"))
            if target_lang != "en" and len(row) > lang_cols.term_idx:
                translated = row[lang_cols.term_idx].strip()
                if translated:
                    candidates.append((translated, "translation"))

            for candidate, source in candidates:
                for variant in _term_variants(_clean_term(candidate)):
                    cleaned = _clean_term(variant)
                    if cleaned and len(cleaned) >= min_len:
                        terms[(cleaned.lower(), source)] = GlossaryTerm(cleaned, source)

    return sorted(terms.values(), key=lambda term: len(term.text), reverse=True)


def _tokenize(text: str) -> list[tuple[str, int, int]]:
    tokens: list[tuple[str, int, int]] = []
    for m in _TERM_CHAR.finditer(text):
        tokens.append((m.group(), m.start(), m.end()))
    return tokens


def _merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not spans:
        return []

    merged: list[tuple[int, int]] = []
    for start, end in sorted(spans):
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
            continue
        merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    return merged


def _protected_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []

    if text.startswith("---\n"):
        frontmatter_end = text.find("\n---", 4)
        if frontmatter_end != -1:
            line_end = text.find("\n", frontmatter_end + 4)
            spans.append((0, len(text) if line_end == -1 else line_end + 1))

    in_fence = False
    fence_start = 0
    offset = 0
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            if in_fence:
                spans.append((fence_start, offset + len(line)))
                in_fence = False
            else:
                fence_start = offset
                in_fence = True
        offset += len(line)
    if in_fence:
        spans.append((fence_start, len(text)))

    for pattern in (_EXISTING_TERM, _HTML_TAG, _INLINE_CODE, _URL):
        spans.extend((m.start(), m.end()) for m in pattern.finditer(text))

    for m in _MARKDOWN_LINK_DESTINATION.finditer(text):
        spans.append((m.start(1), m.end(1)))

    return _merge_spans(spans)


def _unprotected_segments(text: str) -> list[tuple[str, int]]:
    segments: list[tuple[str, int]] = []
    pos = 0
    for start, end in _protected_spans(text):
        if pos < start:
            segments.append((text[pos:start], pos))
        pos = end
    if pos < len(text):
        segments.append((text[pos:], pos))
    return segments


def _is_latin_short(term: str) -> bool:
    return len(term) <= 4 and _LATIN_RANGE.search(term) is not None and _CJK_RANGE.search(term) is None


def _is_cjk_term(term: str) -> bool:
    return _CJK_RANGE.search(term) is not None


def _word_count(term: str) -> int:
    return len(_TERM_CHAR.findall(term))


def build_term_index(glossary_terms: list[GlossaryTerm]) -> TermIndex:
    exact_terms: list[GlossaryTerm] = []
    fuzzy_terms_by_word_count: defaultdict[int, list[GlossaryTerm]] = defaultdict(list)

    for term in glossary_terms:
        exact_terms.append(term)
        if term.source == "en" and not _is_cjk_term(term.text) and len(term.text) >= 4:
            fuzzy_terms_by_word_count[_word_count(term.text)].append(term)

    return TermIndex(
        exact_terms=tuple(exact_terms),
        fuzzy_terms_by_word_count={
            count: tuple(terms) for count, terms in fuzzy_terms_by_word_count.items()
        },
    )


def _has_latin_boundaries(text: str, start: int, end: int) -> bool:
    before = text[start - 1] if start > 0 else ""
    after = text[end] if end < len(text) else ""
    return not (before.isascii() and (before.isalnum() or before == "_")) and not (
        after.isascii() and (after.isalnum() or after == "_")
    )


def _find_exact_matches(
    segment: str, segment_start: int, term_index: TermIndex
) -> list[tuple[int, int, str, float]]:
    matches: list[tuple[int, int, str, float]] = []

    for term in term_index.exact_terms:
        pattern = re.escape(term.text)
        flags = re.IGNORECASE if term.source == "short" or not _is_cjk_term(term.text) else 0
        for m in re.finditer(pattern, segment, flags):
            start = segment_start + m.start()
            end = segment_start + m.end()
            if _is_latin_short(term.text) and not _has_latin_boundaries(segment, m.start(), m.end()):
                continue
            matches.append((start, end, term.text, 1.0))

    return matches


def find_matches(
    text: str,
    glossary_terms: list[GlossaryTerm],
    threshold: float = 0.85,
) -> list[tuple[int, int, str, float]]:
    matches: list[tuple[int, int, str, float]] = []
    term_index = build_term_index(glossary_terms)

    for segment, segment_start in _unprotected_segments(text):
        matches.extend(_find_exact_matches(segment, segment_start, term_index))

        tokens = _tokenize(segment)
        max_window = min(6, len(tokens) + 1)
        for n in range(1, max_window):
            fuzzy_terms = term_index.fuzzy_terms_by_word_count.get(n, ())
            if not fuzzy_terms:
                continue
            for i in range(len(tokens) - n + 1):
                phrase = " ".join(tok[0] for tok in tokens[i : i + n])
                if _CJK_RANGE.search(phrase) or not _WORD_CHAR.search(phrase):
                    continue
                phrase_lower = phrase.lower()
                span_start = segment_start + tokens[i][1]
                span_end = segment_start + tokens[i + n - 1][2]

                for term in fuzzy_terms:
                    term_lower = term.text.lower()
                    if abs(len(phrase_lower) - len(term_lower)) > 3:
                        continue
                    ratio = difflib.SequenceMatcher(None, phrase_lower, term_lower).ratio()
                    if ratio >= threshold:
                        matches.append((span_start, span_end, term.text, ratio))
                    continue

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
