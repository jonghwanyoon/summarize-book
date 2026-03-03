# Book Summarizer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** yes24 도서 링크를 받아 분야별 맞춤 요약 + 추천을 Obsidian 마크다운으로 생성하는 Claude Code Skill, 그리고 RSS 피드에서 새 도서를 탐지하는 Python 스크립트를 구현한다.

**Architecture:** 마스터 스킬(SKILL.md)이 Playwright 크롤링 + 분류를 수행하고, 8개 분야별 가이드라인 파일(category-*.md)을 참조하여 맞춤 요약을 생성한다. RSS 스크립트는 feedparser로 피드를 파싱하여 새 도서 URL을 출력한다.

**Tech Stack:** Claude Code Skill (markdown), Playwright (Python), feedparser (Python)

---

## Task 1: 마스터 스킬 SKILL.md 작성

**Files:**
- Create: `~/.claude/skills/summarize-book/SKILL.md`

**Step 1: 스킬 디렉토리 생성**

```bash
mkdir -p ~/.claude/skills/summarize-book
```

**Step 2: SKILL.md 작성**

`SKILL.md`에 포함할 내용:

```markdown
---
name: summarize-book
description: "yes24 도서 링크를 받아 분야별 맞춤 요약 + 추천을 Obsidian 마크다운으로 생성"
---

# 도서 요약 및 추천

yes24 도서 페이지를 크롤링하여 내용을 유추하고, 분야별 전문 기준으로 평가합니다.

## 작업 프로세스

1. **URL 검증**: argument로 전달된 URL이 yes24 도서 페이지(yes24.com/Product/Goods/)인지 확인
2. **Playwright 크롤링**: 반드시 Playwright tool로 페이지에 접근하여 아래 정보 추출
   - 제목 (한글 + 원서명)
   - 저자, 역자
   - 출판사
   - 가격 (정가, 판매가)
   - 평점 (yes24 평점)
   - 출간일
   - 소개글 (책 설명 전문) — `#infoset_introduce` 영역
   - 목차 전문 — 목차 영역
   - 표지 이미지 URL — `https://image.yes24.com/goods/{상품ID}/XL`
   - 카테고리 정보 — 페이지의 분류/카테고리 breadcrumb
3. **분류**: `categories.md` 파일을 읽고, 추출한 카테고리 정보를 8개 그룹 중 하나로 매핑
4. **가이드라인 로드**: 분류된 그룹에 해당하는 `category-{그룹}.md` 파일을 읽기
5. **내용 유추 및 요약**: 가이드라인의 지시에 따라 요약 생성 (아래 출력 포맷 참조)
6. **이미지 저장**: 표지 이미지를 다운로드하여 `./ATTACHMENTS/{유니크제목}_cover.png`로 저장
   - 유니크 제목: 한글 제목에서 공백을 `-`로, 특수문자 제거 (예: `클린-코드`)
   - 다운로드: `curl -o ./ATTACHMENTS/{파일명} {이미지URL}` 또는 Playwright
7. **마크다운 생성**: 아래 포맷으로 `./00_INBOX/{한글제목}.md` 파일 생성

## 출력 포맷

### YAML Frontmatter

​```yaml
---
id: "{원서 제목 또는 한글 제목}"
aliases: "{한글 번역 제목}"
tags:
  - book/{카테고리}/{세부주제1}
  - book/{카테고리}/{세부주제2}
  - (최대 6개)
author: {저자-이름-kebab-case}
publisher: {출판사}
published_date: {출간일 YYYY-MM-DD}
price: {판매가 숫자만}
yes24_rating: {평점}
created_at: {현재시각 YYYY-MM-DD HH:mm}
source: {yes24 URL}
category: "{8개 그룹명}"
recommendation: "{★ 평가} {추천문구}"
---
​```

### 본문 구조

​```markdown
# {한글 제목}

![[{유니크제목}_cover.png]]

## 기본 정보
| 항목 | 내용 |
|------|------|
| 저자 | {저자명} |
| 출판사 | {출판사} |
| 가격 | {판매가}원 (정가 {정가}원) |
| 평점 | {평점}/10 |
| 출간일 | {출간일} |

## 소개글 요약
(yes24 페이지의 책 소개글을 간결하게 한국어로 정리)

## 목차
(원본 목차를 그대로 포함)

## 내용 유추
> 제목, 소개글, 목차를 종합하여 이 책이 실제로 다루는 내용을 추론합니다.

### 핵심 주제
(이 책이 말하려는 중심 메시지 1-2문단)

### 장별 내용 예측
(목차의 각 파트/장이 어떤 내용을 다룰지 구체적으로 유추. 장마다 2-3문장)

### 저자의 관점과 접근법
(소개글에서 드러나는 저자의 시각, 방법론, 논조 분석)

## 추천 평가
(category-{그룹}.md의 평가 기준에 따라 작성)

### 강점
(이 책의 강점 3-5개)

### 약점/주의사항
(이 책의 약점이나 주의할 점 2-3개)

### 종합 판정: {★★★★★} {추천 문구}
(최종 판정 근거를 2-3문장으로)
​```

