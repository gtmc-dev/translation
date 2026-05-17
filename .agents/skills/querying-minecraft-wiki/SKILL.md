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
python3 scripts/query_minecraft_wiki.py --category blocks --language zh --format table
```

## Common Queries

### Bulk Category Lookup

```bash
# Get all blocks in Chinese
python3 scripts/query_minecraft_wiki.py --category blocks --language zh --format json

# Get all items in Japanese
python3 scripts/query_minecraft_wiki.py --category items --language ja --format table

# Get all entities/mobs in Spanish
python3 scripts/query_minecraft_wiki.py --category entities --language es --format csv
```

### Single Term Lookup

```bash
# Quick lookup for one term
python3 scripts/query_minecraft_wiki.py --term "Diamond" --language zh --format table

# Check a mob translation
python3 scripts/query_minecraft_wiki.py --term "Creeper" --language zh --format json

# Verify a block name
python3 scripts/query_minecraft_wiki.py --term "Stone" --language ja --format table
```

### Output Formats

```bash
# JSON (default) - for programmatic use
python3 scripts/query_minecraft_wiki.py --category blocks --language zh --format json

# CSV - for spreadsheet import
python3 scripts/query_minecraft_wiki.py --category items --language zh --format csv

# Table - for human reading
python3 scripts/query_minecraft_wiki.py --category entities --language zh --format table
```

### Output to File

```bash
# Save to file instead of stdout
python3 scripts/query_minecraft_wiki.py --category blocks --language zh -o references/blocks-zh.json

# Create reference files for multiple languages
python3 scripts/query_minecraft_wiki.py --category items --language zh -o references/items-zh.json
python3 scripts/query_minecraft_wiki.py --category items --language ja -o references/items-ja.json
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

Example JSON output:

```json
[
  {
    "category": "blocks",
    "english_title": "Diamond Block",
    "nameid": "diamond_block",
    "language": "zh",
    "localized_name": "钻石块"
  }
]
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
python3 scripts/query_minecraft_wiki.py --category blocks --language zh -o references/blocks-zh.json

# Look up specific terms as needed
python3 scripts/query_minecraft_wiki.py --term "Redstone" --language zh --format table
python3 scripts/query_minecraft_wiki.py --term "Piston" --language zh --format table
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
  python3 scripts/query_minecraft_wiki.py --category blocks --language $lang -o references/blocks-$lang.json
done
```

## Manual Wiki References

For content types not covered by the script (versions, structures, effects, biomes, advancements, enchantments, potions, commands), see `REFERENCE.md` in this skill directory for comprehensive wiki URLs.

## Resources

- Minecraft Wiki: https://minecraft.wiki/
- Chinese Wiki: https://zh.minecraft.wiki/
- MediaWiki API: https://minecraft.wiki/api.php
- Wiki Style Guide: https://minecraft.wiki/w/Minecraft_Wiki:Style_guide
- **Extended Reference**: See `REFERENCE.md` for complete wiki index pages
