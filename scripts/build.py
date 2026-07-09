#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, shutil, re
from pathlib import Path
from urllib.parse import quote
from datetime import datetime

BASE = Path(__file__).parent.parent
DATA = BASE / "data"
DIST = BASE / "dist"
ASSETS = BASE / "assets"

cfg = json.loads((DATA / "config.json").read_text(encoding="utf-8"))
BIZ = cfg["business"]
SERVICES = cfg["services"]
REGIONS = cfg["regions"]
SITE_URL = cfg["site"]["url"]
SITE_URL_TECH = cfg["site"].get("url_technical", SITE_URL)

SVC_MAP = {s["slug"]: s for s in SERVICES}

# ── 인근 지역 매핑 ──
NEARBY = {
    # 김해
    "gimhae-jangyu":      ["gimhae-yulha","gimhae-sambang","gimhae-juchon","changwon-daebang","changwon-sapa"],
    "gimhae-yulha":       ["gimhae-jangyu","gimhae-sambang","gimhae-samgye","changwon-daebang"],
    "gimhae-naedong":     ["gimhae-jangyu","gimhae-sambang","gimhae-naeoe"],
    "gimhae-naeoe":       ["gimhae-naedong","gimhae-samgye","gimhae-samjeong","gimhae-daeseong"],
    "gimhae-samgye":      ["gimhae-naeoe","gimhae-sambang","gimhae-yulha","gimhae-samjeong"],
    "gimhae-sambang":     ["gimhae-samgye","gimhae-jangyu","gimhae-naeoe","gimhae-yulha"],
    "gimhae-eobang":      ["gimhae-naedong","gimhae-samgye","gimhae-naeoe","gimhae-gusan"],
    "gimhae-gusan":       ["gimhae-eobang","gimhae-naeoe","gimhae-daecheong"],
    "gimhae-oedong":      ["gimhae-jinyeong","gimhae-jinrye","gimhae-juchon"],
    "gimhae-jinyeong":    ["gimhae-oedong","gimhae-jinrye","gimhae-juchon","gimhae-hanrim"],
    "gimhae-juchon":      ["gimhae-jinyeong","gimhae-oedong","changwon-daebang","gimhae-jangyu"],
    "gimhae-hwalcheon":   ["gimhae-naeoe","gimhae-daeseong","gimhae-buwon","gimhae-dongsang"],
    "gimhae-daeseong":    ["gimhae-hwalcheon","gimhae-naeoe","gimhae-buwon"],
    "gimhae-buwon":       ["gimhae-daeseong","gimhae-hwalcheon","gimhae-bonghwang"],
    # 창원
    "changwon-daebang":   ["changwon-sapa","changwon-gaeumjeong","gimhae-jangyu","gimhae-juchon"],
    "changwon-sapa":      ["changwon-daebang","changwon-gaeumjeong","changwon-sangnam","gimhae-jangyu"],
    "changwon-sangnam":   ["changwon-sapa","changwon-jungang-cw","changwon-yongji","changwon-daebang"],
    "changwon-jungang-cw":["changwon-sangnam","changwon-yongji","changwon-sapa"],
    "changwon-yongji":    ["changwon-sangnam","changwon-jungang-cw","changwon-bonsong"],
    "changwon-jaeun":     ["changwon-seokdong","changwon-yeojwa","changwon-idong","changwon-deoksan"],
    "changwon-seokdong":  ["changwon-jaeun","changwon-yeojwa","changwon-idong"],
    "changwon-yeojwa":    ["changwon-jaeun","changwon-seokdong","changwon-gyeonghwa"],
    "changwon-gamgye":    ["changwon-hoewon","changwon-yangdeok","changwon-seokjeon"],
    "changwon-hoewon":    ["changwon-gamgye","changwon-yangdeok","changwon-habseong"],
    "changwon-yangdeok":  ["changwon-hoewon","changwon-gamgye","changwon-seokjeon"],
    # 부산
    "busan_buk-geumgok":  ["busan_buk-hwamyeong","busan_buk-mandeok","busan_buk-gupo","busan_sasang-mora"],
    "busan_buk-hwamyeong":["busan_buk-geumgok","busan_buk-deokcheon","busan_sasang-mora"],
    "busan_buk-gupo":     ["busan_buk-geumgok","busan_buk-deokcheon","busan_sasang-samlak"],
    "busan_sasang-jurye": ["busan_sasang-gwaebop","busan_sasang-mora","busan_sasang-eomgung"],
    "busan_sasang-mora":  ["busan_buk-hwamyeong","busan_sasang-samlak","busan_sasang-jurye"],
}

