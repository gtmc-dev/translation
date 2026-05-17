---
description: Minecraft Wiki reference URLs and query tools for official game term translations
---

# Minecraft Wiki Reference

The Minecraft Wiki is the authoritative source for official Minecraft translations. This skill documents reference URLs and tools for translator workflows.

## Quick Reference

**Automated Query Tool:**
- `scripts/query_minecraft_wiki.py` — Query blocks/items/entities with caching
  - Output formats: `tsv` (default, tab-separated) or `json` (compact array)
  - Prefer TSV for LLM reference data (most token-efficient), JSON for programmatic use

**Language-Specific Wikis:**
- English: `https://minecraft.wiki/`
- Chinese: `https://zh.minecraft.wiki/` (uses zh-cn variant for canonical translations)
- Japanese: `https://ja.minecraft.wiki/`
- Spanish: `https://es.minecraft.wiki/`

**MediaWiki API:**
- `https://minecraft.wiki/api.php` — Standard MediaWiki API endpoint

## When to Use

**Use the automated script when:**
- Translating blocks, items, or entities in bulk
- Building reference materials for long translation tasks
- Verifying canonical names programmatically

**Use manual wiki pages when:**
- The script doesn't cover the content type (versions, structures, effects, biomes, advancements, enchantments, potions, commands)
- You need context beyond just the translated name (descriptions, mechanics, IDs)
- You need to verify edge cases or unofficial names

## Version History References

### Java Edition
| Page | URL | Content |
|------|-----|---------|
| Version history (master) | `https://minecraft.wiki/w/Version_history` | Cross-edition version index |
| Java Edition versions | `https://minecraft.wiki/w/Java_Edition_version_history` | All releases from 1.0 to current |
| Development versions | `https://minecraft.wiki/w/Java_Edition_version_history/Development_versions` | Snapshots, pre-releases, RCs |
| Release timeline | `https://minecraft.wiki/w/Java_Edition_release_timeline` | Chronological list of every build |
| Version types | `https://minecraft.wiki/w/Version_types` | Definitions: snapshots, pre-releases, hotfixes |
| Version formats | `https://minecraft.wiki/w/Version_formats` | Version numbering schemes |

### Bedrock Edition
| Page | URL | Content |
|------|-----|---------|
| Bedrock versions | `https://minecraft.wiki/w/Bedrock_Edition_version_history` | All Bedrock releases |
| Development versions | `https://minecraft.wiki/w/Bedrock_Edition_version_history/Development_versions` | Betas and Previews |
| Protocol versions | `https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Bedrock_Protocol_version_numbers` | Game version → protocol mapping |

### Other Editions
| Page | URL | Content |
|------|-----|---------|
| Legacy Console timeline | `https://minecraft.wiki/w/Legacy_Console_Edition_release_timeline` | Xbox, PlayStation, Wii U, Switch |
| Chronology of events | `https://minecraft.wiki/w/Chronology_of_events` | All Minecraft events by date |

## Content Index Pages

### Blocks & Items
| Page | URL | Content |
|------|-----|---------|
| Blocks | `https://minecraft.wiki/w/Block` | All 740+ blocks with images, properties |
| Items | `https://minecraft.wiki/w/Item` | All 477+ items |
| Data values (Java) | `https://minecraft.wiki/w/Java_Edition_data_values` | Numeric/string IDs (post-1.13) |
| Data values (pre-flattening) | `https://minecraft.wiki/w/Java_Edition_pre-flattening_data_values` | Legacy numeric IDs (pre-1.13) |
| Data values (Bedrock) | `https://minecraft.wiki/w/Bedrock_Edition_data_values` | Bedrock Edition numeric IDs |

### Mobs & Entities
| Page | URL | Content |
|------|-----|---------|
| Mob | `https://minecraft.wiki/w/Mob` | Complete list of all mobs by category |
| Entity | `https://minecraft.wiki/w/Entity` | All entity types with IDs |

### Biomes
| Page | URL | Content |
|------|-----|---------|
| Biome | `https://minecraft.wiki/w/Biome` | 65 (JE) / 87 (BE) biomes with climate tables, IDs |

### Enchantments
| Page | URL | Content |
|------|-----|---------|
| Enchantment | `https://minecraft.wiki/w/Enchantment` | 36+ enchantments with IDs, max levels, incompatibilities |
| Enchanting mechanics | `https://minecraft.wiki/w/Enchanting_table_mechanics` | How enchanting works |

