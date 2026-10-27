"""Generate the static Japanese, English and Spanish ReCorta websites."""
from __future__ import annotations

from datetime import date
from html import escape
import json
from pathlib import Path
import shutil
from xml.etree import ElementTree as ET
from xml.dom import minidom

ROOT = Path(__file__).resolve().parent
BASE = "https://www.recorta.jp"
TODAY = "2026-10-27"
LANGS = ("ja", "en", "es")
PAGES = ("index", "about", "service", "team", "history", "news")
SOURCE = Path(r"C:\Users\dalca\OneDrive\Recorta\assets")
BRAND = ROOT / "assets" / "brand"

with (ROOT / "content" / "site.json").open(encoding="utf-8-sig") as f:
    TEXT = json.load(f)
with (ROOT / "content" / "news.json").open(encoding="utf-8-sig") as f:
    POSTS = json.load(f)["posts"]


def e(value: object) -> str:
    return escape(str(value), quote=True)


def path_for(lang: str, page: str) -> str:
    prefix = "" if lang == "ja" else f"/{lang}"
    return f"{prefix}/" if page == "index" else f"{prefix}/{page}.html"


def post_path(lang: str, slug: str) -> str:
    prefix = "" if lang == "ja" else f"/{lang}"
    return f"{prefix}/news/{slug}.html"


def full(path: str) -> str:
    return BASE + path


def fmt_date(iso: str, lang: str) -> str:
    year, month, day = map(int, iso.split("-"))
    if lang == "ja":
        return f"{year}年{month}月{day}日"
    if lang == "en":
        return date(year, month, day).strftime("%B ") + str(day) + f", {year}"
    months = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
              "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"{day} de {months[month - 1]} de {year}"


def alternates(page: str, slug: str | None = None) -> str:
    url = (lambda lang: post_path(lang, slug)) if slug else (lambda lang: path_for(lang, page))
    links = [f'<link rel="alternate" hreflang="{lang}" href="{full(url(lang))}"/>' for lang in LANGS]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{full(url("ja"))}"/>')
    return "\n  ".join(links)


def org_data() -> dict:
    return {
        "@type": "Organization", "@id": BASE + "/#organization",
        "name": "ReCorta", "legalName": "合同会社ReCorta",
        "alternateName": ["レコルタ", "ReCorta（レコルタ）"],
        "url": BASE + "/", "logo": BASE + "/assets/brand/recorta-logo.svg",
        "foundingDate": "2026-09-09", "email": "diegoalonsojapan@gmail.com",
        "address": {"@type": "PostalAddress", "addressLocality": "西東京市",
                    "addressRegion": "東京都", "addressCountry": "JP"},
        "identifier": {"@type": "PropertyValue", "propertyID": "法人番号",
                       "value": "1012703003624"},
    }


def schema(lang: str, page: str, title: str, description: str,
           canonical: str, label: str = "", post: dict | None = None) -> str:
    t = TEXT[lang]
    org = org_data()
    website = {
        "@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/",
        "name": "ReCorta（レコルタ）" if lang == "ja" else "ReCorta",
        "alternateName": ["ReCorta", "レコルタ"],
        "inLanguage": {"ja": "ja-JP", "en": "en", "es": "es"}[lang],
        "publisher": {"@id": BASE + "/#organization"},
    }
    webpage = {
        "@type": "WebPage", "@id": canonical + "#webpage", "url": canonical,
        "name": title, "description": description,
        "inLanguage": {"ja": "ja-JP", "en": "en", "es": "es"}[lang],
        "isPartOf": {"@id": BASE + "/#website"},
        "about": {"@id": BASE + "/#organization"},
    }
    graph = [org, website]
    if page == "about":
        webpage["@type"] = "AboutPage"
    if post:
        webpage["breadcrumb"] = {"@id": canonical + "#breadcrumb"}
        article_schema = {
            "@type": "BlogPosting", "@id": canonical + "#article",
            "headline": post["translations"][lang]["title"],
            "description": post["translations"][lang]["summary"],
            "datePublished": post["date"], "dateModified": post["date"],
            "inLanguage": webpage["inLanguage"],
            "mainEntityOfPage": {"@id": canonical + "#webpage"},
            "author": {"@id": BASE + "/#organization"},
            "publisher": {"@id": BASE + "/#organization"},
        }
        if post.get("images"):
            article_schema["image"] = [
                BASE + "/assets/news/" + image["file"]
                for image in post["images"]
            ]
        graph.extend([
            {"@type": "BreadcrumbList", "@id": canonical + "#breadcrumb",
             "itemListElement": [
                 {"@type": "ListItem", "position": 1,
                  "name": "ReCorta（レコルタ）" if lang == "ja" else "ReCorta",
                  "item": full(path_for(lang, "index"))},
                 {"@type": "ListItem", "position": 2,
                  "name": t["nav"][5], "item": full(path_for(lang, "news"))},
                 {"@type": "ListItem", "position": 3,
                  "name": post["translations"][lang]["title"], "item": canonical},
             ]},
            article_schema,
        ])
    elif page != "index":
        webpage["breadcrumb"] = {"@id": canonical + "#breadcrumb"}
        graph.append({
            "@type": "BreadcrumbList", "@id": canonical + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1,
                 "name": "ReCorta（レコルタ）" if lang == "ja" else "ReCorta",
                 "item": full(path_for(lang, "index"))},
                {"@type": "ListItem", "position": 2, "name": label, "item": canonical},
            ],
        })
    graph.append(webpage)
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, indent=2)


