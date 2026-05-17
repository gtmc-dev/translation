---
name: querying-minecraft-wiki
description: Use when looking up official Minecraft translations, verifying canonical game terms (blocks, items, entities, mobs), or bulk-querying Minecraft Wiki for translation references.
---

# Querying Minecraft Wiki

## Overview

Use this skill to query the Minecraft Wiki for official Minecraft translations. The wiki is the authoritative source for canonical game terms including blocks, items, entities, mobs, effects, advancements, and other official names.

## When to Use

- The user asks for official Minecraft translations for blocks, items, or entities.
- A source article contains Minecraft game terms that need official translations.
- You need to verify canonical names before translating.
- You need bulk translation references for a category (e.g., all blocks).
- You need to check a single term's official translation quickly.

## Core Command

`scripts/query_minecraft_wiki.py` queries minecraft.wiki via MediaWiki API.

```bash
python3 scripts/query_minecraft_wiki.py --category blocks --language zh
```

## Common Queries

### Bulk Category Lookup

```bash
# Get all blocks in Chinese (default: TSV)
python3 scripts/query_minecraft_wiki.py --category blocks --language zh

# Get all items in Japanese
python3 scripts/query_minecraft_wiki.py --category items --language ja

# Save as TSV for LLM consumption (most token-efficient)
python3 scripts/query_minecraft_wiki.py --category blocks --language zh --format tsv -o references/blocks-zh.tsv

# JSON for structured parsing
python3 scripts/query_minecraft_wiki.py --category entities --language es --format json
```

### Single Term Lookup

```bash
# Quick lookup (default TSV)
python3 scripts/query_minecraft_wiki.py --term "Diamond" --language zh

# Check a mob translation (JSON for programmatic use)
python3 scripts/query_minecraft_wiki.py --term "Creeper" --language zh --format json
```

### Output Formats

```bash
# TSV (default) - tab-separated, most token-efficient for LLM consumption
python3 scripts/query_minecraft_wiki.py --category blocks --language zh

# JSON - compact array (no indent) for programmatic use
python3 scripts/query_minecraft_wiki.py --category blocks --language zh --format json
```

Format comparison (for 1 record):
- tsv: `"blocks"\t"Diamond Block"\t"diamond_block"\t"zh"\t"钻石块"` (~55 chars)
- json: `[{"category":"blocks","english_title":"Diamond Block","nameid":"diamond_block","language":"zh","localized_name":"钻石块"}]` (~100 chars)

Prefer `--format tsv` (default) for LLM reference data (most token-efficient). Use `--format json` when you need structured data for parsing.

### Output to File

```bash
# TSV (default) for LLM reference
python3 scripts/query_minecraft_wiki.py --category blocks --language zh -o references/blocks-zh.tsv

# JSON for programmatic use
python3 scripts/query_minecraft_wiki.py --category items --language zh --format json -o references/items-zh.json
python3 scripts/query_minecraft_wiki.py --category items --language ja --format json -o references/items-ja.json
```

### Development & Testing

```bash
# Limit results for quick testing
python3 scripts/query_minecraft_wiki.py --category blocks --language zh --limit 10 --verbose

# Include incomplete records for audit
python3 scripts/query_minecraft_wiki.py --category blocks --language zh --include-missing --format table

# Disable cache for fresh data
python3 scripts/query_minecraft_wiki.py --category blocks --language zh --no-cache
```

## Output Structure

Each record contains:

- `category`: Category queried (blocks/items/entities) or "term" for single lookups
- `english_title`: English page title from Minecraft Wiki
- `nameid`: Minecraft namespaced ID (e.g., "diamond_block")
- `language`: Target language code
- `localized_name`: Official translated name

Example outputs:

```text
# TSV (default)
"category"	"english_title"	"nameid"	"language"	"localized_name"
"blocks"	"Diamond Block"	"diamond_block"	"zh"	"钻石块"
"blocks"	"Obsidian"	"obsidian"	"zh"	"黑曜石"
```

```json
# JSON (compact array)
[{"category":"blocks","english_title":"Diamond Block","nameid":"diamond_block","language":"zh","localized_name":"钻石块"},{"category":"blocks","english_title":"Obsidian","nameid":"obsidian","language":"zh","localized_name":"黑曜石"}]
```

```text
# TSV (tab-separated, most token-efficient)
category  english_title   nameid          language  localized_name
blocks    Diamond Block   diamond_block   zh        钻石块
```

```text
# NDJSON (one JSON object per line)
{"category":"blocks","english_title":"Diamond Block","nameid":"diamond_block","language":"zh","localized_name":"钻石块"}
```

```json
# JSON (compact array, no indent)
[{"category":"blocks","english_title":"Diamond Block","nameid":"diamond_block","language":"zh","localized_name":"钻石块"}]
```

