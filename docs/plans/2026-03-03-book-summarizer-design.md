# Book Summarizer System Design

## 개요

yes24 도서 구매 링크를 받아 제목, 소개글, 목차를 기반으로 내용을 유추하고 요약하며, 읽을 가치가 있는지 추천하는 시스템.

두 가지 컴포넌트로 구성:
1. **Claude Code Skill (`summarize-book`)**: 링크를 받아 크롤링 → 분류 → 분야별 맞춤 요약 → Obsidian 마크다운 저장
2. **RSS 스크립트 (`rss_checker.py`)**: yes24 RSS 피드를 파싱하여 새 책을 탐지하고 URL 목록을 출력하는 수동 실행 Python 스크립트

---

## 결정 사항

| 항목 | 결정 |
|------|------|
| 아키텍처 | 마스터 스킬 + 8개 분야별 가이드라인 파일 |
| 호출 방식 | Claude Code Skill (`/summarize-book <url>`) |
| 출력 경로 | CWD 기준 `./00_INBOX`, `./ATTACHMENTS` |
| 요약 스타일 | 분야별 맞춤 (8개 카테고리) |
| 추천 기준 | 범용 품질 기준 (저자 인지도, 목차 구성, 독창성 등) |
| 크롤링 | Playwright (Python 1.58.0 설치됨) |
| RSS 자동화 | 수동 Python 스크립트 (자동화는 추후) |

---

## 1. 카테고리 그룹핑

yes24의 17개 분야를 8개 그룹으로 매핑:

| # | 그룹명 | yes24 분야 | 가이드라인 파일 |
|---|--------|-----------|---------------|
| 1 | 기술/IT | 컴퓨터와 인터넷, 컴퓨터 | `category-tech-it.md` |
| 2 | 비즈니스/경제 | 비즈니스와 경제 | `category-business.md` |
| 3 | 자기관리/실용 | 자기관리, 건강/취미/실용, 수험서/자격증 | `category-self-help.md` |
| 4 | 인문/사회/역사 | 인문, 사회, 역사와 문화, 인물 | `category-humanities.md` |
| 5 | 문학/예술 | 문학, 예술/대중문화 | `category-literature.md` |
| 6 | 과학 | 자연과 과학 | `category-science.md` |
| 7 | 교육/어린이 | 어린이, 유아, 국어와 외국어 | `category-education.md` |
| 8 | 여행/지리 | 여행과 지리 | `category-travel.md` |

---

## 2. 스킬 디렉토리 구조

```
~/.claude/skills/summarize-book/
├── SKILL.md                    # 마스터 스킬 (크롤링 + 분류 + 오케스트레이션)
├── categories.md               # 8개 카테고리 분류 기준표
├── category-tech-it.md         # 기술/IT 평가 가이드
├── category-business.md        # 비즈니스/경제 평가 가이드
├── category-self-help.md       # 자기관리/실용 평가 가이드
├── category-humanities.md      # 인문/사회/역사 평가 가이드
├── category-literature.md      # 문학/예술 평가 가이드
├── category-science.md         # 과학 평가 가이드
├── category-education.md       # 교육/어린이 평가 가이드
└── category-travel.md          # 여행/지리 평가 가이드
```

---

## 3. 마스터 스킬 흐름 (SKILL.md)

```
1. URL 수신 → yes24 도서 페이지인지 검증
2. Playwright로 페이지 크롤링
   - 제목, 저자, 출판사, 가격, 평점
   - 소개글 (책 설명)
   - 목차
   - 표지 이미지 URL
   - yes24 카테고리 정보
3. categories.md를 참조하여 8개 그룹 중 분류
4. 해당 카테고리 가이드라인 파일(category-*.md) 읽기
5. 가이드라인에 따라 분야별 맞춤 요약 + 추천 평가 생성
6. 표지 이미지 다운로드 → ./ATTACHMENTS/{유니크제목}_cover.png
7. Obsidian 마크다운 생성 → ./00_INBOX/{한글제목}.md
```

---

## 4. 출력 마크다운 포맷

### YAML Frontmatter

```yaml
---
id: "Clean Code"
aliases: "클린 코드 - 애자일 소프트웨어 장인 정신"
tags:
  - book/tech-it/software-engineering
  - book/clean-code
author: robert-c-martin
publisher: 인사이트
published_date: 2013-12-24
price: 33000
yes24_rating: 9.4
created_at: 2026-03-03 14:30
source: https://www.yes24.com/Product/Goods/11681152
category: 기술/IT
recommendation: "★★★★★ 강력 추천"
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
| 가격 | {가격}원 |
| 평점 | {평점}/10 |

## 소개글 요약
(yes24 페이지의 책 소개글을 간결하게 정리)

## 목차
(원본 목차를 그대로 포함)

## 내용 유추
> 제목, 소개글, 목차를 종합하여 이 책이 실제로 다루는 내용을 추론합니다.

### 핵심 주제
(이 책이 말하려는 중심 메시지 1-2문단)

### 장별 내용 예측
(목차의 각 파트/장이 어떤 내용을 다룰지 구체적으로 유추)

### 저자의 관점과 접근법
(소개글에서 드러나는 저자의 시각, 방법론, 논조 분석)

## 추천 평가
(분야별 전문 기준에 따른 평가)

### 강점
### 약점/주의사항
### 종합 판정: ★★★★★ {추천 문구}
```