def header(lang: str, current: str, t: dict) -> str:
    current_labels = dict(zip(PAGES, t["nav"]))
    nav = "".join(
        f'<a href="{e(path_for(lang, page))}"'
        + (' aria-current="page"' if page == current else "")
        + f'>{e(current_labels[page])}</a>'
        for page in PAGES
    )
    lang_buttons = "".join(
        f'<a lang="{other}" href="{e(path_for(other, current))}"'
        + (' aria-current="page"' if other == lang else "")
        + f' aria-label="{e(TEXT[other]["language"])}">'
        + e({"ja": "日本語", "en": "EN", "es": "ES"}[other]) + "</a>"
        for other in LANGS
    )
    return f'''<a class="skip-link" href="#main">{e(t["skip"])}</a>
<header class="site-header"><div class="header-wrap wrap">
  <div class="header-top">
    <a class="brand" href="{e(path_for(lang, "index"))}">
      <img src="/assets/brand/recorta-logo.svg" width="96" height="96" alt="ReCorta（レコルタ）"/>
    </a>
    <div class="header-actions">
      <nav class="language-switch" aria-label="{e(t["langLabel"])}">{lang_buttons}</nav>
      <button class="menu-toggle" type="button" aria-controls="navigation"
        aria-expanded="false" hidden>{e(t["menu"])}</button>
    </div>
  </div>
  <nav id="navigation" class="primary-nav" aria-label="{e(t["nav"][0])}">{nav}</nav>
</div></header>'''


def footer(lang: str, t: dict) -> str:
    nav = "".join(
        f'<a href="{e(path_for(lang, page))}">{e(label)}</a>'
        for page, label in zip(PAGES, t["nav"])
    )
    return f'''<footer class="site-footer"><div class="wrap footer-main">
  <div><a class="brand footer-brand" href="{e(path_for(lang,"index"))}">
    <img src="/assets/brand/recorta-logo.svg" width="88" height="88" alt="ReCorta（レコルタ）"/>
  </a><p>{e(t["tagline"])}</p></div>
  <div class="footer-nav"><h2>{e(t["nav"][0])}</h2>{nav}</div>
  <div><h2>{e(t["contact"])}</h2>
    <a href="mailto:diegoalonsojapan@gmail.com">diegoalonsojapan@gmail.com</a>
    <p>{e(t["locationValue"])}</p></div>
</div><div class="wrap footer-bottom"><span>{e(t["copyright"])}</span>
  <span>Field science &amp; technology</span></div></footer>'''


def crumbs(lang: str, t: dict, label: str = "") -> str:
    if not label:
        return ""
    name = "ReCorta（レコルタ）" if lang == "ja" else "ReCorta"
    return f'''<nav class="breadcrumbs wrap" aria-label="{e(t["articleLabel"])}">
  <a href="{e(path_for(lang,"index"))}">{e(name)}</a>
  <span aria-hidden="true">/</span><span aria-current="page">{e(label)}</span>
</nav>'''


