# Site videos

Two self-hosted loops, each in two cuts plus a poster. Since the 2026-10
design pass neither is on the homepage: both are generated footage, so the
hero uses the real underwater photo (`images/in-pool.jpg`) instead. They are
kept here until a real product film replaces them. When used, they play through the small HeroVideo player at the end of `js/main.js`:
720 cut on phones (640px and under), 1080 everywhere else, poster only for
reduced motion or no JS. The testimonial loop waits until it is near the
screen before it downloads anything. There is no third-party fallback.

| Files | Used where |
|-------|-----------|
| `hero-720.mp4`, `hero-1080.mp4`, `hero-poster.jpg` | Hero background |
| `testimonial-720.mp4`, `testimonial-1080.mp4`, `testimonial-poster.jpg` | Endorsements section |

Encoded 2026-10 from the original 2084x992 masters (22 MB and 10.6 MB, still
in git history as `video/hero.mp4` and `video/testimonial.mp4`):

```bash
ffmpeg -i hero.mp4 -an -c:v libx264 -preset slow -crf 24 -vf "scale=1280:-2" -pix_fmt yuv420p -profile:v high -movflags +faststart hero-720.mp4
ffmpeg -i hero.mp4 -an -c:v libx264 -preset slow -crf 22 -vf "scale=1920:-2" -pix_fmt yuv420p -profile:v high -movflags +faststart hero-1080.mp4
ffmpeg -i hero.mp4 -frames:v 1 -vf "scale=1920:-2" -q:v 4 hero-poster.jpg
```

Same for `testimonial`. Both loops are generated footage (Higgsfield / Kling);
a real product film is still to come.
