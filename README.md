# Pace Pal® — Website rebuild

A "badass" rebuild of [mypacepal.com](https://mypacepal.com/) by **Stellar Media Collective** — moving Pace Pal off WordPress/WooCommerce onto a fast, self-hosted static site with a **dark, high-tech athletic** look and a real **Stripe storefront**.

The concept is intact (the underwater pace clock for swimmers), but everything is reframed around the product's edge: bold, high-visibility digits you can read *on the bottom of the pool*. The hero is a **live, animated LED pace clock** rendered entirely in CSS/JS — no media required, on-brand, and impossible to ignore.

---

## Stack

Plain static HTML/CSS/JS (no build framework), matching the other Stellar client sites. Two Vercel serverless functions handle commerce and contact. Deploys to Vercel as-is.

- **Fonts:** Sora (display) + Inter (body) + Share Tech Mono (the LED readout), via Google Fonts
- **No browser dependencies** — one stylesheet, one script
- **Storefront:** `api/checkout.js` creates a **Stripe Checkout** session (Stripe hosts the payment page — no card data ever touches this site)
- **Contact:** `api/contact.js` emails submissions via [Resend](https://resend.com)
- **Pages are assembled** from a shared shell by `scripts/build.py` so the header/footer/cart never drift (`index.html` is hand-authored)

## Pages

| File | Page |
|------|------|
| `index.html` | Homepage — live LED clock hero, features, specs, products, training, founder (hand-authored) |
| `led-pace-clock.html` | LED product (buy box + specs) |
| `lcd-pace-clock.html` | LCD product (buy box + specs) |
| `training.html` | Training use ideas — USRPT, Endless Pools®, intervals |
| `about.html` | Larry's story / made-in-USA / guarantee |
| `contact.html` | Contact + inquiry form |
| `success.html`, `canceled.html` | Stripe Checkout return pages |
| `privacy-policy.html`, `terms.html` | Legal starter templates (review before publishing) |

## Editing content

The homepage is edited directly in `index.html`. Every other page is **generated** — edit its content in `scripts/build.py`, then run:

```bash
python3 scripts/build.py      # or: npm run build:pages
```

This rewrites the non-home `.html` files from the shared shell so the nav/footer/cart stay identical everywhere.

## ⚠️ One thing to confirm — LED price

The LCD price ($625) is confirmed from the current site. The **LED price is a placeholder ($795)** in two spots — change both to the real number:

- `js/main.js` → `PRODUCTS.led.price` (display) and drop `placeholderPrice`
- `api/checkout.js` → `CATALOG.led.amount` (in **cents**, e.g. `89500` = $895) — this is the amount Stripe actually charges

The homepage and LED product page note the price is provisional until you do this.

## Images

The site ships with elegant labeled **placeholders** for every photo slot, so it never looks broken. To drop in the real photos, run the downloader **on your Mac** (the cloud build can't reach the live CDN):

```bash
bash download-assets.sh       # or: npm run assets
```

It crawls mypacepal.com, mirrors every uploaded image into `images/source/`, and makes a best effort to map the main shots to the names the pages expect:

```
images/led-clock.jpg   images/lcd-clock.jpg
images/in-pool.jpg     images/larry.jpg   images/og-image.jpg
```

Review `images/source/` and copy the exact shot you want over any of those names. Every `<img>` falls back to a styled placeholder if a file is missing.

> The demo videos embedded on the home + training pages are the existing Pace Pal YouTube clips — swap the IDs in the markup if you want different ones.

## Environment variables

Set in Vercel → Project → Settings → Environment Variables:

```
STRIPE_SECRET_KEY = sk_live_…   (or sk_test_… while testing)
RESEND_API_KEY    = <reuse the existing Stellar Resend key>
SITE_URL          = https://mypacepal.com   (optional; used for Stripe redirects)
```

Without `STRIPE_SECRET_KEY` the cart shows a friendly "payments not configured yet" note instead of breaking. Without `RESEND_API_KEY` the contact form reports a friendly error. Leads currently route to `info@stellarmediacollective.com` (change `TO_EMAIL` in `api/contact.js` to send to Pace Pal directly).

## Local preview

```bash
python3 -m http.server 8000     # or: npm run dev
# open http://localhost:8000
```

The `/api/*` functions only run on Vercel (or `vercel dev`). Locally, checkout and the form will report a network error — that's expected.

## Deploy to Vercel

1. Push this folder to its own GitHub repo.
2. In Vercel, import it. Framework preset: **Other** (no build step).
3. Add the env vars above.
4. Deploy, run the asset downloader, confirm photos + LED price, then point `mypacepal.com` at it.

---

*Rebuilt by Stellar Media Collective.*
