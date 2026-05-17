---
description: "Start a video subtitle translation workflow — download subtitles from YouTube/Bilibili, mark TechMC terminology, translate, and output translated SRT."
argument-hint: [video URL or path to SRT file]
---

# /start-video-translate

## Overview

Execute this workflow when subtitles from YouTube or Bilibili videos need translation. Uses yt-dlp for subtitle download, TechMC terminology tools for glossary matching, and batch-translates subtitle cues while preserving timing.

## When to Use

- Translating YouTube or Bilibili video subtitles
- Converting existing SRT files with terminology-aware translation
- Preparing translated subtitles for Minecraft technical videos

## Inputs

- Video URL (YouTube or Bilibili) OR path to existing `.srt` file in `input/`
- Target language may be provided as argument; if missing, resolved per language detection rules

## Workflow

1. **Resolve input**: If URL provided, run `scripts/download_subs.py <URL>` to download subtitles. If local SRT path provided, copy to `output/` with metadata directory structure.

2. **Detect source language**: Extract from subtitle metadata (`metadata.json`) or filename pattern.

3. **Determine target language**: If source is non-English, default target is English. If source is English, ask user for target language before proceeding.

4. **Mark terminology**: Extract plain text via `scripts/parse_subs.py extract-text <source.srt>`, then run `scripts/mark_terms.py --match-format json` to identify glossary terms per cue.

5. **Resolve ambiguous terms**: Load `/querying-terminologies` skill for any unclear or ambiguous terminology matches.

6. **Chunk subtitles**: Run `scripts/parse_subs.py chunk --chunk-size 6 --overlap 1 <source.srt>` to create context-aware batches for translation.

7. **Translate chunks**: Translate each chunk preserving timing codes and cue structure. Inject terminology JSON as context into translation prompt to ensure consistent term usage.

8. **Reassemble output**: Run `scripts/parse_subs.py reassemble --input translated.json -o output/<video-id>/translated.<lang>.srt` to merge translated chunks.

9. **Write output files**: Create `translated.<lang>.srt`, `terms.md` (table format: Term | Translation | Cue # | Context), and `metadata.json`.

10. **QA verification**: Verify cue count matches source, timing preserved (no drift), no empty cues, no translated timing codes.

## Output Structure

```
output/<video-id>/
  source.<lang>.srt       # Original subtitles
  translated.<lang>.srt   # Translated subtitles
  terms.md                # Glossary terms found in subtitles
  metadata.json           # Video metadata from yt-dlp
```

## Common Options

```bash
# Download with Bilibili authentication
python3 scripts/download_subs.py <URL> --cookies cookies.txt

# Override subtitle language
python3 scripts/download_subs.py <URL> --lang en

# Adjust translation batch size
python3 scripts/parse_subs.py chunk --chunk-size 8 --overlap 1 <source.srt>

# Custom output location
python3 scripts/download_subs.py <URL> --output-dir custom/path
```

## Common Mistakes

- Do NOT translate timing codes (e.g., `00:01:23,456 --> 00:01:27,890`)
- Do NOT merge or split subtitle cues
- Do NOT modify `-->` arrow separators or `\n` within multi-line cues
- Do NOT skip terminology marking — always run `scripts/mark_terms.py` before translating
- Do NOT use ASR by default — require explicit user opt-in (see Optional: ASR section)
- Auto-generated subtitles (Bilibili/YouTube AI captions) may misrecognize technical terms (e.g., "书店" → "数字电路"). The translator may naturally correct these from context — this is expected. If a translation seems oddly different from the audio, this is likely why.

## Optional: ASR for Videos Without Subtitles

**When to use**: Video has no manual or auto-generated subtitles (`scripts/download_subs.py` exits with code 2)

**This is NOT the default path** — only for subtitle-less videos.

**Prerequisites**: `pip install -r requirements-asr.txt` (installs openai-whisper + PyTorch)

**How it works**: yt-dlp downloads audio only → whisperX transcribes → outputs SRT → continues normal pipeline

**Warning**: Large download (~2-5 GB for PyTorch), requires ~10 GB disk, ~10 GB RAM. GPU strongly recommended.

**Agent MUST ask user permission** before installing ASR dependencies or running ASR.

## Resources

- `/marking-terminologies` — Mark source text with TechMC glossary terms
- `/querying-terminologies` — Query TechMC glossary for term lookups
- `/querying-minecraft-wiki` — Verify official Minecraft translations