def loader() -> str:
    animals = "".join(
        f'<img src="/assets/brand/{name}.svg" width="64" height="64" alt="" decoding="async"/>'
        for name in ("yamaneko", "fox", "ezoshika", "kumaoyako", "aosagi", "sansyouuo")
    )
    return f'''<div class="site-loader" hidden aria-hidden="true">
  <div class="loader-stage">
    <span class="loader-orbit"></span>
    <img class="loader-logo" src="/assets/brand/recorta-logo.svg" width="240" height="240" alt=""/>
    <div class="loader-animals">{animals}</div>
  </div>
</div>'''


def shell(lang: str, page: str, title: str, description: str,
          body: str, label: str = "", post: dict | None = None) -> str:
    canonical = full(post_path(lang, post["slug"])) if post else full(path_for(lang, page))
    locale = {"ja": "ja_JP", "en": "en_US", "es": "es_ES"}[lang]
    schema_json = schema(lang, page, title, description, canonical, label, post)
    article_type = "article" if post else "website"
    social_image = (BASE + "/assets/news/" + post["images"][0]["file"]
                    if post and post.get("images") else
                    BASE + "/assets/brand/recorta-logo.svg")
    social_image_type = "image/jpeg" if post and post.get("images") else "image/svg+xml"
    social_image_alt = (post["images"][0]["alt"][lang]
                        if post and post.get("images") else TEXT[lang]["logoAlt"])
    verification = ('  <meta name="google-site-verification" content="AGtMvbME9_p7O6w0GCPyxQbOeeC33mQJFybMO5lpgFI"/>\n'
                    if lang == "ja" and page == "index" else "")
    return f'''<!doctype html>
<html lang="{e(lang)}"><head>
  <meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{e(title)}</title><meta name="description" content="{e(description)}"/>
  <link rel="canonical" href="{e(canonical)}"/>
  {alternates(page, post["slug"] if post else None)}
  <meta property="og:type" content="{article_type}"/><meta property="og:locale" content="{locale}"/>
  <meta property="og:site_name" content="{e('ReCorta（レコルタ）' if lang == 'ja' else 'ReCorta')}"/>
  <meta property="og:title" content="{e(title)}"/><meta property="og:description" content="{e(description)}"/>
  <meta property="og:url" content="{e(canonical)}"/><meta property="og:image" content="{e(social_image)}"/>
  <meta property="og:image:alt" content="{e(social_image_alt)}"/>
{verification}  <meta property="og:image:type" content="{e(social_image_type)}"/>
  <meta name="theme-color" content="#4160ac"/>
  <link rel="icon" type="image/svg+xml" href="/assets/brand/recorta-logo.svg"/>
  <link rel="stylesheet" href="/style.css?v=20261027-field-notes"/>
  <script src="/site.js?v=20261027-orbit-loader" defer></script>
  <script type="application/ld+json">{schema_json}</script>
</head><body class="site-page" data-language="{e(lang)}">
  {loader()}
  {header(lang, page, TEXT[lang])}{crumbs(lang, TEXT[lang], label)}
  <main id="main">{body}</main>{footer(lang,TEXT[lang])}
</body></html>
'''


def card(post: dict, lang: str, t: dict) -> str:
    item = post["translations"][lang]
    return f'''<article class="news-card">
  <div class="news-card-meta"><span class="eyebrow">{e(post["category"][lang])}</span>
    <time datetime="{e(post["date"])}">{e(fmt_date(post["date"],lang))}</time></div>
  <h3><a href="{e(post_path(lang,post["slug"]))}">{e(item["title"])}</a></h3>
  <p>{e(item["summary"])}</p>
  <a class="text-link" href="{e(post_path(lang,post["slug"]))}">{e(t["readMore"])} <span aria-hidden="true">→</span></a>
</article>'''


def intro(label: str, title: str, copy: str, img: str, alt: str) -> str:
    return f'''<section class="page-intro"><div class="wrap intro-layout">
  <div><p class="eyebrow">{e(label)}</p><h1>{e(title)}</h1><p class="lead">{e(copy)}</p></div>
  <img src="/assets/brand/{e(img)}.svg" width="220" height="220" alt="{e(alt)}"/>
</div></section>'''