## Supported Categories

- `blocks` - All block types (Category:Blocks on wiki)
- `items` - All items (Category:Items on wiki)
- `entities` - All entities and mobs (Category:Entities on wiki)

## Supported Languages

Any language code supported by Minecraft Wiki interlanguage links:

- `zh` - Chinese (Simplified/Traditional)
- `ja` - Japanese
- `es` - Spanish
- `de` - German
- `fr` - French
- `pt` - Portuguese
- `ru` - Russian
- And more...

## Cache Behavior

- Cache location: `.cache/minecraft-wiki/`
- Default TTL: 7 days
- Cache key: SHA1 of API URL + sorted params
- Use `--no-cache` to bypass cache
- Use `--cache-ttl SECONDS` to customize TTL

## Missing Data Policy

By default, the script skips records with:
- Missing `localized_name` (no translation available)
- Missing `nameid` (no ID table in wiki page)

Use `--include-missing` to include incomplete records for audit purposes.

## Integration with Translation Workflow

This tool complements the TechMC glossary tools:

- **Minecraft Wiki** (`query_minecraft_wiki.py`): Official Minecraft names
- **TechMC Glossary** (`query_glossary.py`): Community/technical terminology

Use both when translating Minecraft content:

1. Query Minecraft Wiki for official game terms
2. Query TechMC Glossary for community terms and abbreviations
3. Translate with both references available

## Common Mistakes

- Do not use this for community terminology - use `query_glossary.py` instead
- Do not assume all pages have translations - some may be missing
- Do not assume all pages have nameids - some wiki pages lack ID tables
- Do not query without `--language` - it's required
- Do not use this for non-Minecraft terms

## Troubleshooting

### No results returned

- Check if the term exists on minecraft.wiki
- Try `--include-missing` to see if data is incomplete
- Use `--verbose` to see skip counts and reasons

### Slow queries

- First run fetches from API and caches
- Subsequent runs use cache (much faster)
- Use `--limit` for testing to avoid full category fetches

### Cache issues

- Use `--no-cache` to force fresh data
- Delete `.cache/minecraft-wiki/` to clear all cache
- Check cache TTL with `--verbose`

## Examples

### Translate a Minecraft guide

```bash
# Get all blocks in Chinese for reference
python3 scripts/query_minecraft_wiki.py --category blocks --language zh -o references/blocks-zh.tsv

# Look up specific terms as needed
python3 scripts/query_minecraft_wiki.py --term "Redstone" --language zh
python3 scripts/query_minecraft_wiki.py --term "Piston" --language zh
```

### Verify translations

```bash
# Check if your translation matches official
python3 scripts/query_minecraft_wiki.py --term "Diamond Sword" --language zh --format table
```

### Create multi-language reference

```bash
# Build reference files for multiple languages
for lang in zh ja es de fr; do
  python3 scripts/query_minecraft_wiki.py --category blocks --language $lang -o references/blocks-$lang.tsv
done
```

## Manual Wiki References

The script returns top-level category entries only. For anything beyond a canonical name, fetch the wiki page directly. Common cases where the script is insufficient:

- **Variants** — items or blocks with sub-types (e.g. wood types, dye colors, coral variants): the script returns the base name; fetch the item's wiki page to get all variant translations.
- **Details and descriptions** — mechanics explanations, lore, usage notes, or any translated prose beyond the name itself.
- **Entities with states** — mobs that have multiple forms (e.g. villager professions, horse variants, slime sizes): each state may have a distinct translated name on the wiki page.
- **Advancements, effects, enchantments, potions** — not covered by the script's categories; fetch the relevant wiki page or index (see @REFERENCE.md).
- **Edge cases and disambiguation** — when a term has multiple wiki entries (e.g. "Torch" vs "Soul Torch"), the script may return only one; fetch the page to confirm the correct translation.
- **Non-item content** — structures, biomes, commands, game mechanics: no script support; use the wiki page directly.

Fetch strategies:
- Use `webfetch https://minecraft.wiki/w/<PageName>` for English source pages.
- For localized names, use the language-specific wiki (e.g. `https://zh.minecraft.wiki/w/<PageName>`) or append `?uselang=<lang>` to the English URL.
- Use the MediaWiki API for structured extraction: `https://minecraft.wiki/api.php?action=parse&page=<PageName>&prop=wikitext&format=json`

For a full index of wiki URLs by content type, see @REFERENCE.md.

## Resources

- Minecraft Wiki: https://minecraft.wiki/
- Chinese Wiki: https://zh.minecraft.wiki/
- MediaWiki API: https://minecraft.wiki/api.php
- Wiki Style Guide: https://minecraft.wiki/w/Minecraft_Wiki:Style_guide
- **Extended Reference**: See `REFERENCE.md` for complete wiki index pages