def slug_to_region_district(slug):
    for rk, rv in REGIONS.items():
        for d in rv["districts"]:
            full = f"{rk}-{d['slug']}"
            if full == slug:
                return rv["name"], d["name"]
    return None, None

def get_all_posts():
    posts_dir = DATA / "posts"
    posts = []
    if posts_dir.exists():
        for f in posts_dir.glob("*.json"):
            try:
                p = json.loads(f.read_text(encoding="utf-8"))
                posts.append(p)
            except:
                pass
    posts.sort(key=lambda x: x.get("date",""), reverse=True)
    return posts

def encode_url(url):
    parts = url.split("/")
    return "/".join(quote(p, safe=":@!$&'()*+,;=") if i == 0 else quote(p, safe="") for i, p in enumerate(parts))

def punycode_url(url):
    return url.replace(SITE_URL, SITE_URL_TECH)

def head(title, desc, canonical, og_image=None, extra_meta=""):
    og_img = og_image or f"{SITE_URL_TECH}{cfg['site']['default_og_image']}"
    og_img_encoded = encode_url(og_img)
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow">
<meta name="author" content="{BIZ['name']}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img_encoded}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{title}">
<meta property="og:site_name" content="{BIZ['name']}">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_img_encoded}">
{extra_meta}<link rel="canonical" href="{punycode_url(canonical)}">
<link rel="stylesheet" href="/assets/css/style.css">
<link rel="icon" type="image/x-icon" href="/assets/img/favicon.ico">
<link rel="icon" type="image/png" sizes="16x16" href="/assets/img/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/img/favicon-48x48.png">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/img/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="/assets/img/android-chrome-192x192.png">
<link rel="icon" type="image/png" sizes="512x512" href="/assets/img/android-chrome-512x512.png">
</head>"""

def topbar():
    return f"""<div class="top-bar">
  📞 24시간 출장 상담 &nbsp;—&nbsp;
  <a href="tel:{BIZ['phone_tel']}">{BIZ['phone_display']}</a>
  &nbsp;|&nbsp;
  <a href="{BIZ['kakao_url']}" target="_blank" rel="noopener">💬 카톡 상담</a>
</div>"""

def header():
    return f"""<header class="header">
  <div class="header-inner">
    <a href="/" class="logo">만족<span>설비</span></a>
    <div class="header-actions">
      <a href="{BIZ['kakao_url']}" target="_blank" rel="noopener" class="header-kakao">💬 카톡상담</a>
      <a href="tel:{BIZ['phone_tel']}" class="header-phone">📞 {BIZ['phone_display']}</a>
    </div>
  </div>
</header>"""

def footer():
    return f"""<footer class="footer">
  <div class="footer-inner">
    <div>
      <div class="footer-logo">만족<span>설비</span></div>
      <div class="footer-info">
        경남·부산 전지역 배관설비 출장 서비스<br>
        📞 {BIZ['phone_display']} (연중무휴 24시간 상담)
      </div>
    </div>
    <div class="footer-info" style="font-size:13px;line-height:2;">
      <div>하수구 막힘 · 수전 교체</div>
      <div>변기 교체·수리 · 세면대 교체·수리</div>
      <div>욕조 배수구 교체</div>
    </div>
  </div>
  <div class="footer-bottom">© {datetime.now().year} {BIZ['name']}. All rights reserved.</div>
