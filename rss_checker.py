#!/usr/bin/env python3
"""yes24 RSS 피드를 파싱하여 새 도서를 탐지하는 스크립트."""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import feedparser


def parse_rss_urls_from_markdown(content: str) -> list[tuple[str, str]]:
    """yes24_rss.md에서 (카테고리명, URL) 쌍을 추출."""
    pattern = r"- (.+?):\s+(https?://\S+)"
    return re.findall(pattern, content)


def load_processed_books(path: Path) -> dict:
    """processed_books.json 로드. 파일 없으면 빈 구조 반환."""
    if not path.exists():
        return {"last_checked": None, "processed": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_processed_books(path: Path, data: dict) -> None:
    """processed_books.json 저장."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def filter_new_books(feed_entries: list[dict], processed: dict) -> list[dict]:
    """이미 처리된 책을 제외한 새 책 목록 반환."""
    processed_ids = {item["id"] for item in processed["processed"]}
    return [entry for entry in feed_entries if entry["id"] not in processed_ids]


def fetch_rss_entries(url: str) -> list[dict]:
    """RSS 피드를 파싱하여 도서 엔트리 목록 반환."""
    feed = feedparser.parse(url)
    entries = []
    for entry in feed.entries:
        link = entry.get("link", "")
        parsed = parse_qs(urlparse(link).query)
        book_id = parsed.get("goodsNo", [link.rstrip("/").split("/")[-1]])[0]
        entries.append({
            "id": book_id,
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "category": entry.get("category", ""),
        })
    return entries


SCRIPT_DIR = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="yes24 RSS 피드에서 새 도서 탐지")
    parser.add_argument(
        "--rss-file",
        default=None,
        help="RSS URL 목록 파일 경로 (default: 스크립트 경로/yes24_rss.md)",
    )
    parser.add_argument(
        "--state-file",
        default=None,
        help="처리 상태 파일 경로 (default: 스크립트 경로/processed_books.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="목록만 출력하고 요약은 실행하지 않음",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="처리할 최대 도서 수 (0=무제한)",
    )
    args = parser.parse_args()

    rss_path = Path(args.rss_file) if args.rss_file else SCRIPT_DIR / "yes24_rss.md"
    state_path = Path(args.state_file) if args.state_file else SCRIPT_DIR / "processed_books.json"

    if not rss_path.exists():
        print(f"Error: RSS 파일을 찾을 수 없음: {rss_path}", file=sys.stderr)
        sys.exit(1)

    rss_content = rss_path.read_text(encoding="utf-8")
    rss_urls = parse_rss_urls_from_markdown(rss_content)
    processed = load_processed_books(state_path)

    all_new_books = []

    for category, url in rss_urls:
        print(f"[{category}] RSS 피드 확인 중: {url}")
        entries = fetch_rss_entries(url)
        new_books = filter_new_books(entries, processed)
        if new_books:
            print(f"  → 새 도서 {len(new_books)}권 발견")
            for book in new_books:
                book["rss_category"] = category
            all_new_books.extend(new_books)

    if not all_new_books:
        print("\n새 도서가 없습니다.")
        processed["last_checked"] = datetime.now(timezone.utc).isoformat()
        save_processed_books(state_path, processed)
        return

    if args.limit > 0:
        all_new_books = all_new_books[: args.limit]

    print(f"\n총 {len(all_new_books)}권의 새 도서:")
    for book in all_new_books:
        print(f"  [{book['rss_category']}] {book['title']}")
        print(f"    {book['link']}")

    if not args.dry_run:
        for book in all_new_books:
            print(f"\n요약 중: {book['title']}...")
            prompt = f"/summarize-book {book['link']}"
            cmd = [
                "claude", "-p", prompt,
                "--allowedTools", "Bash,Read,Write,WebFetch",
                "--permission-mode", "bypassPermissions",
            ]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                if result.returncode != 0:
                    print(f"  Error: {result.stderr[:200]}", file=sys.stderr)
                else:
                    processed["processed"].append({
                        "id": book["id"],
                        "title": book["title"],
                        "url": book["link"],
                        "category": book["rss_category"],
                        "processed_at": datetime.now(timezone.utc).isoformat(),
                    })
            except subprocess.TimeoutExpired:
                print(f"  Error: 타임아웃 (180초)", file=sys.stderr)
    else:
        print("\n(dry-run: 목록만 출력, 요약 미실행)")
        return

    processed["last_checked"] = datetime.now(timezone.utc).isoformat()
    save_processed_books(state_path, processed)
    print("\n상태 파일 업데이트 완료.")


if __name__ == "__main__":
    main()
