#!/usr/bin/env python3
"""Query Minecraft Wiki for official term translations.

Usage:
    python scripts/query_minecraft_wiki.py --category blocks --language zh
    python scripts/query_minecraft_wiki.py --category items --language ja --format csv
    python scripts/query_minecraft_wiki.py --category entities --language de -o output.json
"""

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

API_ENDPOINT = "https://minecraft.wiki/api.php"
USER_AGENT = "gtmc-translation/0.1 (Minecraft translation workflow) Python urllib"

CATEGORY_MAP = {
    "blocks": "Category:Blocks",
    "items": "Category:Items",
    "entities": "Category:Entities",
}

LANGUAGE_WIKI_MAP = {
    "zh": "https://zh.minecraft.wiki/api.php",
}

LANGUAGE_VARIANT_MAP = {
    "zh": "zh-cn",
}


def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def cache_key(url: str, params: Dict[str, Any]) -> str:
    sorted_params = sorted(params.items())
    key_str = f"{url}?{urllib.parse.urlencode(sorted_params)}"
    return hashlib.sha1(key_str.encode()).hexdigest()


def read_cache(cache_path: Path, ttl: int) -> Optional[Dict[str, Any]]:
    if not cache_path.exists():
        return None
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cached = json.load(f)
        age = time.time() - cached.get("cached_at", 0)
        if age <= ttl:
            return cached.get("data")
    except (json.JSONDecodeError, KeyError, OSError):
        pass
    return None


def write_cache(cache_path: Path, data: Dict[str, Any]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cached = {"cached_at": time.time(), "data": data}
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cached, f)
    except OSError:
        pass


def api_request(
    params: Dict[str, Any],
    cache_dir: Optional[Path] = None,
    cache_ttl: int = 604800,
    no_cache: bool = False,
    timeout: int = 20,
    delay: float = 0.2,
    verbose: bool = False,
    api_endpoint: str = API_ENDPOINT
) -> Dict[str, Any]:
    params.setdefault("format", "json")
    params.setdefault("formatversion", "2")
    params.setdefault("maxlag", "5")
    
    if not no_cache and cache_dir:
        key = cache_key(api_endpoint, params)
        cache_path = cache_dir / f"{key}.json"
        cached_data = read_cache(cache_path, cache_ttl)
        if cached_data is not None:
            if verbose:
                print(f"Cache hit", file=sys.stderr)
            return cached_data
    
    if verbose:
        print(f"API: {params.get('action')}", file=sys.stderr)
    
    time.sleep(delay)
    url = f"{api_endpoint}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode('utf-8'))
        if "error" in data:
            raise RuntimeError(f"API error: {data['error'].get('info', 'Unknown')}")
        if not no_cache and cache_dir:
            write_cache(cache_path, data)
        return data
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}")


WILD_UPDATE_DATE = "2022-06-07"

def extract_nameid(wikitext: str) -> Optional[str]:
    match = re.search(r'\|\s*nameid\s*=\s*([^\n|}]+)', wikitext, re.IGNORECASE)
    if match:
        return match.group(1).strip().replace(r'\_', '_')
    return None


def extract_version_date(wikitext: str) -> Optional[str]:
    match = re.search(r'\{\{Version nav[^}]*\|date=([^|}]+)', wikitext, re.IGNORECASE)
    if match:
        date_str = match.group(1).strip()
        try:
            from datetime import datetime
            parsed = datetime.strptime(date_str, "%B %d, %Y")
            return parsed.strftime("%Y-%m-%d")
        except:
            pass
    return None
    match = re.search(r'\|\s*nameid\s*=\s*([a-z0-9_]+)', wikitext, re.IGNORECASE)
    return match.group(1).strip() if match else None


def get_category_members(category: str, limit: Optional[int], **kwargs) -> List[Dict[str, Any]]:
    members = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": CATEGORY_MAP[category],
        "cmnamespace": "0",
        "cmtype": "page",
        "cmprop": "ids|title",
        "cmlimit": "max",
    }
    
    while True:
        data = api_request(params, **kwargs)
        batch = data.get("query", {}).get("categorymembers", [])
        members.extend(batch)
        
        if limit and len(members) >= limit:
            members = members[:limit]
            break
        
        if "continue" not in data:
            break
        params.update(data["continue"])
    
    return members


