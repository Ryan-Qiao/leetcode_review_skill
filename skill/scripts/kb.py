#!/usr/bin/env python3
"""Local LeetCode review knowledge base.

Stores one JSON document per problem under ~/.leetcode-review/submissions by
default. The tool intentionally does not fetch network data; Codex/browser
automation supplies retrieved submission data and this script handles durable
local storage and lookup.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(os.environ.get("LEETCODE_REVIEW_HOME", "~/.leetcode-review")).expanduser()


def normalize_slug(value: str) -> str:
    value = value.strip()
    match = re.search(r"/problems/([^/?#]+)/?", value)
    if match:
        return match.group(1)
    value = value.lower()
    value = re.sub(r"^\s*\d+\.\s*", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", "", value.strip().lower())


def normalize_code(value: str) -> str:
    text = value.replace("\u00a0", " ")
    lines = []
    for line in text.splitlines():
        if re.fullmatch(r"\s*\d+\s*", line):
            continue
        line = re.sub(r"^\s*\d+(?=\s*\S)", "", line)
        lines.append(line.rstrip())
    return "\n".join(lines).strip()


def submissions_dir(root: Path) -> Path:
    return root / "submissions"


def status_dir(root: Path) -> Path:
    return root / "statuses"


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else None
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    tmp.replace(path)


def read_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.file:
        with Path(args.file).expanduser().open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    else:
        payload = json.load(sys.stdin)
    if not isinstance(payload, dict):
        raise SystemExit("payload must be a JSON object")
    return payload


def command_upsert(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser()
    payload = read_payload(args)
    slug = payload.get("slug") or payload.get("titleSlug") or payload.get("problemSlug") or payload.get("url")
    if not isinstance(slug, str) or not slug.strip():
        raise SystemExit("payload requires slug, titleSlug, problemSlug, or url")
    slug = normalize_slug(slug)

    now = int(time.time())
    record = {
        "schemaVersion": 1,
        "slug": slug,
        "frontendId": payload.get("frontendId") or payload.get("questionFrontendId"),
        "title": payload.get("title"),
        "titleCn": payload.get("titleCn") or payload.get("title"),
        "aliases": sorted(set(filter(None, payload.get("aliases", [])))),
        "source": payload.get("source", "user_submission"),
        "sourceUrl": payload.get("sourceUrl"),
        "submissionId": str(payload.get("submissionId")) if payload.get("submissionId") is not None else None,
        "status": payload.get("status", "通过"),
        "language": payload.get("language") or payload.get("lang"),
        "runtime": payload.get("runtime"),
        "memory": payload.get("memory"),
        "submittedAt": payload.get("submittedAt"),
        "retrievedAt": payload.get("retrievedAt", now),
        "code": normalize_code(payload.get("code")) if isinstance(payload.get("code"), str) else payload.get("code"),
        "notes": payload.get("notes"),
    }

    if not isinstance(record["code"], str) or not record["code"].strip():
        raise SystemExit("payload requires non-empty code")

    aliases = set(record["aliases"])
    for key in ("slug", "title", "titleCn", "frontendId"):
        value = record.get(key)
        if value:
            aliases.add(str(value))
    record["aliases"] = sorted(aliases)

    path = submissions_dir(root) / f"{slug}.json"
    write_json(path, record)
    print(json.dumps({"status": "upserted", "slug": slug, "path": str(path)}, ensure_ascii=False))
    return 0


def iter_records(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    directory = submissions_dir(root)
    if not directory.exists():
        return []
    records: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(directory.glob("*.json")):
        data = load_json(path)
        if data:
            records.append((path, data))
    return records


def command_lookup(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser()
    query = args.query.strip()
    slug = normalize_slug(query)

    direct = load_json(submissions_dir(root) / f"{slug}.json")
    if direct:
        print(json.dumps({"status": "found", "match": "slug", "record": direct}, ensure_ascii=False, indent=2))
        return 0

    normalized_query = normalize_text(query)
    best_contains: tuple[int, dict[str, Any]] | None = None
    for _, record in iter_records(root):
        aliases = [str(item) for item in record.get("aliases", []) if item is not None]
        aliases.extend(str(record.get(key, "")) for key in ("slug", "title", "titleCn", "frontendId"))
        if any(normalize_text(alias) == normalized_query for alias in aliases if alias):
            print(json.dumps({"status": "found", "match": "alias", "record": record}, ensure_ascii=False, indent=2))
            return 0
        for alias in aliases:
            normalized_alias = normalize_text(alias)
            if len(normalized_alias) >= 4 and normalized_alias in normalized_query:
                score = len(normalized_alias)
                if best_contains is None or score > best_contains[0]:
                    best_contains = (score, record)

    if best_contains:
        print(json.dumps({"status": "found", "match": "contains_alias", "record": best_contains[1]}, ensure_ascii=False, indent=2))
        return 0

    print(json.dumps({"status": "not_found", "query": query, "normalizedSlug": slug}, ensure_ascii=False, indent=2))
    return 1


def command_list(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser()
    items = []
    for path, record in iter_records(root):
        items.append({
            "slug": record.get("slug") or path.stem,
            "frontendId": record.get("frontendId"),
            "title": record.get("titleCn") or record.get("title"),
            "language": record.get("language"),
            "submittedAt": record.get("submittedAt"),
            "path": str(path),
        })
    print(json.dumps({"status": "ok", "count": len(items), "items": items}, ensure_ascii=False, indent=2))
    return 0


def command_normalize(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser()
    changed = []
    for path, record in iter_records(root):
        code = record.get("code")
        if not isinstance(code, str):
            continue
        normalized = normalize_code(code)
        if normalized != code:
            record["code"] = normalized
            write_json(path, record)
            changed.append(str(path))
    print(json.dumps({"status": "ok", "changed": len(changed), "paths": changed}, ensure_ascii=False, indent=2))
    return 0


def command_mark_status(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser()
    slug = normalize_slug(args.slug)
    record = {
        "schemaVersion": 1,
        "slug": slug,
        "status": args.status,
        "reason": args.reason,
        "detailUrl": args.detail_url,
        "updatedAt": int(time.time()),
    }
    path = status_dir(root) / f"{slug}.json"
    write_json(path, record)
    print(json.dumps({"status": "marked", "slug": slug, "path": str(path)}, ensure_ascii=False))
    return 0


def load_statuses(root: Path) -> dict[str, dict[str, Any]]:
    directory = status_dir(root)
    if not directory.exists():
        return {}
    statuses: dict[str, dict[str, Any]] = {}
    for path in directory.glob("*.json"):
        data = load_json(path)
        if data and data.get("slug"):
            statuses[str(data["slug"])] = data
    return statuses


def command_coverage(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser()
    manifest_path = Path(args.manifest).expanduser() if args.manifest else root / "hot100.json"
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if not isinstance(manifest, list):
        raise SystemExit("manifest must be a JSON array")

    cached = {path.stem for path, _ in iter_records(root)}
    statuses = load_statuses(root)
    items = []
    for item in manifest:
        if not isinstance(item, dict):
            continue
        slug = item.get("slug")
        if not slug:
            continue
        items.append({
            "slug": slug,
            "frontendId": item.get("frontendId"),
            "title": item.get("titleCn") or item.get("title"),
            "cached": slug in cached,
            "path": str(submissions_dir(root) / f"{slug}.json") if slug in cached else None,
            "lastStatus": statuses.get(slug, {}).get("status"),
            "reason": statuses.get(slug, {}).get("reason"),
            "detailUrl": statuses.get(slug, {}).get("detailUrl"),
        })

    result = {
        "status": "ok",
        "total": len(items),
        "cached": sum(1 for item in items if item["cached"]),
        "missing": sum(1 for item in items if not item["cached"]),
        "items": items,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def command_path(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser()
    print(str(submissions_dir(root)))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage local LeetCode review KB")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="KB root directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    upsert = subparsers.add_parser("upsert", help="Insert or replace one submission record from JSON")
    upsert.add_argument("--file", help="Read payload from a JSON file instead of stdin")
    upsert.set_defaults(func=command_upsert)

    lookup = subparsers.add_parser("lookup", help="Find a submission by URL, slug, title, or frontend id")
    lookup.add_argument("query")
    lookup.set_defaults(func=command_lookup)

    list_cmd = subparsers.add_parser("list", help="List cached submissions")
    list_cmd.set_defaults(func=command_list)

    normalize = subparsers.add_parser("normalize", help="Normalize cached code blocks")
    normalize.set_defaults(func=command_normalize)

    mark_status = subparsers.add_parser("mark-status", help="Persist warmup status for a problem")
    mark_status.add_argument("slug")
    mark_status.add_argument("status")
    mark_status.add_argument("--reason")
    mark_status.add_argument("--detail-url")
    mark_status.set_defaults(func=command_mark_status)

    coverage = subparsers.add_parser("coverage", help="Report coverage for a manifest such as hot100.json")
    coverage.add_argument("--manifest", help="Problem manifest JSON array. Defaults to <root>/hot100.json")
    coverage.set_defaults(func=command_coverage)

    path_cmd = subparsers.add_parser("path", help="Print the submissions directory")
    path_cmd.set_defaults(func=command_path)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