def home(lang: str, t: dict, posts: list[dict]) -> str:
    principles = "".join(
        f'<article class="principle"><span class="principle-index">0{i}</span>'
        f'<h3>{e(title)}</h3><p>{e(copy)}</p></article>'
        for i, (title, copy) in enumerate(t["principles"], 1)
    )
    cards = "".join(card(p, lang, t) for p in posts[:2]) or f'<p>{e(t["noNews"])}</p>'
    art = f'''<div class="hero-art" role="group" aria-label="{e(t["illustrationAlt"])}">
  <span class="art-ring" aria-hidden="true"></span>
  <img class="animal animal-cat" src="/assets/brand/yamaneko.svg" width="228" height="228" alt="{e(t["illustrationLabel"][0])}"/>
  <img class="animal animal-wolf" src="/assets/brand/wolf.svg" width="196" height="196" alt="{e(t["illustrationLabel"][2])}"/>
  <img class="animal animal-salamander" src="/assets/brand/sansyouuo.svg" width="176" height="176" alt="{e(t["illustrationLabel"][1])}"/>
  <img class="animal animal-fox" src="/assets/brand/fox.svg" width="150" height="150" alt="" aria-hidden="true"/>
  <img class="animal animal-deer" src="/assets/brand/ezoshika.svg" width="160" height="160" alt="" aria-hidden="true"/>
  <img class="animal animal-bear" src="/assets/brand/kumaoyako.svg" width="156" height="156" alt="" aria-hidden="true"/>
  <span class="art-caption">FIELD NOTES <i>·</i> RECORTA</span>
</div>'''
    body = f'''<section class="hero"><div class="wrap hero-grid">
  <div class="hero-copy"><p class="eyebrow"><span class="color-dot"></span>{e(t["homeKicker"])}</p>
    <h1>{e(t["homeTitle"])}</h1><p class="hero-lead">{e(t["homeLead"])}</p>
    <p class="hero-subline">{e(t["homeDesc"])}</p>
    <div class="button-row"><a class="button button-blue" href="{e(path_for(lang,"service"))}">{e(t["ctaProducts"])} <span aria-hidden="true">→</span></a>
      <a class="button button-outline" href="{e(path_for(lang,"about"))}">{e(t["ctaAbout"])}</a></div>
  </div>{art}
</div><div class="wrap hero-markers"><span>FIELD SCIENCE</span><span>WILDLIFE</span><span>ENVIRONMENT</span></div></section>
<section class="section products"><div class="wrap"><header class="section-heading">
  <p class="eyebrow">{e(t["productsKicker"])}</p><h2>{e(t["productsTitle"])}</h2><p>{e(t["productsIntro"])}</p>
</header><div class="product-grid">
  <article class="product-card product-blue"><div class="product-top"><span class="product-number">01 / WILDLIFE</span>
    <img src="/assets/brand/yamaneko.svg" width="120" height="120" alt="{e(t["illustrationLabel"][0])}"/></div>
    <p class="eyebrow">{e(t["wildCategory"])}</p><span class="status-pill">{e(t["wildStatus"])}</span>
    <h3 class="latin">WildCatcher</h3><p>{e(t["wildDesc"])}</p><p class="version-line">{e(t["wildVersion"])}</p>
    <a class="button button-dark" href="https://github.com/Theego99/WildCatcher-releases/releases/latest">{e(t["wildButton"])} <span aria-hidden="true">↗</span></a>
  </article>
  <article class="product-card product-green"><div class="product-top"><span class="product-number">02 / EIA TOOLKIT</span>
    <img src="/assets/brand/sansyouuo.svg" width="120" height="120" alt="{e(t["illustrationLabel"][1])}"/></div>
    <p class="eyebrow">{e(t["eiaCategory"])}</p><span class="status-pill">{e(t["eiaStatus"])}</span>
    <h3 class="latin">Wildpass</h3><p>{e(t["eiaDesc"])}</p>
    <a class="button button-dark" href="{e(path_for(lang,"service"))}#wildpass">{e(t["eiaButton"])} <span aria-hidden="true">→</span></a>
  </article>
</div></div></section>
<section class="section values"><div class="wrap values-grid"><div>
  <p class="eyebrow">{e(t["principlesKicker"])}</p><h2>{e(t["principlesTitle"])}</h2>
  <img class="value-illustration" src="/assets/brand/tsukinowaguma1.svg" width="230" height="230" alt=""/>
</div><div class="principles">{principles}</div></div></section>
<section class="section latest-news"><div class="wrap">
  <header class="section-heading section-heading-row"><div><p class="eyebrow">{e(t["newsKicker"])}</p><h2>{e(t["newsTitle"])}</h2></div>
    <a class="text-link" href="{e(path_for(lang,"news"))}">{e(t["newsAll"])} <span aria-hidden="true">→</span></a></header>
  <div class="news-grid">{cards}</div>
</div></section>
<section class="contact-band"><div class="wrap contact-row"><div><p class="eyebrow">ReCorta · Nishitokyo</p>
  <h2>{e(t["ctaTitle"])}</h2><p>{e(t["ctaText"])}</p></div>
  <a class="button button-red" href="mailto:diegoalonsojapan@gmail.com?subject={e(t["contactSubject"])}">{e(t["contact"])} <span aria-hidden="true">↗</span></a>
</div></section>'''
    return shell(lang, "index", t["homeTitle"], t["homeDesc"], body)