def batched(items: List[Any], n: int) -> List[List[Any]]:
    for i in range(0, len(items), n):
        yield items[i:i + n]


def get_page_by_title(title: str, language: str, **kwargs) -> Optional[Dict[str, Any]]:
    params = {
        "action": "query",
        "titles": title,
        "prop": "revisions|langlinks",
        "rvprop": "content",
        "rvslots": "main",
        "lllang": language,
        "lllimit": "max",
    }
    
    data = api_request(params, **kwargs)
    pages = data.get("query", {}).get("pages", [])
    
    if pages:
        return pages[0]
    return None


def get_localized_name_via_variant(title: str, language: str, **kwargs) -> Optional[str]:
    """Get localized name by querying the language-specific wiki with variant."""
    if language not in LANGUAGE_WIKI_MAP:
        return None
    
    api_endpoint = LANGUAGE_WIKI_MAP[language]
    variant = LANGUAGE_VARIANT_MAP.get(language)
    
    params = {
        "action": "query",
        "titles": title,
        "prop": "info",
        "inprop": "varianttitles",
        "redirects": "1",
    }
    if variant:
        params["variant"] = variant
    
    data = api_request(params, api_endpoint=api_endpoint, **kwargs)
    pages = data.get("query", {}).get("pages", [])
    
    if pages:
        page = pages[0]
        if variant and "varianttitles" in page:
            return page["varianttitles"].get(variant, "")
        return page.get("title", "")
    
    return None


def get_page_details(pageids: List[int], language: str, **kwargs) -> Dict[int, Dict[str, Any]]:
    params = {
        "action": "query",
        "pageids": "|".join(str(pid) for pid in pageids),
        "prop": "revisions|langlinks",
        "rvprop": "content",
        "rvslots": "main",
        "lllang": language,
        "lllimit": "max",
    }
    
    data = api_request(params, **kwargs)
    pages = data.get("query", {}).get("pages", [])
    
    result = {}
    for page in pages:
        pageid = page.get("pageid")
        if pageid:
            result[pageid] = page
    
    return result


def build_records(category: str, language: str, members: List[Dict], page_details: Dict, include_missing: bool, verbose: bool, filter_latest: bool = False, cache_dir: Optional[Path] = None, cache_ttl: int = 604800, no_cache: bool = False, timeout: int = 20, delay: float = 0.2) -> List[Dict[str, str]]:
    records = []
    skipped_no_langlink = 0
    skipped_no_nameid = 0
    skipped_old_version = 0
    
    use_variant_api = language in LANGUAGE_WIKI_MAP
    
    kwargs = {
        "cache_dir": cache_dir,
        "cache_ttl": cache_ttl,
        "no_cache": no_cache,
        "timeout": timeout,
        "delay": delay,
        "verbose": verbose,
    }
    
    for member in members:
        pageid = member.get("pageid")
        english_title = member.get("title", "")
        page = page_details.get(pageid, {})
        
        nameid = ""
        revisions = page.get("revisions", [])
        wikitext = ""
        if revisions:
            wikitext = revisions[0].get("slots", {}).get("main", {}).get("content", "")
            nameid = extract_nameid(wikitext) or ""
        
        if filter_latest and wikitext:
            version_date = extract_version_date(wikitext)
            if version_date and version_date <= WILD_UPDATE_DATE:
                skipped_old_version += 1
                continue
        
        localized_name = ""
        if use_variant_api:
            localized_name = get_localized_name_via_variant(english_title, language, **kwargs) or ""
        else:
            langlinks = page.get("langlinks", [])
            if langlinks:
                localized_name = langlinks[0].get("title", "")
        
        if not include_missing:
            if not localized_name:
                skipped_no_langlink += 1
                continue
            if not nameid:
                skipped_no_nameid += 1
                continue
        
        records.append({
            "category": category,
            "english_title": english_title,
            "nameid": nameid,
            "language": language,
            "localized_name": localized_name,
        })
    
    if verbose:
        msg = f"Records: {len(records)}, Skipped (no langlink): {skipped_no_langlink}, Skipped (no nameid): {skipped_no_nameid}"
        if filter_latest:
            msg += f", Skipped (old version): {skipped_old_version}"
        print(msg, file=sys.stderr)
    
    return sorted(records, key=lambda r: r["english_title"])


