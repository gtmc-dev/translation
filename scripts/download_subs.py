#!/usr/bin/env python3
"""
Download subtitles from YouTube or Bilibili videos using yt-dlp.

Extracts video metadata and downloads subtitles in SRT or VTT format.
Supports manual and auto-generated subtitles with fallback logic.

Usage:
    python scripts/download_subs.py "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    python scripts/download_subs.py "https://www.youtube.com/watch?v=jNQXAC9IVRw" --lang en
    python scripts/download_subs.py "URL" --output-dir /tmp/subs --format vtt
    python scripts/download_subs.py "URL" --cookies cookies.txt --verbose
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse

try:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError, ExtractorError
except ImportError:
    print("Error: yt-dlp not installed. Run: pip install yt-dlp", file=sys.stderr)
    sys.exit(1)

try:
    import srt
except ImportError:
    print("Error: srt not installed. Run: pip install srt", file=sys.stderr)
    sys.exit(1)


def detect_platform(url: str) -> str:
    """Detect video platform from URL."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    if "youtube.com" in domain or "youtu.be" in domain:
        return "youtube"
    elif "bilibili.com" in domain or "b23.tv" in domain:
        return "bilibili"
    else:
        return "unknown"


def extract_video_info(url: str, cookies_path: str = None, verbose: bool = False):
    """Extract video metadata without downloading."""
    ydl_opts = {
        "quiet": not verbose,
        "no_warnings": not verbose,
    }
    
    if cookies_path:
        ydl_opts["cookiefile"] = cookies_path
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except ExtractorError as e:
        platform = detect_platform(url)
        if platform == "bilibili" and "login" in str(e).lower():
            print(f"Error: Bilibili authentication required. Use --cookies flag with cookies.txt", file=sys.stderr)
        else:
            print(f"Error: Failed to extract video info: {e}", file=sys.stderr)
        sys.exit(1)
    except DownloadError as e:
        print(f"Error: Download failed: {e}", file=sys.stderr)
        sys.exit(1)


def get_available_subtitles(info: dict) -> dict:
    """Get available subtitle languages from video info."""
    subtitles = info.get("subtitles", {})
    auto_subs = info.get("automatic_captions", {})
    
    # Prefer manual subtitles, include auto as fallback
    all_subs = {}
    for lang in set(list(subtitles.keys()) + list(auto_subs.keys())):
        all_subs[lang] = {
            "manual": lang in subtitles,
            "auto": lang in auto_subs
        }
    
    return all_subs


def convert_vtt_to_srt(vtt_path: Path) -> Path:
    """Convert VTT file to SRT format."""
    with open(vtt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    srt_lines = []
    skip_header = True
    for line in lines:
        if skip_header:
            if "-->" in line:
                skip_header = False
                srt_lines.append(line.replace(".", ","))
            continue
        srt_lines.append(line.replace(".", ",") if "-->" in line else line)
    
    srt_path = vtt_path.with_suffix(".srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        f.writelines(srt_lines)
    
    vtt_path.unlink()
    return srt_path


def download_subtitles(url: str, output_dir: Path, lang: str = None, 
                       subtitle_format: str = "srt", cookies_path: str = None,
                       verbose: bool = False):
    """Download subtitles using yt-dlp."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "outtmpl": str(output_dir / "source.%(ext)s"),
        "quiet": not verbose,
        "no_warnings": not verbose,
    }
    
    if lang:
        ydl_opts["subtitleslangs"] = [lang]
    else:
        ydl_opts["allsubtitles"] = True
    
    if cookies_path:
        ydl_opts["cookiefile"] = cookies_path
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except (ExtractorError, DownloadError) as e:
        print(f"Error: Subtitle download failed: {e}", file=sys.stderr)
        sys.exit(1)
    
    if subtitle_format == "srt":
        for vtt_file in output_dir.glob("*.vtt"):
            convert_vtt_to_srt(vtt_file)


def write_metadata(output_dir: Path, info: dict, available_subs: dict):
    """Write metadata.json to output directory."""
    metadata = {
        "video_id": info.get("id"),
        "title": info.get("title"),
        "source_language": info.get("language"),
        "platform": detect_platform(info.get("webpage_url", "")),
        "available_languages": list(available_subs.keys()),
        "downloaded_at": datetime.now(timezone.utc).isoformat()
    }
    
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    if len(available_subs) > 0:
        print(f"Downloaded subtitles to: {output_dir}", file=sys.stderr)
    else:
        print(f"Metadata written to: {metadata_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Download subtitles from YouTube or Bilibili videos"
    )
    parser.add_argument(
        "url",
        type=str,
        help="Video URL (YouTube or Bilibili)"
    )
    parser.add_argument(
        "--lang",
        type=str,
        default=None,
        help="Subtitle language code (e.g., en, zh). If not specified, downloads all available."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: output/<video-id>/)"
    )
    parser.add_argument(
        "--cookies",
        type=str,
        default=None,
        help="Path to cookies.txt file for authentication (required for some Bilibili videos)"
    )
    parser.add_argument(
        "--format",
        type=str,
        default="srt",
        choices=["srt", "vtt"],
        help="Subtitle format (default: srt)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate URL
    platform = detect_platform(args.url)
    if platform == "unknown":
        print("Error: Unsupported URL. Only YouTube and Bilibili are supported.", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"Platform detected: {platform}", file=sys.stderr)
    
    # Extract video info
    info = extract_video_info(args.url, args.cookies, args.verbose)
    video_id = info.get("id")
    
    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path("output") / video_id
    
    # Check available subtitles
    available_subs = get_available_subtitles(info)
    
    if not available_subs:
        print("Error: No subtitles available for this video.", file=sys.stderr)
        print("Suggestion: Try a different video or check if subtitles exist on the platform.", file=sys.stderr)
        sys.exit(2)
    
    if args.verbose:
        print(f"Available subtitles: {', '.join(available_subs.keys())}", file=sys.stderr)
    
    # Check if requested language is available
    if args.lang and args.lang not in available_subs:
        print(f"Error: Language '{args.lang}' not available.", file=sys.stderr)
        print(f"Available languages: {', '.join(available_subs.keys())}", file=sys.stderr)
        sys.exit(2)
    
    # Download subtitles
    download_subtitles(args.url, output_dir, args.lang, args.format, args.cookies, args.verbose)
    
    # Write metadata
    write_metadata(output_dir, info, available_subs)
    
    print(f"Success: Subtitles downloaded to {output_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
