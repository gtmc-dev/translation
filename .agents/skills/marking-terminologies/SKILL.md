---
name: marking-terminologies
description: Use when marking source text with TechMC glossary terms, preparing marked-term reference files, adjusting mark_terms.py options, or saving match logs for later terminology review.
---

# Marking Terminologies

## Overview

Use this skill only for marking source text with TechMC glossary terms using `scripts/mark_terms.py`. For the full translation workflow, use the `/start-translate` command. For standalone glossary lookups, use `querying-terminologies`.

## When to Use

- Before translating long Minecraft technical prose.
- When the user asks to mark, find, or check glossary terms.
- When deciding whether a community term, abbreviation, or short form has an existing TechMC translation.

## TechMC Glossary

The TechMC glossary repository is embedded as a submodule at `./glossary`. Use it for non-official terms used by the community.

## Mark Glossary Terms

`scripts/mark_terms.py` scans text and wraps detected glossary terms with `<term>...</term>` tags.

Prefer shell redirection with `>>` when creating a reference log you may append to later:

```bash
python3 scripts/mark_terms.py input/article.md >> output/article.marked.md
```

Use `>` instead of `>>` only when you intentionally want to overwrite the reference file.

Common options:

```bash
# Default: match Chinese glossary terms
python3 scripts/mark_terms.py article.md

# Match another language
python3 scripts/mark_terms.py article.md --lang en

# Include matched terms and scores in stderr
python3 scripts/mark_terms.py article.md --verbose

# Use the script's own output option instead of redirection
python3 scripts/mark_terms.py article.md -o output/article.marked.md

# Ignore very short candidate terms
python3 scripts/mark_terms.py article.md --min-len 4
```

When using `--verbose` and you want both the marked text and match log for later reference, redirect them separately:

```bash
python3 scripts/mark_terms.py article.md --verbose >> output/article.marked.md 2>> output/article.matches.log
```

For standalone glossary lookups with `scripts/query_glossary.py`, use the `querying-terminologies` skill.

## Marking Checklist

- The marked output was saved as a reference file when it will be used later.
- `--verbose` match logs were redirected separately from marked text when both are needed.
- `>` was used only for intentional overwrite; `>>` was used for appendable reference notes.
- Unclear matches were checked with `querying-terminologies` instead of guessed.

## Common Mistakes

- Do not translate community terminology from memory when the TechMC glossary has an entry.
- Do not discard the marked-term output; keep it as a reference while translating.
- Do not use `>>` if the target reference file must be clean; remove the old file first or use `>` intentionally.
- Do not use this skill as the full translation workflow entrance; use `/start-translate` for that.