</footer>"""

def floating():
    return f"""<div class="floating-buttons">
  <a href="{BIZ['kakao_url']}" target="_blank" rel="noopener" class="floating-kakao">💬 카톡상담</a>
  <a href="tel:{BIZ['phone_tel']}" class="floating-call">📞 즉시통화</a>
</div>"""

def cta_box():
    return f"""<div class="cta-box">
  <h3>지금 막힘·누수로 곤란하신가요?</h3>
  <p>경남·부산 전지역 빠른 출장 가능합니다. 전화 한 통이면 바로 출동!</p>
  <div class="cta-buttons">
    <a href="tel:{BIZ['phone_tel']}" class="btn-cta-call">📞 {BIZ['phone_display']}</a>
    <a href="{BIZ['kakao_url']}" target="_blank" rel="noopener" class="btn-cta-kakao">💬 카톡으로 상담받기</a>
  </div>
  <p class="cta-tip">💡 카톡으로 사진 보내주시면 더 정확한 견적을 드릴 수 있어요.</p>
</div>"""

def promise_banner():
    items = ["꼼꼼한 시공", "정직한 견적", "KC인증 국산 부품", "미해결 시 0원 보장", "출장비 없음"]
    html = '<div class="promise-banner"><div class="promise-inner">'
    for i, item in enumerate(items):
        html += f'<span class="promise-item">✓ {item}</span>'
        if i < len(items)-1:
            html += '<span class="promise-dot">·</span>'
    html += '</div></div>'
    return html

# ── 인근 후기 찾기 ──
def find_related_posts(post, all_posts):
    region = post.get("region","")
    service_slug = post.get("service_slug","")
    slug = post.get("slug","")

    same_region_other_svc = []
    nearby_same_svc = []

    region_key = None
    district_key = None
    for rk, rv in REGIONS.items():
        if rv["name"] in region:
            region_key = rk
            for d in rv["districts"]:
                if d["name"] in region:
                    district_key = f"{rk}-{d['slug']}"
                    break
            break

    nearby_keys = NEARBY.get(district_key, []) if district_key else []
    nearby_region_names = set()
    for nk in nearby_keys:
        rn, dn = slug_to_region_district(nk)
        if rn and dn:
            nearby_region_names.add(f"{rn} {dn}")

    for p in all_posts:
        if p.get("slug") == slug:
            continue
        p_region = p.get("region","")
        p_svc = p.get("service_slug","")
        if p_region == region and p_svc != service_slug:
            same_region_other_svc.append(p)
        elif p_region in nearby_region_names and p_svc == service_slug:
            nearby_same_svc.append(p)

    return same_region_other_svc[:3], nearby_same_svc[:3]

def render_related(same_region, nearby, all_posts):
    if not same_region and not nearby:
        return ""
    html = '<section class="related-posts"><div class="related-posts-inner">'
    if same_region:
        html += '<h2>이 지역의 다른 작업 후기</h2>'
        html += '<div class="related-grid">'
        for p in same_region:
            thumb = p.get("thumbnail","")
            html += f"""<a href="/post/{p['slug']}/" class="related-card">
  <div class="related-thumb" style="background-image:url('{thumb}')"></div>
  <div class="related-body">
    <span class="related-badge">{p.get('service_name','')}</span>
    <div class="related-title">{p.get('title','')}</div>
    <div class="related-meta">📍 {p.get('region','')} · {p.get('date','')}</div>
  </div>
</a>"""
        html += '</div>'
    if nearby:
        html += '<h2 style="margin-top:32px;">인근 지역 작업 후기</h2>'
        html += '<div class="related-grid">'
        for p in nearby:
            thumb = p.get("thumbnail","")
            html += f"""<a href="/post/{p['slug']}/" class="related-card">
  <div class="related-thumb" style="background-image:url('{thumb}')"></div>
  <div class="related-body">
    <span class="related-badge">{p.get('service_name','')}</span>
    <div class="related-title">{p.get('title','')}</div>
    <div class="related-meta">📍 {p.get('region','')} · {p.get('date','')}</div>
  </div>
