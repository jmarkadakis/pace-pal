#!/usr/bin/env bash
# ============================================================
# Pace Pal — asset downloader
# ------------------------------------------------------------
# Pulls the real photos from the current mypacepal.com (WordPress
# /wp-content/uploads/) into this project's images/ folder so the
# new site is fully self-contained.
#
#   ┌──────────────────────────────────────────────────────────┐
#   │  RUN THIS ON YOUR MAC — not in the cloud build.            │
#   │      cd pace-pal                                           │
#   │      bash download-assets.sh                               │
#   └──────────────────────────────────────────────────────────┘
#
# Safe to re-run. Requires curl (preinstalled on macOS).
# It crawls the public pages, extracts every uploaded image URL,
# mirrors the originals into images/source/, and then makes a best
# effort to map the main product shots to the names the pages use:
#     images/led-clock.jpg   images/lcd-clock.jpg
#     images/in-pool.jpg     images/larry.jpg   images/og-image.jpg
# Anything it can't map shows an elegant placeholder instead, so the
# site never looks broken. Review images/source/ and rename as needed.
# ============================================================
set -u

UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
SITE="https://mypacepal.com"
OUT="images"
SRC="$OUT/source"
mkdir -p "$SRC"

PAGES=(
  "/"
  "/shop/"
  "/about/"
  "/product/led-underwater-pace-clock-light-emitting-digits/"
  "/product/lcd-underwater-pace-clock-liquid-crystal-display-reflecting-ambient-light/"
)

echo "Crawling mypacepal.com and mirroring uploaded media into $SRC/ ..."
echo ""

# Collect every /wp-content/uploads/... image URL across the pages.
tmp_urls="$(mktemp)"
for pg in "${PAGES[@]}"; do
  curl -fsSL -A "$UA" "$SITE$pg" 2>/dev/null \
    | grep -oE 'https://[a-zA-Z0-9.\-]*mypacepal\.com/wp-content/uploads/[A-Za-z0-9_./~%-]+\.(jpg|jpeg|png|webp)' \
    | sed -E 's/-[0-9]+x[0-9]+(\.(jpg|jpeg|png|webp))$/\1/' \
    >> "$tmp_urls"
done
sort -u "$tmp_urls" -o "$tmp_urls"

ok=0
while IFS= read -r url; do
  [ -z "$url" ] && continue
  fn="$(basename "$url")"
  if [ ! -f "$SRC/$fn" ]; then
    if curl -fsSL -A "$UA" -e "$SITE/" "$url" -o "$SRC/$fn" 2>/dev/null && [ -s "$SRC/$fn" ]; then
      echo "  ↓ source/$fn"; ok=$((ok+1))
    fi
  fi
done < "$tmp_urls"
rm -f "$tmp_urls"

echo ""
echo "Mirrored $ok image(s) into $SRC/."
echo ""

# ---- Best-effort mapping to the canonical names the HTML expects ----
# Grab the FIRST uploads image referenced on each product page.
first_img() {  # $1 = page path  -> echoes a source filename or empty
  local url
  url="$(curl -fsSL -A "$UA" "$SITE$1" 2>/dev/null \
    | grep -oE 'https://[a-zA-Z0-9.\-]*mypacepal\.com/wp-content/uploads/[A-Za-z0-9_./~%-]+\.(jpg|jpeg|png|webp)' \
    | sed -E 's/-[0-9]+x[0-9]+(\.(jpg|jpeg|png|webp))$/\1/' \
    | head -n1)"
  [ -n "$url" ] && basename "$url"
}

map() {  # $1 source filename, $2 dest path
  if [ -n "$1" ] && [ -f "$SRC/$1" ]; then cp "$SRC/$1" "$2" && echo "  → mapped $1  →  $2"; fi
}

echo "Mapping main product shots (review & adjust if needed):"
map "$(first_img /product/led-underwater-pace-clock-light-emitting-digits/)" "$OUT/led-clock.jpg"
map "$(first_img /product/lcd-underwater-pace-clock-liquid-crystal-display-reflecting-ambient-light/)" "$OUT/lcd-clock.jpg"
map "$(first_img /about/)" "$OUT/larry.jpg"
# Hero / lifestyle: first image on the homepage that isn't the LED product
home_first="$(first_img /)"; map "$home_first" "$OUT/in-pool.jpg"
[ -f "$OUT/led-clock.jpg" ] && cp "$OUT/led-clock.jpg" "$OUT/og-image.jpg" && echo "  → og-image.jpg from led-clock.jpg"

echo ""
echo "──────────────────────────────────────────────────────────"
echo "Done. Originals are in $SRC/."
echo "Open index.html and confirm the product photos show. To swap a"
echo "specific shot, copy the file you want from $SRC/ over images/led-clock.jpg"
echo "(etc.). Missing files simply show a styled placeholder."
