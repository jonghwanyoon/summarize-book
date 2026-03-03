import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from rss_checker import (
    parse_rss_urls_from_markdown,
    load_processed_books,
    save_processed_books,
    filter_new_books,
    fetch_rss_entries,
)


def test_parse_rss_urls_from_markdown():
    md_content = """- 건강/취미/실용: https://www.yes24.com/_par_/Rss/KNU001001011.xml
- 컴퓨터: https://www.yes24.com/_par_/Rss/FNU002001008.xml"""
    result = parse_rss_urls_from_markdown(md_content)
    assert len(result) == 2
    assert result[0] == ("건강/취미/실용", "https://www.yes24.com/_par_/Rss/KNU001001011.xml")
    assert result[1] == ("컴퓨터", "https://www.yes24.com/_par_/Rss/FNU002001008.xml")


def test_load_processed_books_empty():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"last_checked": None, "processed": []}, f)
        path = f.name
    result = load_processed_books(Path(path))
    assert result["processed"] == []


def test_load_processed_books_missing_file():
    result = load_processed_books(Path("/nonexistent/path.json"))
    assert result["processed"] == []


def test_filter_new_books():
    feed_entries = [
        {"id": "111", "title": "Book A", "link": "https://yes24.com/111"},
        {"id": "222", "title": "Book B", "link": "https://yes24.com/222"},
        {"id": "333", "title": "Book C", "link": "https://yes24.com/333"},
    ]
    processed = {"processed": [{"id": "222"}]}
    new_books = filter_new_books(feed_entries, processed)
    assert len(new_books) == 2
    assert new_books[0]["id"] == "111"
    assert new_books[1]["id"] == "333"


def test_fetch_rss_entries_extracts_goods_no():
    mock_entry = MagicMock()
    mock_entry.get = lambda k, d="": {
        "link": "http://www.yes24.com/Goods/FTGoodsView.aspx?goodsNo=147344423",
        "title": "[도서] 테스트 책",
        "category": "건강",
    }.get(k, d)

    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]

    with patch("rss_checker.feedparser.parse", return_value=mock_feed):
        entries = fetch_rss_entries("http://example.com/rss.xml")

    assert len(entries) == 1
    assert entries[0]["id"] == "147344423"
    assert entries[0]["title"] == "[도서] 테스트 책"