</a>"""
        html += '</div>'
    html += f'<a href="/reviews/" class="btn-all-reviews">📋 전체 후기 보기 →</a>'
    html += '</div></section>'
    return html

# ── 메인 페이지 ──
def build_index(all_posts):
    svc_html = ""
    for i, s in enumerate(SERVICES):
        svc_html += f"""<a href="/service/{s['slug']}/" class="svc-item">
  <div class="svc-item-left">
    <span class="svc-num">0{i+1}</span>
    <div>
      <div class="svc-name">{s['name']}</div>
      <div class="svc-desc">{s['description']}</div>
    </div>
  </div>
  <span class="svc-arr">→</span>
</a>"""

    recent = all_posts[:6]
    reviews_html = ""
    if recent:
        reviews_html = '<section class="reviews-section"><div class="section-inner">'
        reviews_html += '<p class="section-eyebrow">REVIEW</p>'
        reviews_html += '<h2 class="section-title">최근 작업 후기</h2>'
        reviews_html += '<div class="reviews-grid">'
        for p in recent:
            thumb = p.get("thumbnail","")
            reviews_html += f"""<a href="/post/{p['slug']}/" class="review-card">
  <div class="review-thumb" style="background-image:url('{thumb}')"></div>
  <div class="review-body">
    <span class="review-badge">{p.get('service_name','')}</span>
    <div class="review-title">{p.get('title','')}</div>
    <div class="review-meta">📍 {p.get('region','')} · {p.get('date','')}</div>
  </div>
</a>"""
        reviews_html += '</div>'
        if len(all_posts) > 6:
            reviews_html += '<div style="text-align:center;margin-top:24px;"><a href="/reviews/" class="btn-all-reviews" style="display:inline-block;padding:14px 32px;">📋 전체 후기 보기 →</a></div>'
        reviews_html += '</div></section>'

    why_html = """<section class="why-section">
  <div class="section-inner">
    <p class="section-eyebrow" style="color:#666;">WHY</p>
    <h2 class="section-title" style="color:#fff;">만족설비를 선택하는 이유</h2>
    <div class="why-grid">
      <div class="why-item">
        <div class="why-icon">🏆</div>
        <div class="why-title">10년+ 현장 경력</div>
        <div class="why-desc">5,000건 이상의 누적 시공 경험으로 어떤 상황도 빠르게 진단합니다.</div>
      </div>
      <div class="why-item">
        <div class="why-icon">🔩</div>
        <div class="why-title">KC인증 국산 부품만</div>
        <div class="why-desc">검증되지 않은 저가 수입품 대신 KC인증 국산 부품만 사용합니다.</div>
      </div>
      <div class="why-item">
        <div class="why-icon">💰</div>
        <div class="why-title">정직한 견적</div>
        <div class="why-desc">작업 전 견적을 명확히 안내드리며 추가 비용이 없습니다.</div>
      </div>
      <div class="why-item">
        <div class="why-icon">✅</div>
        <div class="why-title">미해결 시 0원 보장</div>
        <div class="why-desc">문제를 해결하지 못하면 비용을 받지 않습니다.</div>
      </div>
    </div>
  </div>