### Status Effects
| Page | URL | Content |
|------|-----|---------|
| Effect | `https://minecraft.wiki/w/Effect` | 34 status effects with IDs, types, descriptions, potency |
| Effect colors | `https://minecraft.wiki/w/Effect_colors` | RGB color values for each effect |

### Potions
| Page | URL | Content |
|------|-----|---------|
| Potion | `https://minecraft.wiki/w/Potion` | All potion types, durations, modifiers |
| Brewing | `https://minecraft.wiki/w/Brewing` | Brewing recipes and mechanics |
| Splash Potion | `https://minecraft.wiki/w/Splash_Potion` | Throwable potion variants |
| Lingering Potion | `https://minecraft.wiki/w/Lingering_Potion` | Area-effect potions |
| Tipped Arrow | `https://minecraft.wiki/w/Tipped_arrow` | Arrows with status effects |

### Structures
| Page | URL | Content |
|------|-----|---------|
| Structure | `https://minecraft.wiki/w/Structure` | All generated structures with IDs, biome locations |

### Advancements & Achievements
| Page | URL | Content |
|------|-----|---------|
| Advancement | `https://minecraft.wiki/w/Advancement` | 125+ advancements with descriptions, criteria |
| Achievement | `https://minecraft.wiki/w/Achievement` | Bedrock Edition achievements |
| Hidden advancements | `https://minecraft.wiki/w/Hidden_advancements` | The 9 hidden advancements |

### Commands
| Page | URL | Content |
|------|-----|---------|
| Command | `https://minecraft.wiki/w/Command` | All commands with syntax, OP levels |
| Commands (category) | `https://minecraft.wiki/w/Category:Commands` | 322 command sub-pages |

### Trades & Loot
| Page | URL | Content |
|------|-----|---------|
| Trading | `https://minecraft.wiki/w/Trading` | Villager trade tables |
| Loot table | `https://minecraft.wiki/w/Loot_table` | Loot table mechanics and references |

## Category Pages

### Primary Content Categories
| Category | URL | Members |
|----------|-----|---------|
| Blocks | `https://minecraft.wiki/w/Category:Blocks` | ~740 |
| Items | `https://minecraft.wiki/w/Category:Items` | ~477 |
| Mobs | `https://minecraft.wiki/w/Category:Mobs` | Large |
| Entities | `https://minecraft.wiki/w/Category:Entities` | Large |
| Biomes | `https://minecraft.wiki/w/Category:Biomes` | Large |
| Structures | `https://minecraft.wiki/w/Category:Structures` | Large |
| Commands | `https://minecraft.wiki/w/Category:Commands` | ~322 |
| Enchantments | `https://minecraft.wiki/w/Category:Enchantments` | Large |
| Potions | `https://minecraft.wiki/w/Category:Potions` | Large |
| Status effects | `https://minecraft.wiki/w/Category:Status_effects` | Large |
| Data values | `https://minecraft.wiki/w/Category:Data_values` | Large |

### Special Index Categories
| Category | URL | Purpose |
|----------|-----|---------|
| Set index pages | `https://minecraft.wiki/w/Category:Set_index_pages` | 124 "list of" indexes |
| Data pages | `https://minecraft.wiki/w/Category:Data_pages` | Transcluded data tables |
| Disambiguation pages | `https://minecraft.wiki/w/Category:Disambiguation_pages` | Ambiguity resolution |
| Pages with unofficial names | `https://minecraft.wiki/w/Category:Pages_with_unofficial_names` | Pending official naming |
| All Categories | `https://minecraft.wiki/w/Special:Categories` | All 10,000+ categories |

### Translation Project Categories
| Category | URL | Purpose |
|----------|-----|---------|
| Projects | `https://minecraft.wiki/w/Minecraft_Wiki:Projects#Language_translations` | Wiki translation projects (11 languages) |
| Language | `https://minecraft.wiki/w/Language` | Crowdin translation info |

## Additional Resources

**Style Guides:**
- Minecraft Wiki Style Guide: `https://minecraft.wiki/w/Minecraft_Wiki:Style_guide`
- Community game terms: `https://minecraft.fandom.com/wiki/Tutorials/Game_terms`

**API Access:**
- MediaWiki API: `https://minecraft.wiki/api.php`
- Category members: `https://minecraft.wiki/api.php?action=query&list=categorymembers&cmtitle=Category:Blocks&format=json`
- Page content: `https://minecraft.wiki/api.php?action=query&prop=revisions&titles=Block&rvprop=content&format=json`
- XML sitemap: `https://minecraft.wiki/Sitemap.xml`


