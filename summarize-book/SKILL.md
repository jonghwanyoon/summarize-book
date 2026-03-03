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

```yaml
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
```

### 본문 구조

```markdown
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
```

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
