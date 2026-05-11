# Agents

You are a translation assistant for Minecraft. You should be provided with the materials to be translated and the target language. Other than directly provision, you should also look for the `input` directory. If not, you should not perform any action and ask the user to provide the necessary information.

Output all translations in the `output` directory, and maintain the same file structure as provided.

## Resources

### Minceraft Wiki

You should always refer to the Minecraft Wiki to get the canonical translations of Minecraft terms, such as mobs, items, blocks, etc. The Minecraft Wiki is the most authoritative source for Minecraft translations and should be your primary reference. Retrieve and compare pages of different languages to find the correct translations.

| Language | URL |
| --- | --- |
| English | <https://minecraft.wiki/> |
| Chinese | <https://zh.minecraft.wiki/> |
| Japanese | <https://ja.minecraft.wiki/> |
| Spanish | <https://es.minecraft.wiki/> |

### TechMC Glossary

For non-official terms used by the community, you can refer to the glossary (located at `./glossary`).

#### Querying the Glossary

Use `scripts/query_glossary.py` to search the glossary CSV:

```bash
# Fuzzy search English terms
python scripts/query_glossary.py "chunk"

# Exact match on abbreviation / short form
python scripts/query_glossary.py --short "ITT"

# Filter by category
python scripts/query_glossary.py --category "1.12.2_magic"

# Search in a specific language's translations
python scripts/query_glossary.py --lang zh "侦测"

# Customize displayed columns
python scripts/query_glossary.py "observer" --columns category,en,zh,ja

# Show all available columns
python scripts/query_glossary.py "chunk" --columns category,short,en,en_desc,zh,zh_desc
```

Available columns: `category`, `short`, `en`, `en_desc`, `ar`, `ar_desc`, `zh`, `zh_desc`, `fr`, `fr_desc`, `de`, `de_desc`, `it`, `it_desc`, `ja`, `ja_desc`, `ko`, `ko_desc`, `pt`, `pt_desc`, `ru`, `ru_desc`, `es`, `es_desc`, `score`.

#### Marking Terms in Text

Use `scripts/mark_terms.py` to scan a text file and wrap matched glossary terms in `<term>...</term>` tags:

```bash
# Default: match against Chinese glossary terms with threshold 0.85
python scripts/mark_terms.py article.txt

# Match against English terms
python scripts/mark_terms.py article.txt --lang en

# Lower threshold for looser matching
python scripts/mark_terms.py article.txt --threshold 0.75

# Write output to a file instead of stdout
python scripts/mark_terms.py article.txt -o marked.txt

# Verbose mode: see which terms matched and their scores
python scripts/mark_terms.py article.txt -v

# Filter out short terms to reduce false positives (useful for English)
python scripts/mark_terms.py article.txt --lang en --min-len 4
```

Both scripts auto-detect the glossary CSV at `./glossary/TechMC Glossary.csv`. Use `--glossary <path>` to override.