## 태그 규칙

- 최대 6개
- 구조: `book/{카테고리}/{세부주제}`
- 카테고리: tech-it, business, self-help, humanities, literature, science, education, travel
- 세부주제: 소문자, 공백은 `-`, 구체적 키워드 (예: `book/tech-it/clean-code`)
- 추천 등급 태그 추가: `book/rating/must-read`, `book/rating/recommended`, `book/rating/average`, `book/rating/not-recommended`, `book/rating/warning`

## 주의사항

- 반드시 Playwright tool로 페이지에 접근할 것 (fetch tool 사용 금지)
- `./00_INBOX` 및 `./ATTACHMENTS` 디렉토리가 없으면 생성할 것
- 이미지는 하나도 누락 없이 저장하고 문서에 포함할 것
```

**Step 3: 스킬이 로드되는지 확인**

```bash
ls -la ~/.claude/skills/summarize-book/SKILL.md
```

Expected: 파일이 존재하고 내용이 올바름

---

## Task 2: 카테고리 분류 기준표 작성

**Files:**
- Create: `~/.claude/skills/summarize-book/categories.md`

**Step 1: categories.md 작성**

yes24 분야 → 8개 그룹 매핑 테이블과 분류 가이드를 포함하는 파일.

내용:

```markdown
# 도서 카테고리 분류 기준

## 매핑 테이블

| yes24 분야 | 그룹 | 가이드라인 파일 |
|-----------|------|---------------|
| 컴퓨터와 인터넷 | 기술/IT | category-tech-it.md |
| 컴퓨터 | 기술/IT | category-tech-it.md |
| 비즈니스와 경제 | 비즈니스/경제 | category-business.md |
| 자기관리 | 자기관리/실용 | category-self-help.md |
| 건강/취미/실용 | 자기관리/실용 | category-self-help.md |
| 수험서/자격증 | 자기관리/실용 | category-self-help.md |
| 인문 | 인문/사회/역사 | category-humanities.md |
| 사회 | 인문/사회/역사 | category-humanities.md |
| 역사와 문화 | 인문/사회/역사 | category-humanities.md |
| 인물 | 인문/사회/역사 | category-humanities.md |
| 문학 | 문학/예술 | category-literature.md |
| 예술/대중문화 | 문학/예술 | category-literature.md |
| 자연과 과학 | 과학 | category-science.md |
| 어린이 | 교육/어린이 | category-education.md |
| 유아 | 교육/어린이 | category-education.md |
| 국어와 외국어 | 교육/어린이 | category-education.md |
| 여행과 지리 | 여행/지리 | category-travel.md |

## 분류 방법

1. 크롤링한 페이지의 카테고리/breadcrumb 정보를 확인
2. 위 매핑 테이블에서 가장 가까운 yes24 분야를 찾아 그룹 결정
3. 카테고리 정보가 불명확하면, 제목과 소개글 내용으로 판단
4. 여러 분야에 걸치면, 핵심 주제가 속하는 그룹을 선택
```

---

## Task 3: 8개 분야별 가이드라인 파일 작성

**Files:**
- Create: `~/.claude/skills/summarize-book/category-tech-it.md`
- Create: `~/.claude/skills/summarize-book/category-business.md`
- Create: `~/.claude/skills/summarize-book/category-self-help.md`
- Create: `~/.claude/skills/summarize-book/category-humanities.md`
- Create: `~/.claude/skills/summarize-book/category-literature.md`
- Create: `~/.claude/skills/summarize-book/category-science.md`
- Create: `~/.claude/skills/summarize-book/category-education.md`
- Create: `~/.claude/skills/summarize-book/category-travel.md`

> 이 Task는 8개 파일을 병렬로 작성할 수 있음. 각 파일은 독립적.

**공통 구조** (모든 파일에 적용):

```markdown
# {분야명} 도서 평가 가이드

## 대상 독자 프로필
(이 분야 독자가 기대하는 것, 전형적 독자 특성)

## 요약 스타일
(이 분야에 맞는 요약 톤, 초점, 사용할 용어 수준)