---

## 5. 분야별 가이드라인 구조 (category-*.md)

각 가이드라인 파일은 동일한 구조를 따름:

```markdown
# {분야명} 도서 평가 가이드

## 대상 독자 프로필
(이 분야 독자가 기대하는 것)

## 요약 스타일
(이 분야에 맞는 요약 톤과 초점)

## 품질 평가 기준
(이 분야에서 좋은 책의 기준)

## 헛소리 감지 규칙
(이 분야에서 흔한 과장/허위 주장 패턴)

## 추천 등급 기준
- ★★★★★ 강력 추천: ...
- ★★★★☆ 추천: ...
- ★★★☆☆ 보통: ...
- ★★☆☆☆ 비추천: ...
- ★☆☆☆☆ 경고: ...
```

### 분야별 핵심 차별점

**기술/IT**: 코드 예시 유무, 기술 트렌드 시의성, 실무 적용 가능성, 저자의 실무 경력

**비즈니스/경제**: 비현실적 수익률 탐지, 구체적 데이터/사례 비율, 저자 경력/자격 검증, 경제학 원리와의 일관성

**자기관리/실용**: 근거 없는 성공 공식 탐지, 과학적 뒷받침 여부, 실행 가능한 액션 아이템 존재 여부

**인문/사회/역사**: 학술적 엄밀성, 출처/참고문헌 품질, 다양한 시각 반영 여부, 원전 인용 정확성

**문학/예술**: 문학적 가치, 작가의 문체와 서사 기법, 작품의 주제 심층성, 문학사적 위치

**과학**: 유사과학 탐지, 인용 논문/연구 존재 여부, 과학적 방법론 준수, 대중화 vs 정확성 균형

**교육/어린이**: 연령 적절성, 교육적 가치, 부모/교사 활용도, 아이 흥미 유발 요소

**여행/지리**: 정보의 최신성, 실용적 팁 밀도, 문화적 깊이 vs 표면적 관광 정보

---

## 6. 태그 정책 (도서용)

기존 summarize-article의 tag-policy.md를 기반으로, 도서에 맞게 조정:

- 최대 6개 태그
- 기본 prefix: `book/`
- 구조: `book/{카테고리}/{세부주제}`
- 예시:
  - `book/tech-it/software-engineering`
  - `book/business/investment`
  - `book/humanities/philosophy`
  - `book/recommendation/must-read` (추천 등급 태그)

---

## 7. RSS 스크립트 (Task 2)

### 파일 구조

```
summarize-book/
├── rss_checker.py              # RSS 파싱 + 새 책 탐지
├── yes24_rss.md                # RSS 피드 URL 목록 (기존)
├── processed_books.json        # 이미 처리된 책 ID 기록
└── requirements.txt            # feedparser
```

### 흐름

```
python rss_checker.py
  │
  ├─ yes24_rss.md에서 RSS URL 목록 로드
  ├─ 각 RSS 피드 파싱 (feedparser)
  ├─ processed_books.json과 대조하여 새 책 필터링
  ├─ 새 책 URL 목록 출력
  └─ (선택) --run 옵션 시 각 URL에 대해 `claude` CLI 호출
       claude -s summarize-book "{url}"
```

### 상태 관리

`processed_books.json`:
```json
{
  "last_checked": "2026-03-03T14:30:00",
  "processed": [
    {"id": "12345", "title": "클린 코드", "url": "https://...", "processed_at": "2026-03-03T14:30:00"},
    ...
  ]
}
```

---

## 8. 이미지 처리

- 표지 이미지: `{유니크제목}_cover.png`
- 본문 중 추가 이미지: `{유니크제목}_fig1.png`, `{유니크제목}_fig2.png`, ...
- 유니크 제목: 한글 제목을 kebab-case로 변환 (예: `클린-코드`)
- 저장 경로: `./ATTACHMENTS/`
- Obsidian 참조: `![[클린-코드_cover.png]]`

---

## 9. 향후 확장 가능성

- GitHub Actions / cron 자동화
- 개인 관심사 프로필 기반 추천 점수
- Obsidian 그래프 뷰에서 책 간 연결 관계 자동 생성
- 알라딘/교보문고 등 다른 서점 지원
