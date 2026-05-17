---
name: querying-terminologies
description: Use when searching the TechMC glossary, checking abbreviations or short forms, comparing translated terminology, filtering glossary categories, or choosing columns for terminology lookup.
---

# Querying Terminologies

## Overview

Use this skill to query `./glossary/TechMC Glossary.csv` before choosing community terminology. Prefer querying the glossary over guessing, especially for abbreviations, redstone/mechanics terms, and terms with descriptions.

## When to Use

- The user asks what a TechMC term, abbreviation, or category means.
- A source article contains a community term that may have an established translation.
- You need to compare English, Chinese, Japanese, Spanish, or description columns before translating.
- You need a narrow glossary subset before marking or translating text.

## Core Command

`scripts/query_glossary.py` auto-detects the glossary at `./glossary/TechMC Glossary.csv`.

```bash
python3 scripts/query_glossary.py "chunk"
```

Default behavior fuzzy-searches English terms and displays `category`, `en`, and `zh`.

## Common Queries

```bash
# Fuzzy search English terms
python3 scripts/query_glossary.py "chunk"

# Exact match on abbreviation / short form
python3 scripts/query_glossary.py --short "ITT"

# Filter by category
python3 scripts/query_glossary.py --category "1.12.2_magic"

# Search in a specific language column
python3 scripts/query_glossary.py --lang zh "侦测"

# Loosen or tighten fuzzy matching
python3 scripts/query_glossary.py "observer" --threshold 0.8

# Show selected translation columns
python3 scripts/query_glossary.py "observer" --columns category,short,en,zh,ja,es

# Include descriptions for context
python3 scripts/query_glossary.py "chunk" --columns category,short,en,en_desc,zh,zh_desc
```

## Combining Filters

Category filters narrow the working set before searching terms, short forms, or language columns:

```bash
python3 scripts/query_glossary.py --category "1.12.2_magic" "update"
python3 scripts/query_glossary.py --category "1.12.2_magic" --short "ITT"
python3 scripts/query_glossary.py --category "1.12.2_magic" --lang zh "更新"
```

## Output Formats

```bash
# TSV (default) - tab-separated, most token-efficient
python3 scripts/query_glossary.py "chunk"

# JSON - compact array for programmatic use
python3 scripts/query_glossary.py "chunk" --format json
```

Format guide:
- `tsv` (default): Tab-separated, most token-efficient for LLM reference data
- `json`: Compact JSON array (no indent)

Use `--limit N` to cap output rows.

## Columns

Available columns: `category`, `short`, `en`, `en_desc`, `ar`, `ar_desc`, `zh`, `zh_desc`, `fr`, `fr_desc`, `de`, `de_desc`, `it`, `it_desc`, `ja`, `ja_desc`, `ko`, `ko_desc`, `pt`, `pt_desc`, `ru`, `ru_desc`, `es`, `es_desc`, `score`.

Use description columns when multiple candidate terms look similar. Use `score` only for fuzzy searches (`query` or `--lang`); exact short-form and category-only output has no score.

## Saving Query Output

For later translation reference, save useful query results to a notes file. Prefer `>>` when appending multiple lookups:

```bash
python3 scripts/query_glossary.py "observer" --columns category,short,en,en_desc,zh,zh_desc >> output/terminology-notes.txt
python3 scripts/query_glossary.py --short "ITT" --columns category,short,en,zh >> output/terminology-notes.txt
```

Use `>` only when intentionally replacing the notes file.

## Glossary Override

Use `--glossary <path>` only when intentionally querying a different CSV:

```bash
python3 scripts/query_glossary.py "chunk" --glossary glossary/TechMC\ Glossary.csv
```

## Common Mistakes

- Do not use fuzzy search for abbreviations; use `--short` for exact short-form lookup.
- Do not choose between similar terms without checking description columns.
- Do not assume a category filter is a search term; `--category` limits the result set first.
- Do not overwrite terminology notes with `>` when you meant to append with `>>`.
- Do not use TechMC glossary terms as official Minecraft item/block names; check Minecraft Wiki language pages for official names.