def format_json(records: List[Dict[str, str]]) -> str:
    return json.dumps(records, ensure_ascii=False, indent=2)


def format_csv(records: List[Dict[str, str]]) -> str:
    if not records:
        return "category,english_title,nameid,language,localized_name\n"
    
    lines = ["category,english_title,nameid,language,localized_name"]
    for r in records:
        lines.append(f"{r['category']},{r['english_title']},{r['nameid']},{r['language']},{r['localized_name']}")
    return "\n".join(lines) + "\n"


def format_table(records: List[Dict[str, str]]) -> str:
    if not records:
        return "No records\n"
    
    lines = [f"{'English':<30} {'NameID':<25} {'Localized':<30}"]
    lines.append("-" * 85)
    for r in records:
        lines.append(f"{r['english_title']:<30} {r['nameid']:<25} {r['localized_name']:<30}")
    lines.append(f"\nTotal: {len(records)} records")
    return "\n".join(lines) + "\n"


def write_output(content: str, output_path: Optional[str]) -> None:
    if output_path:
        Path(output_path).write_text(content, encoding='utf-8')
    else:
        sys.stdout.write(content)


def main():
    parser = argparse.ArgumentParser(description="Query Minecraft Wiki for official term translations")
    parser.add_argument("--category", choices=["blocks", "items", "entities"], help="Category to query")
    parser.add_argument("--term", help="Query a single term by English title")
    parser.add_argument("--language", required=True, help="Target language code (e.g., zh, ja, de)")
    parser.add_argument("--format", choices=["json", "csv", "table"], default="json", help="Output format")
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    parser.add_argument("--cache-dir", help="Cache directory path")
    parser.add_argument("--cache-ttl", type=int, default=604800, help="Cache TTL in seconds (default: 7 days)")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument("--include-missing", action="store_true", help="Include records with missing data")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay between requests in seconds")
    parser.add_argument("--timeout", type=int, default=20, help="Request timeout in seconds")
    parser.add_argument("--limit", type=int, help="Limit number of pages (for testing)")
    parser.add_argument("--latest-changes", action="store_true", help="Filter items by version (experimental, requires {{Version nav}} in page)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output to stderr")
    
    args = parser.parse_args()
    
    if not args.category and not args.term:
        parser.error("Either --category or --term is required")
    if args.category and args.term:
        parser.error("Cannot use both --category and --term")
    
    cache_dir = Path(args.cache_dir) if args.cache_dir else get_repo_root() / ".cache" / "minecraft-wiki"
    
    kwargs = {
        "cache_dir": cache_dir,
        "cache_ttl": args.cache_ttl,
        "no_cache": args.no_cache,
        "timeout": args.timeout,
        "delay": args.delay,
        "verbose": args.verbose,
    }
    
    try:
        if args.term:
            if args.verbose:
                print(f"Querying term '{args.term}' for language {args.language}", file=sys.stderr)
            
            page = get_page_by_title(args.term, args.language, **kwargs)
            if not page:
                print(f"Error: Page '{args.term}' not found", file=sys.stderr)
                sys.exit(1)
            
            members = [{"pageid": page.get("pageid"), "title": page.get("title", args.term)}]
            all_details = {page.get("pageid"): page}
            category = "term"
        else:
            if args.verbose:
                print(f"Querying {args.category} for language {args.language}", file=sys.stderr)
            
            members = get_category_members(args.category, args.limit, **kwargs)
            if args.verbose:
                print(f"Found {len(members)} pages", file=sys.stderr)
            
            all_details = {}
            for batch in batched(members, 50):
                pageids = [m["pageid"] for m in batch]
                details = get_page_details(pageids, args.language, **kwargs)
                all_details.update(details)
            
            category = args.category
        
        records = build_records(
            category, args.language, members, all_details, 
            args.include_missing, args.verbose, args.latest_changes,
            cache_dir, args.cache_ttl, args.no_cache, args.timeout, args.delay
        )
        
        if args.format == "json":
            output = format_json(records)
        elif args.format == "csv":
            output = format_csv(records)
        else:
            output = format_table(records)
        
        write_output(output, args.output)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