</section>"""

    canonical = f"{SITE_URL}/"
    local_biz_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": BIZ["name"],
        "telephone": BIZ["phone"],
        "url": SITE_URL_TECH,
        "description": BIZ["description"],
        "areaServed": ["경남", "부산", "김해", "창원"],
        "openingHours": "Mo-Su 00:00-23:59",
        "priceRange": "₩₩"
    }, ensure_ascii=False, indent=2)

    html = head(
        f"{BIZ['name']} — 경남·부산 배관설비 전문 24시간 출장",
        BIZ["description"],
        canonical,
        extra_meta=f'<script type="application/ld+json">{local_biz_ld}</script>\n'
    )
    html += f"""<body>
{topbar()}
{header()}
<main>
  <section class="hero">
    <div class="hero-inner">
      <div class="hero-left">
        <p class="hero-eyebrow">경남 · 부산 전지역 24시간 출장</p>
        <h1>배관 문제,<br>오늘 바로<br>해결합니다</h1>
        <p class="hero-sub">10년+ 현장 경력 · 5,000건+ 누적 시공<br>꼼꼼한 시공 · 정직한 견적 · 미해결 시 0원 보장</p>
        <div class="hero-btns">
          <a href="tel:{BIZ['phone_tel']}" class="btn-primary">📞 지금 바로 전화</a>
          <a href="{BIZ['kakao_url']}" target="_blank" rel="noopener" class="btn-kakao-hero">💬 카톡 상담</a>
        </div>
      </div>
      <div class="hero-stats">
        <div class="stat-box"><div class="stat-n">10년+</div><div class="stat-l">운영 경력</div></div>
        <div class="stat-box"><div class="stat-n">5,000+</div><div class="stat-l">누적 시공건</div></div>
        <div class="stat-box"><div class="stat-n">24H</div><div class="stat-l">연중무휴</div></div>
        <div class="stat-box"><div class="stat-n">0원</div><div class="stat-l">미해결 보장</div></div>
      </div>
    </div>
  </section>
  {promise_banner()}
  <section class="services-section">
    <div class="section-inner">
      <p class="section-eyebrow">SERVICE</p>
      <h2 class="section-title">서비스 안내</h2>
      <div class="svc-list">{svc_html}</div>
    </div>
  </section>
  {why_html}
  {reviews_html}
  <section style="padding:40px 24px;background:#fff;border-top:2px solid #1a1a1a;">
    <div class="section-inner">{cta_box()}</div>
  </section>
</main>
{footer()}
{floating()}
</body></html>"""
    return html

# ── 서비스 페이지 ──
def build_service(svc, all_posts):
    svc_posts = [p for p in all_posts if p.get("service_slug") == svc["slug"]][:9]
    canonical = f"{SITE_URL}/service/{svc['slug']}/"

    posts_html = ""
    if svc_posts:
        posts_html = '<div class="reviews-grid" style="margin-top:24px;">'
        for p in svc_posts:
            thumb = p.get("thumbnail","")
            posts_html += f"""<a href="/post/{p['slug']}/" class="review-card">
  <div class="review-thumb" style="background-image:url('{thumb}')"></div>
  <div class="review-body">
    <span class="review-badge">{p.get('region','')}</span>
    <div class="review-title">{p.get('title','')}</div>
    <div class="review-meta">📍 {p.get('region','')} · {p.get('date','')}</div>
  </div>
</a>"""
        posts_html += '</div>'
    else:
        posts_html = '<p style="color:#888;padding:24px 0;">작업 후기를 준비 중입니다.</p>'

    html = head(
        f"{svc['name']} — 경남·부산 전지역 | {BIZ['name']}",
        svc["description"],
        canonical
    )
    html += f"""<body>
{topbar()}
{header()}
<main>
  <div class="service-header">
    <div class="service-header-inner">
      <h1>{svc['name']}</h1>
      <p>{svc['description']}</p>
    </div>
  </div>
  {promise_banner()}
  <div style="max-width:1100px;margin:0 auto;padding:40px 24px;">
    <p class="section-eyebrow">REVIEW</p>
    <h2 class="section-title">{svc['name']} 작업 후기</h2>
    {posts_html}
    {cta_box()}
  </div>
