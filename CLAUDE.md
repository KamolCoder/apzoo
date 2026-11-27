# apzoo — notes for Claude

Owner: Kamol. Answer in Russian, code and code comments in English. Short, essentials first.
Do not write code until Kamol says «делай».

Company website of the Animal Planet pet store chain (Tashkent, ~30 stores). Info only — no online shop.
Backend forked from `zooplaneta-site` (Zoo Planeta) — same models/CMS/SEO; the frontend is written from scratch and must not
look like Zoo Planeta. Nothing here depends on ZooCorpApp (stores can be imported from its export).

## Stack
Django 5.2 + Wagtail 7.4, SQLite (WAL, IMMEDIATE transactions; file in `/app/data` mounted from the host
`/srv/animalplanet`, nightly `backup_db --with-files`), whitenoise, gunicorn, Docker.
Low-traffic site: keep it small — container 384 MB / 0.5 CPU, gunicorn 2 workers × 2 threads.
No frontend build: hand-written `static/css/site.css`, vanilla JS (`static/js/site.js`, `stores.js`),
self-hosted Unbounded + Golos Text fonts and Leaflet (no CDNs).

## Structure
- `config/` settings/urls. Languages ru/uz/en via `i18n_patterns` (`/ru/…`), `WAGTAIL_I18N_ENABLED`,
  translations with `wagtail.contrib.simple_translation`. CMS at `ADMIN_URL` (default `cms/`).
- `core/` — `SiteSettings` (contacts, one set for all languages), StreamField blocks (`blocks.py`),
  UI strings `ui.py` (`{% t "key" %}`; no gettext), template tags `site_tags.py`, `seed_demo` (covers every page type,
  block and setting; `--missing` adds absent sections to a live site, `--photos` runs seed_photos), `import_stores`,
  `seed_photos` (sample Unsplash photos in the «Демо-фото (Unsplash)» collection; `--remove` deletes them).
- `pages/` — Home (fixed section order: hero (headline with orange last word `|accent_last`, up to 3 photos as a collage,
  button + «find store», store count badge, 4 quick links) → orange ticker of catalogue sections → deals of the week →
  intro+numbers → categories as numbered rows → about+advantages → stores (count + search + map) → delivery/UDS duo →
  news (lead + list) → charity → brands grid → extra blocks); Standard, Contact, Promo index/page, News index/page (rubric `kind`,
  `?kind=` filter, NewsArticle JSON-LD), Careers/Vacancy, Partners, CharityIndex/CharityPage («Помогаем животным»: project /
  event / animal story, RU+UZ), DeliveryPage (own app + aggregators StreamField) and LoyaltyPage (UDS), RU+UZ.
  App Store / Google Play / UDS link + code / short call-centre number live in SiteSettings; `{% qr url %}` (segno)
  renders inline SVG QR codes.
- `catalog/` — informational catalogue: CategoryIndexPage/CategoryPage (icon, subcategories, brands) and the `Brand`
  snippet. No products/prices; `code_1c` fields are the hook for a future 1C OData sync.
  `FormPageMixin`: POST → `leads.handling.handle_lead_form` (honeypot, 10/hour per IP, notify) → `?sent=1`.
- `stores/` — StoreIndexPage (list + map, city/district filters, JSON in page) and StorePage (city, manager name +
  photo, photo gallery `StorePhoto`, JSON-LD PetStore, nearby stores); overview maps (`data-overview-map`) are lazy-initialised in `stores.js`;
  `GET /api/stores/<lang>/`.
- CMS: Wagtail default colours (no recolouring), Animal Planet logo via `templates/wagtailadmin/*`, light theme forced
  for everyone (`core/signals.py` + migration, theme choice hidden in `static/css/cms.css`), start page panels in
  `core/dashboard.py` (quick actions, new leads, running promos).
