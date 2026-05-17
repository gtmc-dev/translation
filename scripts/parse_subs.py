#!/usr/bin/env python3
"""
SRT subtitle parser and manipulation tool.

Provides commands for parsing, chunking, text extraction, and reassembly of SRT files.
"""

import argparse
import json
import sys
from datetime import timedelta
from pathlib import Path

import srt


def read_file(path, encodings=('utf-8-sig', 'latin-1')):
    """Read file with fallback encodings."""
    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode {path} with any supported encoding")


def preprocess_vtt(content):
    """Convert WebVTT to SRT format if needed."""
    if content.startswith('WEBVTT'):
        lines = content.split('\n')
        # Remove WEBVTT header and metadata
        start_idx = 0
        for i, line in enumerate(lines):
            if '-->' in line:
                start_idx = i - 1 if i > 0 and lines[i-1].strip().isdigit() else i
                break
        content = '\n'.join(lines[start_idx:])
        # Convert timestamp format: . to ,
        content = content.replace('.', ',')
    return content


def timedelta_to_srt(td):
    """Convert timedelta to SRT timestamp format."""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def parse_srt_file(file_path):
    """Parse SRT file and return list of subtitle objects."""
    content = read_file(file_path)
    content = preprocess_vtt(content)
    
    try:
        subs = list(srt.parse(content))
    except srt.SRTParseError as e:
        print(f"Error parsing SRT file: {e}", file=sys.stderr)
        sys.exit(1)
    
    return subs


def cmd_parse(args):
    """Parse SRT file and output JSON."""
    subs = parse_srt_file(args.file)
    
    result = [
        {
            'index': sub.index,
            'start': timedelta_to_srt(sub.start),
            'end': timedelta_to_srt(sub.end),
            'content': sub.content
        }
        for sub in subs
    ]
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_chunk(args):
    """Chunk SRT file for batch translation."""
    subs = parse_srt_file(args.file)
    
    chunks = []
    i = 0
    while i < len(subs):
        chunk_end = min(i + args.chunk_size, len(subs))
        chunk = [
            {
                'index': sub.index,
                'start': timedelta_to_srt(sub.start),
                'end': timedelta_to_srt(sub.end),
                'content': sub.content
            }
            for sub in subs[i:chunk_end]
        ]
        chunks.append(chunk)
        # Move forward by chunk_size - overlap
        i += args.chunk_size - args.overlap
    
    print(json.dumps(chunks, ensure_ascii=False, indent=2))


def cmd_extract_text(args):
    """Extract text content with cue indices."""
    subs = parse_srt_file(args.file)
    
    for sub in subs:
        print(f"[{sub.index}] {sub.content}")


def cmd_reassemble(args):
    """Reassemble SRT from translated JSON."""
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Flatten if chunked
    if data and isinstance(data[0], list):
        flat = []
        seen = set()
        for chunk in data:
            for item in chunk:
                if item['index'] not in seen:
                    flat.append(item)
                    seen.add(item['index'])
        data = flat
    
    # Parse timestamps and create Subtitle objects
    def parse_timestamp(ts):
        if isinstance(ts, str):
            parts = ts.replace(',', ':').split(':')
            h, m, s, ms = map(int, parts)
            return timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms)
        return ts
    
    subs = []
    for item in data:
        content = item.get('translated_content', item.get('content', ''))
        sub = srt.Subtitle(
            index=item['index'],
            start=parse_timestamp(item['start']),
            end=parse_timestamp(item['end']),
            content=content
        )
        subs.append(sub)
    
    output = srt.compose(subs, reindex=True)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
    else:
        print(output)


def main():
    parser = argparse.ArgumentParser(description='SRT subtitle parser and manipulation tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse SRT file to JSON')
    parse_parser.add_argument('file', help='Input SRT file')
    parse_parser.add_argument('--output-format', choices=['json', 'text'], default='json', help='Output format')
    parse_parser.set_defaults(func=cmd_parse)
    
    # Chunk command
    chunk_parser = subparsers.add_parser('chunk', help='Chunk SRT for batch translation')
    chunk_parser.add_argument('file', help='Input SRT file')
    chunk_parser.add_argument('--chunk-size', type=int, default=6, help='Number of cues per chunk')
    chunk_parser.add_argument('--overlap', type=int, default=1, help='Number of overlapping cues between chunks')
    chunk_parser.set_defaults(func=cmd_chunk)
    
    # Extract text command
    extract_parser = subparsers.add_parser('extract-text', help='Extract text content with indices')
    extract_parser.add_argument('file', help='Input SRT file')
    extract_parser.set_defaults(func=cmd_extract_text)
    
    # Reassemble command
    reassemble_parser = subparsers.add_parser('reassemble', help='Reassemble SRT from translated JSON')
    reassemble_parser.add_argument('--input', required=True, help='Input JSON file')
    reassemble_parser.add_argument('-o', '--output', help='Output SRT file (default: stdout)')
    reassemble_parser.set_defaults(func=cmd_reassemble)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
