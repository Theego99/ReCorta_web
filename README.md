# ReCorta corporate website

Public site: https://www.recorta.jp/

The site is a static Japanese, English and Spanish website published by GitHub Pages from the repository root. Keep CNAME set to www.recorta.jp. Python's standard library builds the pages; no package installation is required.

## Pages and languages

Japanese is at the root (/). English lives in /en/ and Spanish in /es/. Each language has Home, Company, Products, Team, History and News pages, plus a translated detail page for every news post. Language links open the same page in the selected language.

build_site.py generates the HTML pages, per-page canonical and alternate-language links, structured data, and the XML sitemap. The generated pages remain ordinary, crawlable HTML if JavaScript is disabled.

## Visual identity

The logo and palette are supplied in assets/brand/. The official colours are blue #4160AC, Spanish red #D71428 and leafy green #50AF3E. The custom ReCorta font is assets/brand/ReCorta-Regular.otf; it includes the accented characters used in Spanish. The logo and the yamaneko, salamander and wolf illustrations are used throughout the site. These files are copied from C:\Users\dalca\OneDrive\Recorta\assets during the first build and kept in this repository for later builds.

## News and announcements

Write posts in content/news.json. Each post has a unique URL slug, publication date, topic label, official source link and Japanese, English and Spanish copy. Duplicate all three translations whenever adding an announcement. Then run python build_site.py from the repository folder; the builder adds the post to every News archive and creates its three localized detail pages and sitemap entries. Use accurate event dates and locations, and confirm that any announcement is suitable for the public website before adding it.

content/site.json holds the translated site wording and factual company details. After editing it, run the builder to regenerate the site. Keep the product descriptions current while preserving the distinction between the available WildCatcher app and the Wildpass EIA toolkit, which is still in pilot development.

## Search and company details

Every language version has a self-referencing canonical, hreflang alternates, a unique page title and description, and structured data for ReCorta. The homepage's Google Search Console verification tag must stay in the Japanese root page. The index.html root duplicate intentionally points to / as its canonical.

The company legal name is 合同会社ReCorta; its registered name must not be changed to a stock company. The representative member is 辰巳海斗. Publish only the confirmed 13-digit Japanese corporate number 1012703003624; do not add the separate company registry number or links to the national registry search. No private correspondence, registration documents, personal home address, seals, banking information, customer data or licence keys belong in this repository.

The incorporation date is September 9, 2026. WildCatcher 2.2.6 is the latest release for Windows and macOS as of October 21, 2026. Wildpass is an EIA toolkit under development and pilot evaluation; do not describe it as a released service, a legal compliance check or automated expert decision.