def page(lang: str, key: str, t: dict, posts: list[dict]) -> str:
    if key == "index":
        return home(lang, t, posts)
    if key == "about":
        title, desc, label, h1, lead = t["aboutTitle"], t["aboutDesc"], t["aboutKicker"], t["aboutH1"], t["aboutIntro"]
        content = intro(label, h1, lead, "recorta-logo", t["logoAlt"])
        rows = "".join(
            f'<div class="profile-row"><dt>{e(k)}</dt><dd>{e(v)}</dd></div>'
            for k, v in [
                (t["legal"], t["legalValue"]), (t["corporateNumber"], "1012703003624"),
                (t["founded"], t["foundedValue"]), (t["representative"], t["representativeValue"]),
                (t["location"], t["locationValue"]), (t["capital"], t["capitalValue"]),
                (t["business"], t["businessValue"]),
                (t["emailLabel"], "diegoalonsojapan@gmail.com"),
            ]
        )
        body = content + f'''<section class="section"><div class="wrap about-grid">
  <div><p class="eyebrow">{e(t["companyDetails"])}</p><h2 class="latin">ReCorta</h2>
    <p class="lead">{e(t["aboutText"])}</p><p>{e(t["homeDesc"])}</p>
    <div class="inline-links"><a class="text-link" href="{e(path_for(lang,"team"))}">{e(t["teamLink"])} →</a>
      <a class="text-link" href="{e(path_for(lang,"history"))}">{e(t["historyLink"])} →</a></div>
  </div><dl class="profile">{rows}</dl>
</div></section><section class="contact-band"><div class="wrap contact-row">
  <div><p class="eyebrow">ReCorta</p><h2>{e(t["contactButton"])}</h2></div>
  <a class="button button-red" href="mailto:diegoalonsojapan@gmail.com">{e(t["contact"])} ↗</a>
</div></section>'''
    elif key == "service":
        title, desc, label, h1, lead = t["serviceTitle"], t["serviceDesc"], t["serviceKicker"], t["serviceH1"], t["serviceIntro"]
        content = intro(label, h1, lead, "ezoshika", "")
        wild_list = "".join(f"<li>{e(x)}</li>" for x in t["wildFeatures"])
        eia_list = "".join(f"<li>{e(x)}</li>" for x in t["eiaFeatures"])
        body = content + f'''<section id="wildcatcher" class="section product-detail"><div class="wrap detail-grid">
  <div class="detail-art detail-blue"><span>01 / WILDLIFE ANALYSIS</span>
    <img src="/assets/brand/yamaneko.svg" width="280" height="280" alt="{e(t["illustrationLabel"][0])}"/></div>
  <div><p class="eyebrow">{e(t["wildCategory"])}</p><span class="status-pill">{e(t["wildStatus"])}</span>
    <h2 class="latin">WildCatcher</h2><p class="lead">{e(t["wildDesc"])}</p>
    <ul class="feature-list">{wild_list}</ul><p class="small-note">{e(t["wildNote"])}</p>
    <p class="version-line">{e(t["wildVersion"])}</p>
    <a class="button button-blue" href="https://github.com/Theego99/WildCatcher-releases/releases/latest">{e(t["wildButton"])} ↗</a>
  </div></div></section>
<section id="wildpass" class="section product-detail"><div class="wrap detail-grid">
  <div class="detail-art detail-green"><span>02 / EIA TOOLKIT</span>
    <img src="/assets/brand/sansyouuo.svg" width="280" height="280" alt="{e(t["illustrationLabel"][1])}"/></div>
  <div><p class="eyebrow">{e(t["eiaCategory"])}</p><span class="status-pill status-red">{e(t["eiaStatus"])}</span>
    <h2 class="latin">Wildpass</h2><p class="lead">{e(t["eiaDesc"])}</p>
    <ul class="feature-list">{eia_list}</ul><p class="small-note">{e(t["eiaPilot"])}</p>
    <aside class="notice">{e(t["eiaNote"])}</aside>
    <a class="button button-red" href="mailto:diegoalonsojapan@gmail.com?subject=Wildpass">{e(t["contactButton"])} ↗</a>
  </div></div></section><section class="section consulting"><div class="wrap consulting-grid">
  <div><p class="eyebrow">{e(t["consultTitle"])}</p><h2>{e(t["contactButton"])}</h2></div>
  <div><p>{e(t["consultText"])}</p><a class="text-link" href="mailto:diegoalonsojapan@gmail.com">{e(t["contact"])} ↗</a></div>
</div></section>'''
    elif key == "team":
        title, desc, label, h1, lead = t["teamTitle"], t["teamDesc"], t["teamKicker"], t["teamH1"], t["teamIntro"]
        content = intro(label, h1, lead, "aosagi", "")
        body = content + f'''<section class="section"><div class="wrap people-grid">
  <article class="person-card person-blue"><p class="eyebrow">{e(t["role1"])}</p><h2>{e(t["name1"])}</h2>
    <p class="latin roman-subtitle">{e(t["latin1"])}</p><p>{e(t["bio1"])}</p></article>
  <article class="person-card person-green"><p class="eyebrow">{e(t["role2"])}</p><h2 class="latin">{e(t["name2"])}</h2>
    <p class="roman-subtitle">{e(t["latin2"])}</p><p>{e(t["bio2"])}</p></article>
</div></section><section class="section field-story"><div class="wrap field-grid">
  <img src="/assets/brand/yamaneko.svg" width="310" height="310" alt="{e(t["illustrationLabel"][0])}"/>
  <div><p class="eyebrow">FIELD NOTES / TSUSHIMA</p><h2>{e(t["fieldTitle"])}</h2>
    <p class="lead">{e(t["fieldText"])}</p>
    <a class="text-link" href="{e(path_for(lang,"service"))}">{e(t["nav"][2])} →</a>
  </div></div></section>'''
    elif key == "history":
        title, desc, label, h1, lead = t["historyTitle"], t["historyDesc"], t["historyKicker"], t["historyH1"], t["historyIntro"]
        content = intro(label, h1, lead, "fox2", "")
        events = "".join(
            f'<li><time datetime="{e(iso)}">{e(printed)}</time><div><h2>{e(name)}</h2><p>{e(copy)}</p></div></li>'
            for iso, printed, name, copy in t["events"]
        )
        body = content + f'''<section class="section"><div class="wrap history-layout">
  <ol class="timeline">{events}</ol>
  <aside class="history-aside"><img src="/assets/brand/recorta-logo.svg" width="152" height="152" alt="ReCorta（レコルタ）"/>
    <p class="eyebrow">{e(t["companyDetails"])}</p><p>{e(t["tagline"])}</p>
    <a class="text-link" href="{e(path_for(lang,"about"))}">{e(t["nav"][1])} →</a>
  </aside></div></section>'''
    elif key == "news":
        title, desc, label, h1, lead = t["newsPageTitle"], t["newsDesc"], t["newsTitle"], t["newsH1"], t["newsLead"]
        content = intro(label, h1, lead, "akashobin", "")
        listings = "".join(card(post, lang, t) for post in sorted(posts, key=lambda x: x["date"], reverse=True))
        body = content + f'<section class="section"><div class="wrap news-grid news-archive">{listings or e(t["noNews"])}</div></section>'
    else:
        raise ValueError(f"Unknown page {key}")
    return shell(lang, key, title, desc, body, label)


