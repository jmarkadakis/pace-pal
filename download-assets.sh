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

# ---- Map the known originals to the canonical names the HTML expects ----
map() {  # $1 source basename, $2 dest path
  if [ -f "$SRC/$1" ]; then cp "$SRC/$1" "$2" && echo "  → $1  →  $2"; fi
}

echo "Mapping product + lifestyle shots to the names the pages use:"
map "pace-clock-primary.png"          "$OUT/led-clock.jpg"      # LED studio shot
map "pace-pal-pace-clock-9.jpg"       "$OUT/led-clock-2.jpg"    # LED alt
map "Clock-LCD-unnamed.jpg"           "$OUT/lcd-clock.jpg"      # LCD studio shot
map "IMG_9702.jpg"                    "$OUT/lcd-lifestyle.jpg"  # LCD on deck
map "underwater-image.jpg"            "$OUT/in-pool.jpg"        # hero: swimmer + clock
map "underwater-image.jpg"            "$OUT/og-image.jpg"       # social share image
map "mypacepal-arm-over-clock.jpg"    "$OUT/in-pool-2.jpg"      # about / lifestyle
map "mypacepal-peter-vanderkaay.png"  "$OUT/vanderkaay.png"     # endorser portrait

echo ""
echo "──────────────────────────────────────────────────────────"
echo "Done. Originals are in $SRC/."
echo "Open index.html and confirm the product photos show. To swap a"
echo "specific shot, copy the file you want from $SRC/ over images/led-clock.jpg"
echo "(etc.). Missing files simply show a styled placeholder."