## 품질 평가 기준
(이 분야에서 좋은 책의 기준 5-7개)

## 헛소리 감지 규칙
(이 분야에서 흔한 과장/허위/비현실적 주장 패턴 5-7개)

## 추천 등급 기준
- ★★★★★ 강력 추천: (구체적 기준)
- ★★★★☆ 추천: (구체적 기준)
- ★★★☆☆ 보통: (구체적 기준)
- ★★☆☆☆ 비추천: (구체적 기준)
- ★☆☆☆☆ 경고: (구체적 기준)
```

**Step 1: category-tech-it.md 작성**

핵심 차별점:
- 코드 예시 유무 및 품질
- 기술 트렌드 시의성 (출간일 vs 기술 변화)
- 실무 적용 가능성
- 저자의 실무 경력/오픈소스 기여도
- 헛소리: "이 기술 하나면 취업 보장", 이미 죽은 기술 다루기, 공식 문서 복붙

**Step 2: category-business.md 작성**

핵심 차별점:
- 비현실적 수익률 탐지 (예: "1000만원으로 월 300만원 배당")
- 구체적 데이터/사례 vs 감성적 주장 비율
- 저자의 실제 경력/자격 (금융자격증, 실제 투자경력 등)
- 경제학 기본 원리와의 일관성
- 헛소리: 보장된 수익, 비밀 공식, 부자 마인드만으로 성공

**Step 3: category-self-help.md 작성**

핵심 차별점:
- 근거 없는 성공 공식 탐지
- 과학적 뒷받침 여부 (심리학 연구, 통계 등)
- 실행 가능한 구체적 액션 아이템 존재 여부
- 저자의 전문성 (학위, 실제 경험)
- 헛소리: "생각만 바꾸면 인생이 바뀐다", 생존자 편향 사례, 감성 포르노

**Step 4: category-humanities.md 작성**

핵심 차별점:
- 학술적 엄밀성
- 출처/참고문헌 품질과 양
- 다양한 시각 반영 여부 (편향성 체크)
- 원전 인용 정확성
- 헛소리: 단일 사관 강요, 출처 없는 주장, 역사 왜곡

**Step 5: category-literature.md 작성**

핵심 차별점:
- 문학적 가치 (문체, 서사 구조)
- 작가의 문학적 배경과 수상 이력
- 작품의 주제 심층성
- 문학사적 위치와 영향력
- 요약 스타일: 스포일러 최소화, 분위기/테마 중심

**Step 6: category-science.md 작성**

핵심 차별점:
- 유사과학 탐지 (양자역학 남용, 뇌과학 과장 등)
- 인용 논문/연구 존재 여부
- 과학적 방법론 준수
- 대중화 vs 정확성 균형
- 헛소리: "양자역학으로 설명되는 마음의 힘", 체리피킹 연구

**Step 7: category-education.md 작성**

핵심 차별점:
- 연령 적절성
- 교육적 가치와 커리큘럼 연계성
- 부모/교사 활용도
- 아이 흥미 유발 요소
- 어학서: 실용적 학습법 vs 이론 나열

**Step 8: category-travel.md 작성**

핵심 차별점:
- 정보의 최신성 (출간일 중요)
- 실용적 팁 밀도 (교통, 숙소, 비용 등)
- 문화적 깊이 vs 표면적 관광 정보
- 저자의 실제 방문 경험 여부
- 헛소리: 오래된 정보 재탕, 인터넷 검색으로 대체 가능한 수준

---

## Task 4: 스킬 통합 테스트

**Step 1: 기술 서적으로 테스트**

```bash
# Claude Code에서 실행
/summarize-book https://www.yes24.com/Product/Goods/11681152
```

Expected:
- `./00_INBOX/클린-코드.md` 파일 생성
- `./ATTACHMENTS/클린-코드_cover.png` 이미지 저장
- YAML frontmatter에 `category: "기술/IT"` 포함
- "내용 유추" 섹션에 장별 내용 예측 존재
- 추천 평가에 기술/IT 기준 적용

**Step 2: 비기술 서적으로 테스트 (다른 분야)**

경제/비즈니스 분야 도서 하나를 선택하여 테스트. 분류가 올바르게 되는지, 해당 분야 가이드라인이 적용되는지 확인.

**Step 3: 결과 검토 및 수정**

출력 마크다운을 검토하고 필요 시 SKILL.md나 가이드라인 파일 수정.

---

## Task 5: RSS 체커 Python 스크립트 작성

**Files:**
- Create: `/mnt/d/git/summarize-book/rss_checker.py`
- Create: `/mnt/d/git/summarize-book/tests/test_rss_checker.py`
- Create: `/mnt/d/git/summarize-book/requirements.txt`

**Step 1: requirements.txt 작성**

```
feedparser>=6.0
```

**Step 2: 테스트 작성**

```python
# tests/test_rss_checker.py
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
```

**Step 3: 테스트 실행하여 실패 확인**

```bash
cd /mnt/d/git/summarize-book && pip install feedparser && python -m pytest tests/ -v
```

Expected: ImportError — rss_checker 모듈이 아직 없음

**Step 4: rss_checker.py 구현**

```python
#!/usr/bin/env python3
"""yes24 RSS 피드를 파싱하여 새 도서를 탐지하는 스크립트."""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

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
        book_id = entry.get("link", "").rstrip("/").split("/")[-1]
        entries.append({
            "id": book_id,
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "category": entry.get("category", ""),
        })
    return entries


