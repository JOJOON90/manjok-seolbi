# 만족설비 사이트

경남·부산 전지역 배관설비 전문 — 만족설비

## 파일 구조

```
├── data/
│   ├── config.json      # 사업체 정보 + 지역/서비스 설정
│   └── posts/           # 후기 JSON 파일들
├── scripts/
│   └── build.py         # 빌드 스크립트
├── assets/
│   ├── css/style.css
│   └── img/             # 이미지 파일들
└── netlify.toml
```

## 후기 JSON 구조

```json
{
  "slug": "지역-서비스-날짜",
  "title": "제목",
  "description": "메타 설명",
  "region": "김해 장유",
  "service_name": "수전 교체",
  "service_slug": "faucet-replace",
  "date": "2026-01-01",
  "thumbnail": "/assets/img/posts/{slug}/{파일명}",
  "body_html": "본문 HTML"
}
```