def article(lang: str, post: dict) -> str:
    t = TEXT[lang]
    item = post["translations"][lang]
    title = item["title"] + (" | ReCorta（レコルタ）のお知らせ" if lang == "ja" else " | ReCorta")
    paragraphs = "".join(f"<p>{e(text)}</p>" for text in item["paragraphs"])
    images = "".join(
        f'''<figure><img src="/assets/news/{e(image['file'])}" width="1200" height="900"
          loading="lazy" decoding="async" alt="{e(image['alt'][lang])}"/>
          <figcaption>{e(image['caption'][lang])}</figcaption></figure>'''
        for image in post.get("images", [])
    )
    gallery = f'<div class="article-gallery">{images}</div>' if images else ""
    body = f'''<article class="section article"><div class="wrap article-wrap">
  <p class="eyebrow">{e(post["category"][lang])}</p>
  <time class="article-date" datetime="{e(post["date"])}">{e(fmt_date(post["date"],lang))}</time>
  <h1>{e(item["title"])}</h1><p class="article-lead">{e(item["summary"])}</p>
  <div class="article-content">{paragraphs}{gallery}
    <a class="button button-blue" href="{e(post["url"])}">{e(item["link"])} ↗</a>
  </div><a class="text-link article-back" href="{e(path_for(lang,"news"))}">← {e(t["articleBack"])}</a>
</div></article>'''
    return shell(lang, "news", title, item["summary"], body, t["nav"][5], post)