def main():
    parser = argparse.ArgumentParser(description="yes24 RSS 피드에서 새 도서 탐지")
    parser.add_argument(
        "--rss-file",
        default="yes24_rss.md",
        help="RSS URL 목록 파일 경로 (default: yes24_rss.md)",
    )
    parser.add_argument(
        "--state-file",
        default="processed_books.json",
        help="처리 상태 파일 경로 (default: processed_books.json)",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="새 도서 발견 시 claude CLI로 summarize-book 스킬 호출",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="처리할 최대 도서 수 (0=무제한)",
    )
    args = parser.parse_args()

    rss_path = Path(args.rss_file)
    state_path = Path(args.state_file)

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

    if args.run:
        for book in all_new_books:
            print(f"\n요약 중: {book['title']}...")
            try:
                subprocess.run(
                    ["claude", "-s", "summarize-book", book["link"]],
                    check=True,
                )
                processed["processed"].append({
                    "id": book["id"],
                    "title": book["title"],
                    "url": book["link"],
                    "category": book["rss_category"],
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                })
            except subprocess.CalledProcessError as e:
                print(f"  Error: {e}", file=sys.stderr)
    else:
        # --run 없이 실행 시에도 상태에 기록 (중복 출력 방지)
        for book in all_new_books:
            processed["processed"].append({
                "id": book["id"],
                "title": book["title"],
                "url": book["link"],
                "category": book.get("rss_category", ""),
                "processed_at": datetime.now(timezone.utc).isoformat(),
            })

    processed["last_checked"] = datetime.now(timezone.utc).isoformat()
    save_processed_books(state_path, processed)
    print("\n상태 파일 업데이트 완료.")


if __name__ == "__main__":
    main()
```

**Step 5: 테스트 실행하여 통과 확인**

```bash
cd /mnt/d/git/summarize-book && python -m pytest tests/ -v
```

Expected: 4개 테스트 모두 PASS

**Step 6: 실제 RSS 피드로 수동 테스트**

```bash
cd /mnt/d/git/summarize-book && python rss_checker.py --limit 3
```

Expected: 각 RSS 피드에서 도서 목록이 출력되고, `processed_books.json`이 생성됨

---

## Task 6: 전체 통합 테스트 및 마무리

**Step 1: 스킬 테스트 — 기술 서적**

Obsidian vault 디렉토리에서 Claude Code를 열고:

```
/summarize-book https://www.yes24.com/Product/Goods/11681152
```

검증:
- [ ] `./00_INBOX/` 에 마크다운 파일 생성됨
- [ ] `./ATTACHMENTS/` 에 표지 이미지 저장됨
- [ ] YAML frontmatter 형식 올바름
- [ ] category가 "기술/IT"로 분류됨
- [ ] "내용 유추" 섹션에 핵심 주제 / 장별 예측 / 저자 관점 존재
- [ ] "추천 평가"에 기술/IT 기준 적용됨
- [ ] Obsidian에서 열었을 때 이미지가 정상 표시됨

**Step 2: 스킬 테스트 — 비기술 서적**

비즈니스/경제 분야 도서로 테스트하여 분류 및 가이드라인 적용 확인.

**Step 3: RSS → 스킬 연동 테스트**

```bash
python rss_checker.py --limit 1 --run
```

검증:
- [ ] RSS에서 도서 1권 탐지
- [ ] claude CLI로 summarize-book 호출
- [ ] 마크다운 + 이미지 정상 생성
- [ ] processed_books.json에 처리 기록 저장

**Step 4: 문제 있으면 수정, 없으면 커밋**

```bash
cd /mnt/d/git/summarize-book
git init
git add rss_checker.py tests/ requirements.txt yes24_rss.md docs/
git commit -m "feat: book summarizer system - skill + RSS checker"
```
