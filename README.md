# ReCorta corporate website

Public site: https://www.recorta.jp/

Static Japanese website published by GitHub Pages from `main` at the repository root. Keep `CNAME` set to `www.recorta.jp`. There is no package installation or compilation step.

## Pages

- `index.html`: introduction, products, and current news.
- `about.html`: company profile and incorporation status.
- `service.html`: WildCatcher, Wildpass, and consulting enquiries.
- `team.html`: founders and their roles.
- `history.html`: company and product timeline.

Shared presentation and accessible navigation are in `style.css` and `site.js`. Core content and navigation work without JavaScript. The WebP photos are optimized copies of existing site assets; original photographs remain available in `assets`.

## Brand

The name is **ReCorta**, with capital R and C. The owner-supplied circular wildlife logo, including its ReCorta lettering, is preserved in `assets/recorta-logo-2026-source.jpg` (received September 27, 2026). The 512px logo, 192px navigation image, 32px favicon and 180px Apple touch icon are optimized derivatives with only the outer white margin trimmed and image sizing adjusted. The artwork and its white background are unchanged.

The corporate palette is sampled from this logo: light green `#BBE285`, sky blue `#9ADAFE`, white and near-black `#141819`. Pale green and blue surfaces extend the palette; a darker blue `#20586F` is used for readable links and text accents. Primary buttons use green with dark text. The corporate logo and palette are separate from WildCatcher product branding.

## Japanese search identity

Use **ReCorta（レコルタ）** for the bilingual public name, while keeping the registered legal name **合同会社ReCorta** unchanged. The reading appears in the visible header/footer and company profile, page titles and descriptions, and Open Graph metadata. Organization structured data lists レコルタ as an alternate name; the homepage also declares the WebSite name and its alternatives. Keep those names consistent when editing pages. The canonical domain is `https://www.recorta.jp/`; the sitemap is declared in `robots.txt`, and the 404 page remains `noindex`. Preserve the homepage Google site-verification tag to retain the owner’s Search Console verification.

## Content maintenance

Registration information updated September 27, 2026. The incorporation date is September 9, 2026. The legal name is 合同会社ReCorta; the public brand is ReCorta. The representative member is 辰巳海斗. Do not use 株式会社 titles such as 代表取締役 in the company profile.

The incorporation registration is complete. The corporate number (法人番号) **1012703003624** was verified and assigned September 18, 2026. The assignment date is distinct from the September 9 incorporation date. Publish only this 13-digit corporate number in the company profile and Organization structured data. Do not add the separate company registry number or links to the registry search. Wildpass is in development/pilot verification; do not describe it as a general production release or an automated legal assessment service.

No private correspondence, registration attachments, personal addresses, seals, banking information, license keys, or customer data are published in this repository. Update canonical links and `sitemap.xml` when changing routes.

## Search indexing maintenance

All home links must point to `/`, matching the homepage canonical and sitemap. GitHub Pages also serves `index.html`; its canonical intentionally points to `/`. Search Console's “Alternate page with proper canonical tag” for this duplicate is expected, not a reason to remove the canonical or add `noindex` to the homepage.

Each content page has a self-referencing canonical URL, a unique Japanese title and description, and WebPage structured data linked to the shared Organization and WebSite. The four inner pages include visible breadcrumbs and matching BreadcrumbList data. Keep structured data consistent with visible content and preserve crawlable HTML links even without JavaScript. Mobile menu rules apply only to `#navigation`, not breadcrumb navigation.

Keep the sitemap limited to the five canonical content URLs, excluding `index.html` and `404.html`. Update `lastmod` only when the corresponding page actually changes; do not regenerate dates on every deployment. A successful sitemap submission or live URL test does not guarantee indexing or ranking. For an uncrawled page, inspect and test its live URL in Search Console, then request indexing once after publishing improvements. Do not repeatedly request indexing, block duplicate URLs in robots.txt, or use the Indexing API for these ordinary corporate pages.
