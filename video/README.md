# Site videos

Two clips are used on the homepage. Each `<video>` tries the local file first,
then falls back to the Higgsfield CDN (so the site works immediately either way).

| File | Used where | Clip |
|------|-----------|------|
| `video/hero.mp4` | Hero background | High-energy sequence (diver + swimmer + dynamic camera), Kling 3.0 pro |
| `video/hero-underwater.mp4` | Testimonial banner | Calm underwater clip (swimmer glides past) |

To self-host either, download it from the Higgsfield panel and save it at the
exact path above, then commit + push. Until then they stream from the CDN.

The site already works streaming from the CDN. To self-host for permanence
(so the hero never depends on an external CDN):

1. In the Higgsfield panel, open the underwater hero clip and **Download** it.
2. Save it here as exactly: `video/hero-underwater.mp4`
3. Commit + push:

   ```bash
   cd ~/github/clients/pace-pal
   git add video/hero-underwater.mp4
   git commit -m "Self-host hero video"
   git push
   ```

The browser tries the local file first and only falls back to the CDN if it's
missing — so once the file is here, the hero serves entirely from your own site.

> Take A (wired): hf_20260623_010728_040835ef-…mp4
> Take B (alt):   hf_20260623_010728_3d6d32a2-…mp4