def sitemap() -> str:
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    xhtml = "http://www.w3.org/1999/xhtml"
    ET.register_namespace("", ns)
    ET.register_namespace("xhtml", xhtml)
    root = ET.Element(f"{{{ns}}}urlset")
    entries = [("page", key) for key in PAGES]
    entries += [("post", post["slug"]) for post in POSTS]
    for kind, key in entries:
        for lang in LANGS:
            routes = {
                alternate: (post_path(alternate, key) if kind == "post"
                            else path_for(alternate, key))
                for alternate in LANGS
            }
            current = ET.SubElement(root, f"{{{ns}}}url")
            ET.SubElement(current, f"{{{ns}}}loc").text = full(routes[lang])
            ET.SubElement(current, f"{{{ns}}}lastmod").text = TODAY
            for alternate, route in routes.items():
                ET.SubElement(current, f"{{{xhtml}}}link", {
                    "rel": "alternate", "hreflang": alternate, "href": full(route)
                })
            ET.SubElement(current, f"{{{xhtml}}}link", {
                "rel": "alternate", "hreflang": "x-default", "href": full(routes["ja"])
            })
    return minidom.parseString(ET.tostring(root, encoding="utf-8")).toprettyxml(
        indent="  ", encoding="UTF-8"
    ).decode("utf-8")


def main() -> None:
    BRAND.mkdir(parents=True, exist_ok=True)
    for asset in ("recorta-logo.svg", "ReCorta-Regular.otf", "yamaneko.svg",
                  "sansyouuo.svg", "wolf.svg", "akashobin.svg", "aosagi.svg",
                  "ezoshika.svg", "fox.svg", "fox2.svg", "honndoten.svg",
                  "kuma-baby1.svg", "kumababy2.svg", "kumababys.svg",
                  "kumaoyako.svg", "tsukinowaguma1.svg", "tsukinowaguma2.svg",
                  "tsushimaten.svg"):
        source = SOURCE / asset
        if source.is_file():
            shutil.copy2(source, BRAND / asset)
        elif not (BRAND / asset).is_file():
            raise FileNotFoundError(f"Official brand asset not found: {source}")

    for lang in LANGS:
        folder = ROOT if lang == "ja" else ROOT / lang
        folder.mkdir(parents=True, exist_ok=True)
        for key in PAGES:
            name = "index.html" if key == "index" else f"{key}.html"
            (folder / name).write_text(page(lang, key, TEXT[lang], POSTS),
                                       encoding="utf-8", newline="\n")
        article_dir = folder / "news"
        article_dir.mkdir(parents=True, exist_ok=True)
        for post in POSTS:
            (article_dir / f'{post["slug"]}.html').write_text(
                article(lang, post), encoding="utf-8", newline="\n"
            )

    (ROOT / "404.html").write_text(
        f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="robots" content="noindex"/><title>ページが見つかりません | ReCorta</title>
<link rel="stylesheet" href="/style.css?v=20261027-field-notes"/></head>
<body><main class="not-found wrap"><img src="/assets/brand/recorta-logo.svg" width="100" height="100" alt="ReCorta（レコルタ）"/>
<p class="eyebrow">404 / NOT FOUND</p><h1>お探しのページは見つかりません。</h1>
<a class="button button-blue" href="/">ホームへ戻る</a>
<nav class="language-switch" aria-label="Language"><a href="/en/">English</a><a href="/es/">Español</a></nav></main></body></html>
''', encoding="utf-8", newline="\n")
    (ROOT / "sitemap.xml").write_text(sitemap(), encoding="utf-8", newline="\n")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: https://www.recorta.jp/sitemap.xml\n",
        encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