- SEO: `core/seo.py` (meta title/description with per-page `seo_auto_title/description`, hreflang + x-default,
  OG, JSON-LD @graph: Organization/WebSite, PetStore, JobPosting, BreadcrumbList), `core/sitemap.py` (all locales
  + xhtml:link), robots in `core/views.py`. Absolute URLs come from `SITE_URL`; `sync_site` (run at container start)
  writes it into Wagtail's Site. Verification codes + Metrika/GA4 in SiteSettings (counters only when DEBUG=False).
- Icons: `static/icons/*` built by `manage.py make_icons` from `static/img/logo.png` (rerun when an SVG/bigger logo
  arrives); `/favicon.ico`, `/apple-touch-icon.png`, `/site.webmanifest` served from the site root (`core/views.py`).
- Deploy: host nginx on the timkon.uz server, `deploy/nginx/animalplanet.conf` → `/etc/nginx/conf.d/`, included from
  nginx.conf; certbot --nginx adds HTTPS; app on 127.0.0.1:8031.
- `leads/` — JobApplication / PartnerRequest / Feedback, Wagtail ModelViewSets («Заявки», CSV export).
  CVs in `PRIVATE_MEDIA_ROOT`, downloaded only via `/cms/leads/resume/<name>` (needs view perm).

## Design
Brand from the logo: black `#000`, white, orange `#F07F1B` accent; cream `#F3EFE7` for light sections.
Unbounded (headings, numbers) + Golos Text (text). Orange text only on black; on light surfaces orange is a fill
(badges, buttons, ticker, offset photo frame). Sharp corners everywhere, pill buttons (`.pill-or/-dark/-line/-line-w`),
hairline rules and numbered lists (`01`, `|two_digits`). Sections alternate black / cream / white (`.sec-black`, `.sec-cream`).
Black sticky header; nav collapses into a full-screen black menu below 1320 px. Giraffe silhouette (`#i-giraffe`) is the
graphic motif and the placeholder (`includes/ph.html`) until photos. Header/footer use `static/img/logo-wide.png`
(cropped from the 150 px logo — replace with a big/SVG logo when it arrives). Container 1360 px.
Mascot: flat vector giraffe drawn in code (`core/mascot.py`: parts + pivots, poses = part rotations). `manage.py make_mascot`
writes `static/mascot/giraffe-<pose>[-mono].svg` (idle, stretch, talk, win, sleep, newyear, navruz, wave, head) and the
inline rig `templates/includes/mascot_rig.svg` (pose / season classes on an ancestor move the parts via its own CSS);
rerun it after editing `core/mascot.py` — a test fails on stale files. 404 uses giraffe-wave.svg.
Footer giraffe (`{% giraffe %}`, `core/easter.py`, `includes/giraffe.html`, the rig): click → stretch + talk pose, random animal fact (20, ru/uz/en),
after 7 clicks → win + wave pose, promo code from SiteSettings «Пасхалка с жирафом» (Metrika goal / GA4 event `giraffe_code`); seasonal
looks by Tashkent time: hat + scarf 20 Dec–10 Jan, tulips + wreath in March, sleep pose with «Zzz» 22:00–07:00.
Motion: `.reveal` / `.reveal-group` fade-in on scroll (only under `html.js`, off with reduced motion), ticker animation.
Name is «Animal Planet» (Latin) in every language.

## Content rules
EN is for foreign partners: home, about, stores, catalogue, partners, contacts. Promos/news/vacancies/charity/delivery/UDS are RU+UZ;
untranslated pages are hidden from that language's menu automatically.
Uzbek uses ʻ (U+02BB) and ʼ (U+02BC): oʻ, gʻ, maʼlumot.

## Run / test
```bash
DEBUG=True python manage.py migrate && DEBUG=True python manage.py seed_demo
DEBUG=True python manage.py test core
```
Previews: Playwright screenshots (OSM tiles are blocked in the sandbox — route them to a stub SVG).

## Git
Work branch `claude/magical-archimedes-lm2gn3`; Kamol merges PRs himself. No force push.