</main>
{footer()}
{floating()}
</body></html>"""
    return html

# ── 후기 상세 페이지 ──
def build_post(post, all_posts):
    slug = post["slug"]
    title = post["title"]
    desc = post.get("description","")
    region = post.get("region","")
    svc_name = post.get("service_name","")
    date = post.get("date","")
    body = post.get("body_html","")
    thumb = post.get("thumbnail","")
    canonical = f"{SITE_URL}/post/{slug}/"

    og_img = ""
    if thumb:
        og_img = f"{SITE_URL_TECH}{thumb}"

    news_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": title,
        "description": desc,
        "image": [encode_url(og_img)] if og_img else [],
        "datePublished": date,
        "dateModified": date,
        "author": {"@type": "Organization", "name": BIZ["name"], "url": SITE_URL_TECH},
        "publisher": {
            "@type": "Organization",
            "name": BIZ["name"],
            "logo": {"@type": "ImageObject", "url": f"{SITE_URL_TECH}/assets/img/og-default.jpg"}
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": punycode_url(canonical)}
    }, ensure_ascii=False, indent=2)

    same_region, nearby = find_related_posts(post, all_posts)
    related_html = render_related(same_region, nearby, all_posts)

    svc_slug = post.get("service_slug","")
    svc_link = f"/service/{svc_slug}/" if svc_slug else "/"

    html = head(
        f"{title} | {BIZ['name']}",
        desc,
        canonical,
        og_image=og_img if og_img else None,
        extra_meta=f'<script type="application/ld+json">{news_ld}</script>\n'
    )
    html += f"""<body>
{topbar()}
{header()}
<main>
  <div class="post-header">
    <div class="post-header-inner">
      <h1>{title}</h1>
      <div class="post-meta">
        <span>📍 {region}</span>
        <span>📅 {date}</span>
        <span><a href="{svc_link}" style="color:var(--red);font-weight:700;">🔧 {svc_name}</a></span>
      </div>
    </div>
  </div>
  <div class="post-content">
    {body}
    {cta_box()}
  </div>
  {related_html}
</main>
{footer()}
{floating()}
</body></html>"""
    return html

# ── 후기 목록 페이지 ──
def build_reviews(all_posts, page=1, per_page=6):
    total = len(all_posts)
    total_pages = max(1, (total + per_page - 1) // per_page)
    start = (page-1)*per_page
    page_posts = all_posts[start:start+per_page]

    canonical = f"{SITE_URL}/reviews/" if page == 1 else f"{SITE_URL}/reviews/page/{page}/"

    cards = ""
    for p in page_posts:
        thumb = p.get("thumbnail","")
        cards += f"""<a href="/post/{p['slug']}/" class="review-card">
  <div class="review-thumb" style="background-image:url('{thumb}')"></div>
  <div class="review-body">
    <span class="review-badge">{p.get('service_name','')}</span>
    <div class="review-title">{p.get('title','')}</div>
    <div class="review-meta">📍 {p.get('region','')} · {p.get('date','')}</div>
  </div>
</a>"""

    pagi = '<div class="pagination">'
    if page > 1:
        prev = "/reviews/" if page == 2 else f"/reviews/page/{page-1}/"
        pagi += f'<a href="{prev}">‹</a>'
    for i in range(1, total_pages+1):
        url = "/reviews/" if i == 1 else f"/reviews/page/{i}/"
        cls = ' class="current"' if i == page else ''
        pagi += f'<a href="{url}"{cls}>{i}</a>'
    if page < total_pages:
        pagi += f'<a href="/reviews/page/{page+1}/">›</a>'
    pagi += '</div>'

    html = head(
        f"작업 후기 {f'(페이지 {page})' if page > 1 else ''} | {BIZ['name']}",
        f"경남·부산 배관설비 전문 {BIZ['name']}의 실제 작업 후기 모음입니다.",
        canonical
    )
    html += f"""<body>
{topbar()}
{header()}
<main>
  <div class="page-header">
    <div class="page-header-inner">
      <h1>작업 후기</h1>
    </div>
  </div>
  <div class="reviews-list-section">
    <div class="reviews-list-inner">
      <div class="reviews-grid">{cards}</div>
      {pagi}
    </div>
  </div>
