# رُكن الكوكيز · Cookie Nook

A bilingual (Arabic / English) single-page website for a small-batch artisan cookie shop.
Warm, playful, and fully vector-illustrated — no external image assets.

![status](https://img.shields.io/badge/status-ready-2f7d4f) ![stack](https://img.shields.io/badge/stack-HTML%20%2F%20CSS%20%2F%20Vanilla%20JS-c98b58)

## Highlights

- **Two moods, no reload** — Morning (cream, beige, warm yellow) and Evening
  (deep brown, caramel, golden glow) switch instantly and persist in `localStorage`.
- **Full RTL / LTR** — every string, price and layout direction swaps between
  Arabic and English, including the document `lang` and `dir`.
- **Working basket** — add, merge, increment, remove, free-delivery progress,
  checkout confirmation with confetti, and an order number.
- **Product filtering** — chocolate / fruity / nutty / classic, plus favourites.
- **Offer countdown** — a 24-hour timer that survives reloads.
- **Validated forms** — contact and newsletter with inline errors and toasts.
- **Responsive & accessible** — mobile drawer navigation, keyboard focus handling,
  reduced-motion support, skip link, semantic landmarks and ARIA states.
- **Hand-authored SVG art** — hero flat-lay, six cookies, a bakery storefront and
  the favicon, all generated from `tools/gen_art.py`.

## Running it

Any static server works, because the site has no build step:

```powershell
python -m http.server 8000
```

Then open <http://127.0.0.1:8000/>.

> Opening `index.html` directly from disk also works, but a local server is
> recommended so fonts and storage behave consistently.

## Project layout

```
index.html            Page markup, inline SVG icon sprite, bilingual copy
css/styles.css        Design system, themes, RTL rules, responsive breakpoints
js/data.js            Bilingual dictionary + product / add-on catalogue
js/main.js            i18n, themes, rendering, basket, forms, countdown, reveals
assets/               Generated SVG illustrations
tools/gen_art.py      Regenerates every SVG in assets/
tools/capture.py      Headless-Chrome screenshot tour (DevTools Protocol)
tools/qa_check.py     60 functional checks against the live page
```

## Regenerating the artwork

```powershell
python tools/gen_art.py
```

The script uses only the standard library and rewrites:

- `hero-cookies.svg`, `about-bakery.svg`, `favicon.svg`
- `cookie-classic.svg`, `cookie-double.svg`, `cookie-strawberry.svg`,
  `cookie-pistachio.svg`, `cookie-oat.svg`, `cookie-caramel.svg`

## Quality checks

With the site running on port 8000 and Chrome installed:

```powershell
python tools/capture.py     # screenshot tour for visual review
python tools/qa_check.py    # functional smoke tests (expects 60 passes)
```

Both scripts drive a private headless Chrome instance and do not touch your
normal browser profile.

## Notes

- Prices are in Saudi Riyal (`ر.س` / `SAR`); free delivery starts at 100.
- State keys: `cookienook.lang`, `cookienook.theme`, `cookienook.cart`,
  `cookienook.likes`, `cookienook.offerEnd`.
- Checkout is a front-end demo: it confirms the order and clears the basket
  without taking payment.
