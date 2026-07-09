# Early-stage smell catalog

The 15 review lenses. Each finder agent takes ONE lens (section headers below match the perspective
keys exactly), reads its section, and hunts only that class of smell. Per lens: **Signals** (what it
says to a visitor, seed for the finding's `whyNotLive`), **Look for** (where in the codebase),
**Grep** (concrete patterns, case-insensitive unless stated), **Skip** (what NOT to report, and which
lens owns a borderline case, so two finders never file the same smell twice), **Live** (what to check
on the deployed product, read-only GETs only).

Severity guide (grade the single most visible instance; visibility decides, never code quality):
- **high**: a first-time visitor or paying customer will very likely see it and lose trust, or it breaks
  the funnel (dead checkout link, lorem ipsum on the landing, noindex on the whole site).
- **medium**: visible to an attentive visitor or to crawlers (default og-image, missing meta description,
  mixed-language string, console errors).
- **low**: visible only in edge cases or view-source (commented-out blocks in shipped HTML, verbose
  console.log noise).

When torn between two grades, take the lower; the verifier re-grades on user impact anyway. Anything
behind an auth wall drops at least one grade.

Effort guide (grades the fix, not the hunt): S = one file, minutes. M = a few files or one flow.
L = structural (new pages, new service).

---

## 1. placeholder-content
**Signals**: the site was scaffolded and never finished.
**Look for**: lorem ipsum in any casing; "Coming soon", "Under construction", "TBD", "TODO" in shipped
COPY (rendered text, not code); `[INSERT ...]`, unrendered `{{...}}` or `%PLACEHOLDER%` leaking into
visible text; headings like "Your headline here"; `example.com` / `example@` in visible content or
mailto/tel links; UI-kit demo sections left in (default hero copy); "latest news" or blog dates frozen
long in the past.
**Grep**: `lorem|ipsum|coming soon|under construction|\[INSERT|your headline|example\.com|%[A-Z_]+%`
across page sources, content JSON/MD, and i18n files.
**Skip**: the HTML `placeholder=` input attribute (legit UX, do not grep the bare word "placeholder");
TODO/FIXME in code comments (code-hygiene-leaks owns those); `{{...}}` inside template source the engine
demonstrably renders.
**Live**: render key pages and read them as a first-time visitor.

## 2. test-demo-data
**Signals**: the data is fake, so the product looks fake.
**Look for**: John Doe / Jane Doe / Jonas Jonaitis / Vardenis Pavardenis; test@ / demo@ / foo@ emails;
phones like +370 600 00000 or 123456789; testimonials or client logos with no real client behind them;
seeded demo records visible in production views; prices like 0.01 or 99999; "Test product" entries.
**Grep**: `john doe|jane doe|jonaitis|vardenis|pavardenis|test@|demo@|acme` in shipped content and in
seed/fixture files, then confirm the file is imported by code that ships.
**Skip**: fixtures and factories used only by tests or storybook; `acme` inside test directories;
demo data reachable only after login is low, not high.
**Live**: check lists, tables, testimonials, and counters for obviously fabricated entries.

## 3. trust-legal
**Signals**: no real company stands behind this.
**Look for**: missing or empty privacy policy, terms, refund policy; missing cookie consent while
analytics/marketing cookies are actually set; footer without legal entity name, company code, address,
or VAT code where required; copyright year older than the current year; legal pages that are templates
with a foreign company's name left in; contact email or phone that does not match the entity or domain.
**Grep**: this lens greps for ABSENCE: list the routes, use `privacy|terms|refund|cookie` to locate the
legal pages, then check substance inside them (`UAB|GmbH|Ltd|Inc|©` plus a real address), and confirm
every footer legal link resolves to real content.
**Skip**: missing cookie banner when the site verifiably sets no non-essential cookies; entity details
absent from pages where local law does not require them.
**Live**: click every footer link; read the legal pages for template leftovers.

## 4. branding-assets
**Signals**: default scaffolding was never replaced.
**Look for**: default framework favicon (Next.js triangle, Vite logo, CRA atom); missing or default
og-image / twitter-image; missing apple-touch-icon and manifest icons; default 404/500 pages ("This page
could not be found", unstyled); "Welcome to Next.js/Vite" leftovers; UI-kit demo images or unsplash
placeholders in production sections; the public canonical domain still a `*.vercel.app` / `*.netlify.app`
host; inconsistent logo variants.
**Grep**: `favicon|og-image|opengraph|apple-touch|manifest` in the head/layout; list `public/` and diff
against the framework's default scaffold assets (identical filename plus identical size is a strong tell).
**Skip**: a plain but clearly custom favicon; unbranded pages reachable only behind auth.
**Live**: GET `/favicon.ico`, the og-image URL, and a nonexistent path to see the 404 page.

## 5. seo-metadata
**Signals**: nobody expects anyone to find this site.
**Look for**: default titles ("Create Next App", framework names); missing or duplicated meta
descriptions; `noindex` / `nofollow` left on from staging; missing canonical; missing or broken
`robots.txt` and `sitemap.xml`; sitemap listing pages that 404 or missing real pages; missing OG and
Twitter card tags; missing hreflang on multilingual sites; missing structured data where the content
type calls for it.
**Grep**: `noindex|Create Next App|metadataBase|robots|sitemap|hreflang|canonical` in layouts, head
components, and `public/`.
**Skip**: noindex on auth-only or utility routes (dashboards, previews); missing structured data on
content types where none is expected.
**Live**: GET `/robots.txt`, `/sitemap.xml`; view-source the head of the main pages.

## 6. dead-ends
**Signals**: the building has doors painted on the walls.
**Look for**: `href="#"` or empty href on visible links; buttons with no handler; nav items pointing at
pages that do not exist; social icons linking to the network's homepage instead of a profile; "Read more"
to nowhere; pagination past real content; disabled features still shown in nav.
**Grep**: `href="#"|href=""|href=''|to="/undefined|onClick={\s*}` then cross-check every route referenced
in nav, footer, and CTAs against the actual route/page list.
**Skip**: `href="#section"` in-page anchors; `href="#"` on elements where a JS handler IS attached
(confirm the handler is absent before reporting).
**Live**: GET every internal link found on the main pages; note every non-200.

## 7. error-empty-states
**Signals**: nobody has ever hit an edge here.
**Look for**: raw stack traces or JSON error dumps reaching the user; "undefined", "null", "NaN",
"Invalid Date", "[object Object]" rendered in UI; unstyled framework error pages; empty lists with no
empty-state copy; loading states that never resolve; forms that fail silently.
**Grep**: grep the BUILT output or served HTML for `>undefined|>NaN|Invalid Date|\[object Object\]`;
bare `undefined` in source is pure noise, never grep it there. In source: find the error boundaries and
404/500 pages and check they are branded; check list components for an empty-state branch.
**Skip**: `undefined`/`null` in code logic (normal JS); an edge case you cannot show reaching a rendered
string.
**Live**: GET a nonexistent route, a malformed query, an empty-state page.

## 8. forms-transactions
**Signals**: the money path was never finished.
**Look for**: payment provider test keys or test mode in shipped config (`pk_test_`, `sk_test_`, sandbox
endpoints); checkout or signup flows that reference unfinished steps; forms without validation, success,
or failure feedback; transactional email from default/sandbox senders (onboarding@resend.dev, mailtrap,
@gmail.com for a company product); order/confirmation copy with placeholder values; prices inconsistent
between page, checkout, and legal text.
**Grep**: `pk_test_|sk_test_|sandbox|resend\.dev|mailtrap|noreply@example` in shipped config, env usage,
and the client bundle.
**Skip**: test keys in `.env.example`, test files, or CI config (they belong there); sandbox endpoints
behind a non-production flag verifiably off in prod. Secrets leaked to the client belong to
security-config; this lens owns test MODE on the money path.
**Live**: inspect the checkout button target and the client bundle for test-mode keys. Never submit a
real payment; stop at the provider redirect.

## 9. copy-localization
**Signals**: the text was machine-drafted and never proofread.
**Look for**: mixed languages on one page; raw i18n keys rendered (`home.hero.title`); untranslated
fallback strings; missing diacritics in languages that require them (Lithuanian: ą č ę ė į š ų ū ž);
transliterations (sh/zh/ch); inconsistent terminology for the same concept; anglicisms where the locale
style forbids them; tone jumps between marketing and product copy.
**Grep**: locale files for empty values and identical source/target strings; templates for hardcoded
strings bypassing i18n; `\bt\('` keys that do not exist in the locale files.
**Skip**: brand and product names intentionally untranslated; anglicisms the run's constraints or the
repo's own style guide allow.
**Live**: render each locale's main pages and read them in that language.

## 10. code-hygiene-leaks
**Signals**: the dev environment is showing through.
**Look for**: `console.log` / `print` noise in the shipped bundle; `debugger` statements; commented-out
blocks visible in served HTML; TODO/FIXME/HACK in files that ship; feature flags defaulted on for
unfinished features; dev-only routes reachable in production (`/test`, `/debug`, `/storybook`,
unprotected `/admin`); verbose logging of request payloads; source maps exposing internals in prod.
**Grep**: `console\.log|debugger|TODO|FIXME|HACK` only in files reachable from the app's real entry
points (not scripts/, tests, or tooling); `/debug|/test-` in the route table; build config for sourcemap
and feature-flag defaults.
**Skip**: console calls behind a logger wrapper silenced in prod; TODOs in tests, scripts, or docs that
never ship; storybook that is not deployed. TODO in RENDERED copy belongs to placeholder-content.
**Live**: open main pages and record browser console output; GET the suspect dev routes.

## 11. security-config
**Signals**: staging config went live.
**Look for**: localhost / 127.0.0.1 / staging URLs referenced by production code or content; secrets
committed or exposed to the client bundle (keys in `NEXT_PUBLIC_*` or equivalent); `http://` links on an
https site; wide-open CORS; missing basic security headers (CSP, X-Frame-Options, HSTS); API endpoints
that accept unauthenticated writes.
**Grep**: `localhost|127\.0\.0\.1|staging\.` in shipped code and content; `http://` ignoring xmlns,
w3.org, schema.org, and license URLs; scan client-exposed env vars for values that look secret (`sk_`,
`-----BEGIN`, long random strings).
**Skip**: publishable-by-design client values (Stripe `pk_live_`, analytics IDs, referrer-locked map
keys); localhost in dev-only config that never ships. A `*.vercel.app` canonical domain is
branding-assets; here report only staging/preview hosts wired into prod code.
**Live**: check response headers of the main pages; confirm canonical/host redirects (www vs non-www).

## 12. ops-analytics
**Signals**: nobody is watching this product run.
**Look for**: no analytics at all, or analytics pointed at a dev property; no error tracking wired in;
no uptime or health endpoint; emails/webhooks with no failure handling or retry; missing redirects from
legacy URLs; deployment artifacts (build IDs, debug banners) visible to users.
**Grep**: the analytics/error-tracking snippets and their IDs; compare env samples vs code for
observability config that exists but is never mounted.
**Skip**: analytics deliberately absent under a declared no-tracking stance (check the run constraints);
robots.txt and sitemap issues (seo-metadata owns them); server-side monitoring this sweep cannot see,
absence of the invisible is not evidence.
**Live**: view-source for analytics tags; GET the health endpoint if one is referenced.

## 13. performance-polish
**Signals**: it works on the dev machine, on fiber.
**Look for**: multi-megabyte unoptimized images; missing width/height causing layout shift; fonts loaded
without display strategy (FOUC/FOIT); render-blocking third-party scripts; no caching headers on static
assets; enormous client bundles for simple pages; missing loading states on slow data.
**Grep**: `public/` for files > 500 KB that a shipped page actually references; image components
bypassing the framework optimizer; font loading setup.
**Skip**: heavy files no shipped page references; dev-server slowness (judge the production build only).
**Live**: check response sizes and cache headers of the heaviest assets on the landing page.

## 14. responsive-mobile
**Signals**: nobody opened it on a phone.
**Look for**: missing viewport meta; fixed pixel widths that force horizontal scroll; tap targets under
~44 px; overlapping elements at narrow breakpoints; tables and code blocks that overflow; hover-only
interactions with no touch path; sticky elements covering content on small screens.
**Grep**: `viewport` meta in the layout; hardcoded `width:` pixel values in main page styles.
**Skip**: admin or auth-only screens; deliberate desktop-only surfaces declared in the constraints.
**Live**: render key pages at 375 px and 768 px widths (screenshot if a browser tool is available) and
look at them.

## 15. funnel-walkthrough
**Signals**: the happy path has never been walked end to end.
**Look for**: this lens does not grep, it WALKS. Follow the primary user journey as a skeptical
first-time customer: landing, understand the offer, pricing, start the flow, each step up to the last
safe read-only point. At every step ask: does it look operated (real data, recent dates, working links),
is the next step obvious, does anything contradict another page (price, promise, name)?
**Skip**: smells another lens owns, unless the walk shows them compounding on one step (a dead link plus
a contradictory price at checkout is one funnel finding); anything past the last safe read-only step.
**Live**: primarily a live-product lens; use the deployed URL when given, otherwise walk the route/page
sources in order. Cite each finding as URL plus step ("step 3, pricing to checkout"). Never submit a
form, create an account, or start a payment; stop at the provider redirect.

---

## Not smells (never report, any lens)
- Anything the run's `constraints` declare intentional.
- Internal docs, tests, fixtures, and comments that never reach the shipped bundle.
- Framework files users never see, unless they leak (a default 404 IS visible).
- Unfinished features genuinely unreachable from the shipped UI and unindexed.
- Style opinions with no "does not look live" component; that is `refine` territory.