</main>
{footer()}
{floating()}
</body></html>"""
    return html

# ── sitemap ──
def build_sitemap(all_posts):
    urls = [SITE_URL_TECH + "/"]
    urls.append(SITE_URL_TECH + "/reviews/")
    for s in SERVICES:
        urls.append(f"{SITE_URL_TECH}/service/{s['slug']}/")
    for p in all_posts:
        urls.append(f"{SITE_URL_TECH}/post/{p['slug']}/")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        xml += f"  <url><loc>{u}</loc></url>\n"
    xml += "</urlset>"
    return xml

# ── robots.txt ──
def build_robots():
    return f"""User-agent: *
Allow: /

User-agent: Yeti
Allow: /

User-agent: NaverBot
Allow: /

Sitemap: {SITE_URL_TECH}/sitemap.xml"""

# ── 이미지 압축 ──
def compress_images():
    try:
        from PIL import Image, ExifTags
        import io
        FAVICON_NAMES = {"favicon.ico","favicon-16x16.png","favicon-32x32.png",
                         "favicon-48x48.png","apple-touch-icon.png",
                         "android-chrome-192x192.png","android-chrome-512x512.png",
                         "og-default.jpg"}
        img_src = ASSETS / "img"
        img_dst = DIST / "assets" / "img"
        if not img_src.exists():
            return
        for src in img_src.rglob("*"):
            if not src.is_file():
                continue
            rel = src.relative_to(img_src)
            dst = img_dst / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.name in FAVICON_NAMES or src.suffix.lower() not in (".jpg",".jpeg",".png",".webp"):
                shutil.copy2(src, dst)
                continue
            try:
                img = Image.open(src)
                try:
                    for tag, val in (img._getexif() or {}).items():
                        if ExifTags.TAGS.get(tag) == "Orientation":
                            if val == 3: img = img.rotate(180, expand=True)
                            elif val == 6: img = img.rotate(270, expand=True)
                            elif val == 8: img = img.rotate(90, expand=True)
                            break
                except: pass
                if img.mode in ("RGBA","P"):
                    img = img.convert("RGB")
                MAX = 1600
                if max(img.size) > MAX:
                    img.thumbnail((MAX, MAX), Image.LANCZOS)
                img.save(dst, "JPEG", quality=82, optimize=True)
            except Exception as e:
                print(f"  압축 실패 {src.name}: {e}")
                shutil.copy2(src, dst)
    except ImportError:
        shutil.copytree(ASSETS / "img", DIST / "assets" / "img", dirs_exist_ok=True)

def write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def copy_netlify_redirects():
    src = BASE / "_redirects"
    if src.exists():
        shutil.copy2(src, DIST / "_redirects")

# ── MAIN ──
def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    # CSS
    css_dst = DIST / "assets" / "css"
    css_dst.mkdir(parents=True)
    shutil.copy2(ASSETS / "css" / "style.css", css_dst / "style.css")

    # 이미지
    compress_images()

    all_posts = get_all_posts()
    print(f"후기 {len(all_posts)}개 발견")

    # 메인
    write(DIST / "index.html", build_index(all_posts))

    # 서비스 페이지
    for s in SERVICES:
        write(DIST / "service" / s["slug"] / "index.html", build_service(s, all_posts))

    # 후기 목록
    per_page = 6
    total_pages = max(1, (len(all_posts) + per_page - 1) // per_page)
    write(DIST / "reviews" / "index.html", build_reviews(all_posts, 1, per_page))
    for pg in range(2, total_pages+1):
        write(DIST / "reviews" / "page" / str(pg) / "index.html", build_reviews(all_posts, pg, per_page))

    # 후기 상세
    for p in all_posts:
        write(DIST / "post" / p["slug"] / "index.html", build_post(p, all_posts))

    # sitemap, robots
    write(DIST / "sitemap.xml", build_sitemap(all_posts))
    write(DIST / "robots.txt", build_robots())

    copy_netlify_redirects()
    print("빌드 완료!")

if __name__ == "__main__":
    main()
