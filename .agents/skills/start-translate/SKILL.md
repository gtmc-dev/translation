---
description: Start a Minecraft translation workflow, resolve source/target inputs, prepare terminology references, translate into output/, and run QA.
argument-hint: [source path or target language]
---

# /start-translate

Execute this workflow when `/start-translate` is invoked. Treat it as the main translation command for this repository.

## Inputs

- Source material may be provided directly, passed as an argument, or placed under `input/`.
- Target language must be known before translation begins.
- If either source material or target language is missing after checking direct input and `input/`, ask one precise question and stop.

## Workflow

1. Confirm both source material and target language. If material was not provided directly, inspect `input/`. If source material or target language is still missing, ask one precise question and stop.
2. Preserve file structure exactly: write translated files under `output/` with the same relative paths as the source material.
3. Before translating long prose, prepare terminology references. Use `marking-terminologies` to mark source text with TechMC glossary terms. Use `querying-terminologies` for standalone glossary lookups.
4. Use Minecraft Wiki language pages for official Minecraft names, including mobs, items, blocks, effects, advancements, and other canonical game terms.
5. Use TechMC terminology resources for community/non-official technical terminology, redstone/mechanics terms, abbreviations, and short forms.
6. Translate content while preserving Markdown structure, code spans, URLs, placeholders, formatting tags, translation keys, file metadata, and other technical syntax.
7. Run a QA pass before final delivery: check official names, community terms, placeholders, tags, punctuation/spacing, and whether output structure mirrors the input.

## Resources

External localization references support this structure: professional workflows use explicit source/target confirmation, glossary or style-guide preparation, translation memory or reference notes, structure-preserving export, and QA gates. Agent workflow references support keeping `AGENTS.md` as identity and routing only, with detailed task workflows in focused skills loaded on demand.

### Minecraft Wiki

Use the Minecraft Wiki as the authoritative source for official Minecraft translations. Compare the relevant language pages when verifying canonical terms.

| Language | URL |
| --- | --- |
| English | <https://minecraft.wiki/> |
| Chinese | <https://zh.minecraft.wiki/> |
| Japanese | <https://ja.minecraft.wiki/> |
| Spanish | <https://es.minecraft.wiki/> |

Also consult these Minecraft-specific references when relevant:

- Minecraft Wiki Style Guide: <https://minecraft.wiki/w/Minecraft_Wiki:Style_guide>
- Minecraft Wiki Language page: <https://minecraft.wiki/w/Language>
- Minecraft community game terms: <https://minecraft.fandom.com/wiki/Tutorials/Game_terms>

### Terminology Support

- Use `marking-terminologies` only for producing marked source/reference files with `scripts/mark_terms.py`.
- Use `querying-terminologies` only for direct TechMC glossary lookups with `scripts/query_glossary.py`.

Keep these categories distinct while translating:

- Official Minecraft names: verify against Minecraft Wiki language pages or Mojang resources.
- Community terminology: verify with TechMC terminology tools.
- Do-not-translate or partially translated names: follow Mojang official glossary guidance when applicable.
- Technical tokens: preserve translation keys, placeholders, color codes, commands, paths, URLs, and code exactly unless the source explicitly asks otherwise.

## QA Checklist

- Source material and target language were identified before translation.
- Every translated file is under `output/` and mirrors the input relative path.
- Official Minecraft names were checked against Minecraft Wiki or Mojang references.
- Community and technical terms were checked with terminology references when they affected translation choices.
- Placeholders such as `%s`, `%1$s`, `%1`, `{name}`, Markdown links, HTML/XML tags, color codes, commands, paths, URLs, code spans, and translation keys remain intact.
- Marked-term output and useful query results were kept as reference notes when they informed the translation.

## Common Mistakes

- Do not start translating before identifying both source material and target language.
- Do not flatten or reorganize files in `output/`; preserve the source structure.
- Do not confuse community terminology with official Minecraft names.
- Do not translate technical syntax such as translation keys, placeholders, commands, URLs, code spans, or formatting tags.
- Do not put terminology-tool instructions here; keep detailed `mark_terms.py` usage in `marking-terminologies` and detailed `query_glossary.py` usage in `querying-terminologies`.

## Final Response

Report the output paths created, the target language, terminology references used, verification performed, and any source/term ambiguities that remain unresolved.
