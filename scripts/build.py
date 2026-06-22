#!/usr/bin/env python3
"""
Pace Pal — page generator.

index.html is hand-authored (the rich homepage). Every OTHER page is generated
here from one shared shell so the header, footer and cart drawer never drift.

Edit a page's content in PAGES below, then run:

    python3 scripts/build.py        # or: npm run build:pages
"""
import os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800'
         '&family=Inter:wght@400;500;600&family=Share+Tech+Mono&display=swap" rel="stylesheet">')

HEADER = """<header class="site-header">
  <div class="wrap">
    <nav class="nav">
      <a class="brand" href="index.html"><span class="mark"></span>PACE&nbsp;PAL<sup>&reg;</sup></a>
      <ul class="nav-links">
        <li><a href="led-pace-clock.html">LED Clock</a></li>
        <li><a href="lcd-pace-clock.html">LCD Clock</a></li>
        <li><a href="training.html">Training</a></li>
        <li><a href="testimonials.html">Reviews</a></li>
        <li><a href="about.html">About</a></li>
        <li><a href="contact.html">Contact</a></li>
      </ul>
      <div class="nav-right">
        <a class="btn btn--primary" href="led-pace-clock.html">Shop</a>
        <button class="cart-btn" data-open-cart aria-label="Open cart">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6 6h15l-1.5 9h-12L6 6Z"/><path d="M6 6 5 3H2"/><circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/></svg>
          <span class="cart-count" data-cart-count>0</span>
        </button>
        <button class="nav-toggle" aria-label="Menu"><span></span><span></span><span></span></button>
      </div>
    </nav>
  </div>
</header>"""

FOOTER = """<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="index.html"><span class="mark"></span>PACE&nbsp;PAL<sup>&reg;</sup></a>
        <p>The portable underwater pace clock for swimmers. Designed and milled in the USA.</p>
      </div>
      <div class="footer-col"><h4>Shop</h4>
        <a href="led-pace-clock.html">LED Pace Clock</a>
        <a href="lcd-pace-clock.html">LCD Pace Clock</a>
        <a href="#" data-open-cart>Cart</a>
      </div>
      <div class="footer-col"><h4>Learn</h4>
        <a href="training.html">Training Ideas</a>
        <a href="testimonials.html">Testimonials</a>
        <a href="about.html">About Pace Pal</a>
        <a href="contact.html">Contact</a>
      </div>
      <div class="footer-col"><h4>Support</h4>
        <a href="contact.html">Help &amp; returns</a>
        <a href="privacy-policy.html">Privacy</a>
        <a href="terms.html">Terms</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; <span data-year></span> Pace Pal, LLC. PACE PAL&reg; is a registered trademark. U.S. Patent No. 8,472,285.</span>
      <span class="made">Rebuilt by Stellar Media Collective</span>
    </div>
  </div>
</footer>"""

DRAWER = """<div class="drawer-scrim" data-drawer-scrim></div>
<aside class="drawer" data-drawer aria-label="Shopping cart">
  <div class="drawer-head"><h3>Your cart</h3><button class="drawer-close" data-close-cart aria-label="Close cart">&#10005;</button></div>
  <div class="drawer-items" data-cart-items></div>
  <div class="drawer-foot">
    <div class="row"><span>Subtotal</span><span class="total" data-cart-total>$0</span></div>
    <button class="btn btn--primary btn--block" data-checkout disabled>Checkout</button>
    <p class="fineprint">Secure checkout via Stripe &middot; Shipping &amp; tax at checkout &middot; 60-day refund</p>
  </div>
</aside>"""

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#04060d">
<link rel="canonical" href="https://mypacepal.com/{slug}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="images/og-image.jpg">
<link rel="icon" href="images/favicon.png">
{fonts}
<link rel="stylesheet" href="css/styles.css">
</head>
<body>
{header}
{body}
{footer}
{drawer}
<script src="js/main.js"></script>
</body>
</html>
"""


def buybox(pid, label, price, ghost_href):
    return f"""<div class="buybox" data-buybox style="display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin-top:8px">
      <div class="qty" style="border:1px solid var(--line-strong);border-radius:999px;padding:6px 10px">
        <button data-qty-dec aria-label="Decrease quantity">&minus;</button>
        <input data-qty value="1" inputmode="numeric" style="width:34px;background:none;border:0;color:var(--text);text-align:center;font-family:var(--font-display);font-weight:700" aria-label="Quantity">
        <button data-qty-inc aria-label="Increase quantity">+</button>
      </div>
      <button class="btn btn--primary btn--lg" data-add="{pid}">Add to cart &mdash; {price}</button>
      <a class="btn btn--ghost btn--lg" href="{ghost_href}">{label}</a>
    </div>"""


def product_page(pid, name, tag, price, note, blurb, bullets, specs, screen_class, screen_time, screen_label, depth):
    spec_html = "".join(
        f'<div class="spec"><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in specs
    )
    bullet_html = "".join(f"<li>{b}</li>" for b in bullets)
    other = "lcd-pace-clock.html" if pid == "led" else "led-pace-clock.html"
    other_name = "LCD clock" if pid == "led" else "LED clock"
    return f"""
<section class="page-hero">
  <div class="wrap">
    <div class="breadcrumb reveal"><a href="index.html">Home</a> / Shop / {name}</div>
    <div class="split" style="margin-top:28px;align-items:center">
      <div class="split-media reveal">
        <div class="media-frame wide" style="display:grid;place-items:center;aspect-ratio:4/3">
          <img src="images/{pid}-clock.jpg" alt="{name}">
          <div class="ph"><div>
            <div class="pace-clock" style="width:78%;box-shadow:none">
              <div class="screen"><div class="led-time {screen_class}" style="font-size:2.6rem">{screen_time}</div><div class="led-label">{screen_label}</div></div>
            </div>
            <div class="ph-label" style="margin-top:14px">Product photo &rarr; <code>images/{pid}-clock.jpg</code></div>
          </div></div>
        </div>
      </div>
      <div class="split-copy reveal" data-d="1">
        <span class="eyebrow">{tag}</span>
        <h1>{name}</h1>
        <div class="price" style="font-family:var(--font-display);font-weight:800;font-size:2.4rem;margin:14px 0">{price} <small style="font-size:.9rem;color:var(--text-dim)">USD</small></div>
        <p class="lede">{blurb}</p>
        {buybox(pid, "View " + other_name, price, other)}
        <p class="form-note" style="margin-top:16px">{note} &middot; 60-day, no-questions-asked refund &middot; Ships from the USA.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Why swimmers pick it</span><h2>{name.split(' ')[0]} advantages</h2></div>
    <ul class="checklist reveal" style="max-width:760px;grid-template-columns:1fr 1fr;display:grid;gap:16px 36px">{bullet_html}</ul>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">The numbers</span><h2>Specifications</h2></div>
    <div class="specs reveal">{spec_html}</div>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap">
    <div class="cta-band reveal">
      <h2>Ready to stay on pace?</h2>
      <p class="lede" style="margin:0 auto 26px">Backed by a 60-day full-refund guarantee.</p>
      <div class="btn-row" style="justify-content:center">
        <button class="btn btn--primary btn--lg" data-add="{pid}">Add to cart &mdash; {price}</button>
        <a class="btn btn--ghost btn--lg" href="contact.html">Ask a question</a>
      </div>
    </div>
  </div>
</section>
"""


PAGES = {}

# ---- LED product ----
PAGES["led-pace-clock"] = dict(
    title="LED Underwater Pace Clock | Pace Pal®",
    desc="The LED PACE PAL® underwater pace clock — bold light-emitting digits with three brightness levels, waterproof to 20 ft, rechargeable. Built in the USA.",
    body=product_page(
        "led", "LED Underwater Pace Clock", "Light-Emitting Digits", "$465",
        "Three brightness levels",
        "Glowing, light-emitting digits with three brightness levels — the brightest, most visible PACE PAL®. Built for indoor pools, low light, deep water and the bottom of an Endless Pool®.",
        ["Bold LED digits, 2&frac14;&Prime; tall &mdash; readable ~25 yards away",
         "Three brightness levels for any lighting",
         "Rechargeable: 8+ sessions of 100 minutes per charge",
         "Sleeps to extend battery, wakes instantly",
         "Counts up or down, 0&ndash;99:59",
         "Marine-grade aluminum case, machined acrylic lens"],
        [("Display", "Bold LED &middot; 3 brightness levels"), ("Digit size", "2&frac14;&Prime; &times; 1&frac14;&Prime;"),
         ("Range", "Up/down &middot; 0&ndash;99:59"), ("Waterproof", "To 20 feet"),
         ("Case", "9&frac34;&Prime; &times; 5&frac14;&Prime; &times; 2&frac18;&Prime; aluminum"), ("Weight", "~5.4 lbs"),
         ("Battery", "Rechargeable &middot; 8+ &times; 100 min"), ("Origin", "Designed &amp; milled in the USA")],
        "", "12:34", "Counting up", "20",
    ),
)

# ---- LCD product ----
PAGES["lcd-pace-clock"] = dict(
    title="LCD Underwater Pace Clock | Pace Pal®",
    desc="The LCD PACE PAL® underwater pace clock — high-contrast bold black digits on silver, optimal for outdoor pools and well-lit natatoriums. Waterproof and durable.",
    body=product_page(
        "lcd", "LCD Underwater Pace Clock", "Reflects Ambient Light", "$465",
        "Best for bright, outdoor pools",
        "High-contrast, bold black digits on a silver face that reflect ambient light. The right choice for outdoor pools and bright, well-lit natatoriums where the sun and lights do the work.",
        ["Bold high-contrast black-on-silver digits",
         "Optimal in outdoor pools &amp; well-lit indoor pools",
         "Counts up automatically and restarts",
         "Waterproof and built to last",
         "Patented ballast design for stable positioning",
         "Highly visible, keeps you on pace every lap"],
        [("Display", "High-contrast LCD"), ("Digit size", "Bold, high-visibility digits"),
         ("Range", "Counts up &middot; 0&ndash;99:59"), ("Waterproof", "Submersible"),
         ("Best for", "Outdoor &amp; well-lit pools"), ("Build", "Durable, patented design"),
         ("Battery", "Long battery life"), ("Origin", "Made in the USA")],
        "", "08:15", "Ambient light", "",
    ),
)

# ---- Training ----
PAGES["training"] = dict(
    title="Training Use Ideas | Pace Pal®",
    desc="How to train with PACE PAL® — Ultra-Short Race-Pace Training (USRPT), Endless Pools®, interval send-offs, masters and triathlon. Put the clock where you swim.",
    body="""
<section class="page-hero"><div class="wrap">
  <div class="breadcrumb reveal"><a href="index.html">Home</a> / Training</div>
  <span class="eyebrow reveal" style="margin-top:18px">Train with intent</span>
  <h1 class="reveal" data-d="1">Put the clock<br><span class="gradient-text">where you swim.</span></h1>
  <p class="lede reveal" data-d="2">A pace clock only helps if you can actually see it mid-set. PACE PAL&reg; sits on the bottom of the pool in your line of sight, so you hold pace without breaking rhythm.</p>
</div></section>

<section class="section section--tight"><div class="wrap">
  <div class="grid grid-3">
    <div class="card reveal"><div class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M13 3 4 14h7l-1 7 9-11h-7l1-7Z"/></svg></div><h3>USRPT sets</h3><p>Ultra-Short Race-Pace Training is all about precise send-offs and holding goal pace. Keep the clock under you and nail every interval.</p></div>
    <div class="card reveal" data-d="1"><div class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2 16c2 0 2 1.5 4 1.5S8 16 10 16s2 1.5 4 1.5S16 16 18 16s2 1.5 4 1.5"/><path d="M2 11c2 0 2 1.5 4 1.5S8 11 10 11"/></svg></div><h3>Endless Pools®</h3><p>In a flow-current pool, deck clocks are useless. The suction pad mirrors PACE PAL&reg; to the bottom so your pace is always right in front of you.</p></div>
    <div class="card reveal" data-d="2"><div class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Interval send-offs</h3><p>Count down to your send-off or up through a set. From 0 to 99:59, structure any workout exactly how your coach wrote it.</p></div>
  </div>
</div></section>

<section class="section section--tight"><div class="wrap">
  <div class="split">
    <div class="split-media reveal"><div class="video-frame"><iframe src="https://www.youtube-nocookie.com/embed/Ij_WEGLpwr4" title="Pace Pal training" loading="lazy" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe></div></div>
    <div class="split-copy reveal" data-d="1">
      <span class="eyebrow">Above water too</span>
      <h2>One clock, every workout</h2>
      <p class="lede">PACE PAL&reg; reads perfectly above water, so it pulls double duty for masters practices, triathlon brick sessions, dryland intervals and open-water starts.</p>
      <ul class="checklist">
        <li>Masters &amp; age-group interval training</li>
        <li>Triathlon and open-water pacing</li>
        <li>Dryland circuits and deck timing</li>
      </ul>
      <div class="btn-row" style="margin-top:26px"><a class="btn btn--primary" href="led-pace-clock.html">Shop the LED clock</a></div>
    </div>
  </div>
</div></section>

<section class="section section--tight"><div class="wrap"><div class="cta-band reveal">
  <h2>Train where it counts</h2>
  <p class="lede" style="margin:0 auto 26px">60-day, no-questions-asked refund. Built and milled in the USA.</p>
  <div class="btn-row" style="justify-content:center"><a class="btn btn--primary btn--lg" href="led-pace-clock.html">Shop now</a><a class="btn btn--ghost btn--lg" href="contact.html">Ask a question</a></div>
</div></div></section>
""",
)

# ---- About ----
PAGES["about"] = dict(
    title="About | Pace Pal®",
    desc="PACE PAL® was created by lifelong swimmer Larry Day — a highly visible underwater pace clock, designed and milled in the USA. Read the story behind the clock.",
    body="""
<section class="page-hero"><div class="wrap">
  <div class="breadcrumb reveal"><a href="index.html">Home</a> / About</div>
  <span class="eyebrow reveal" style="margin-top:18px">Our story</span>
  <h1 class="reveal" data-d="1">Built by a swimmer,<br><span class="gradient-text">for swimmers.</span></h1>
</div></section>

<section class="section section--tight"><div class="wrap">
  <div class="split">
    <div class="split-media reveal"><div class="media-frame tall"><img src="images/in-pool-2.jpg" alt="Pace Pal underwater pace clock on the bottom of a pool"><div class="ph"><div><div class="ph-mark">Pace Pal in the water</div><div class="ph-label">images/in-pool-2.jpg</div></div></div></div></div>
    <div class="split-copy reveal" data-d="1">
      <h2>The need that started it</h2>
      <div class="prose">
        <p>PACE PAL&reg; underwater pace clocks were developed by a lifelong swimmer. Staying motivated and holding pace in the pool every day is hard &mdash; especially when the only clock is a deck unit you can barely see on each breath.</p>
        <p>The PACE PAL&reg; underwater pace clock was created to meet that need, with a high-contrast digital screen and highly visible <strong>BOLD DIGITS</strong> that sit right where you swim.</p>
        <blockquote style="border-left:3px solid var(--led-cyan);padding-left:20px;margin:24px 0;color:var(--text);font-style:italic">&ldquo;I&rsquo;ve been a swimmer most of my life and have always wanted a highly visible pace clock on the bottom of the pool or at the end of my lane &mdash; so I created PACE PAL&reg;.&rdquo;<br><span style="font-style:normal;color:var(--led-cyan);font-family:var(--font-led);font-size:.8rem;letter-spacing:.16em;display:block;margin-top:14px">&mdash; LARRY DAY, PRESIDENT</span></blockquote>
      </div>
    </div>
  </div>
</div></section>

<section class="section section--tight"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">What we stand for</span><h2>Made right, made here</h2></div>
  <div class="grid grid-3">
    <div class="card reveal"><div class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 2 4 6v6c0 5 3.4 8.5 8 10 4.6-1.5 8-5 8-10V6l-8-4Z"/></svg></div><h3>Made in the USA</h3><p>The marine-grade aluminum nest and acrylic lens are designed and machined in the United States.</p></div>
    <div class="card reveal" data-d="1"><div class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 6 9 17l-5-5"/></svg></div><h3>60-day guarantee</h3><p>A no-questions-asked, full-refund policy. Train with it, and if it&rsquo;s not for you, send it back.</p></div>
    <div class="card reveal" data-d="2"><div class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3s7 6.5 7 11a7 7 0 1 1-14 0c0-4.5 7-11 7-11Z"/></svg></div><h3>Built to last</h3><p>Robust and durable by design &mdash; and when the clock inside eventually wears out, replace it in the original case.</p></div>
  </div>
</div></section>

<section class="section section--tight"><div class="wrap"><div class="cta-band reveal">
  <h2>Swim with a clock you can actually see</h2>
  <div class="btn-row" style="justify-content:center;margin-top:22px"><a class="btn btn--primary btn--lg" href="led-pace-clock.html">Shop Pace Pal</a><a class="btn btn--ghost btn--lg" href="contact.html">Get in touch</a></div>
</div></div></section>
""",
)

# ---- Contact ----
PAGES["contact"] = dict(
    title="Contact | Pace Pal®",
    desc="Questions about PACE PAL® underwater pace clocks, orders, dealers or returns? Get in touch and we'll be glad to help.",
    body="""
<section class="page-hero"><div class="wrap">
  <div class="breadcrumb reveal"><a href="index.html">Home</a> / Contact</div>
  <span class="eyebrow reveal" style="margin-top:18px">Get in touch</span>
  <h1 class="reveal" data-d="1">Questions? <span class="gradient-text">We&rsquo;re here.</span></h1>
  <p class="lede reveal" data-d="2">Orders, product questions, dealer inquiries or returns &mdash; send a note and we&rsquo;ll get back to you.</p>
</div></section>

<section class="section section--tight"><div class="wrap">
  <form class="form reveal" data-form>
    <input type="text" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
    <div class="field"><label for="name">Name</label><input id="name" name="name" required></div>
    <div class="field"><label for="email">Email</label><input id="email" name="email" type="email" required></div>
    <div class="field"><label for="phone">Phone (optional)</label><input id="phone" name="phone" type="tel"></div>
    <div class="field"><label for="reason">Reason for reaching out</label>
      <select id="reason" name="reason">
        <option>Product question</option>
        <option>Order &amp; shipping</option>
        <option>Returns &amp; 60-day refund</option>
        <option>Dealer / bulk inquiry</option>
        <option>Something else</option>
      </select>
    </div>
    <div class="field"><label for="message">Message</label><textarea id="message" name="message" required></textarea></div>
    <button class="btn btn--primary btn--lg" type="submit">Send message</button>
    <div class="form-status" role="status"></div>
    <p class="form-note">We reply to every message. Your details are only used to respond to you.</p>
  </form>
</div></section>
""",
)

# ---- Testimonials ----
PAGES["testimonials"] = dict(
    title="Testimonials | Pace Pal®",
    desc="Olympic medalists, Olympic coaches and Hall-of-Famers train with PACE PAL®. Read endorsements from Peter Vanderkaay, Rowdy Gaines, Gregg Troy and Karlyn Pipes.",
    body="""
<section class="page-hero"><div class="wrap">
  <div class="breadcrumb reveal"><a href="index.html">Home</a> / Testimonials</div>
  <span class="eyebrow reveal" style="margin-top:18px">Endorsed by champions</span>
  <h1 class="reveal" data-d="1">What the best in<br><span class="gradient-text">swimming say.</span></h1>
  <p class="lede reveal" data-d="2">Olympic medalists, Olympic coaches and Hall-of-Famers train with Pace Pal. Here&rsquo;s why.</p>
</div></section>

<section class="section section--tight"><div class="wrap">
  <div class="split">
    <div class="split-media reveal"><div class="media-frame tall" style="aspect-ratio:3/4;display:grid;place-items:center;background:linear-gradient(165deg,var(--ink-600),var(--ink-800))"><img src="images/vanderkaay.png" alt="Peter Vanderkaay, four-time Olympic medalist and Pace Pal endorser" style="object-fit:contain;padding:24px"><div class="ph"><div><div class="ph-mark">Peter Vanderkaay</div><div class="ph-label">images/vanderkaay.png</div></div></div></div></div>
    <div class="split-copy reveal" data-d="1">
      <span class="eyebrow">Official endorser</span>
      <h2 style="margin:16px 0 8px">Peter Vanderkaay</h2>
      <p style="font-family:var(--font-led);font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--led-cyan)">4&times; Olympic medalist &middot; 2&times; Olympic gold</p>
      <div class="prose" style="margin-top:18px">
        <p>One of the premier distance and middle-distance freestyle specialists in the world. Peter graduated from the University of Michigan after winning five NCAA titles, took gold on the 800 freestyle relay in Athens (2004) and Beijing (2008), and earned individual bronze in the 200m freestyle (2008) and 400m freestyle (London 2012).</p>
        <p style="color:var(--text)"><em>&ldquo;He used our pace clock for six months before endorsing Pace Pal&reg;.&rdquo;</em> &mdash; Larry Day, Founder</p>
      </div>
    </div>
  </div>
</div></section>

<section class="section section--tight"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">In their words</span><h2>From medalists &amp; coaches</h2></div>
  <div class="grid grid-2">
    <div class="card reveal"><p style="font-family:var(--font-display);font-size:1.25rem;line-height:1.5;font-weight:600">&ldquo;Thanks so much for the pace clock&hellip; I just love it and use it every time I am in my Endless Pool.&rdquo;</p><div style="margin-top:20px;font-family:var(--font-led);font-size:.76rem;letter-spacing:.14em;text-transform:uppercase;color:var(--led-cyan)">Rowdy Gaines<br><span style="color:var(--text-dim)">3&times; Olympic gold medalist</span></div></div>
    <div class="card reveal" data-d="1"><p style="font-family:var(--font-display);font-size:1.25rem;line-height:1.5;font-weight:600">&ldquo;Pace Pal clocks have been a real plus for our program. They&rsquo;ve allowed our athletes to be more aware of their timing in practice &mdash; making sessions more reliable and visible to them.&rdquo;</p><div style="margin-top:20px;font-family:var(--font-led);font-size:.76rem;letter-spacing:.14em;text-transform:uppercase;color:var(--led-cyan)">Gregg Troy<br><span style="color:var(--text-dim)">2012 USA Olympic coach</span></div></div>
    <div class="card reveal"><p style="font-family:var(--font-display);font-size:1.25rem;line-height:1.5;font-weight:600">&ldquo;Pace Pal lets our coaches set up distance sets effectively, so they can focus more on technique and less on being human pace clocks. It&rsquo;s like having another coach on deck.&rdquo;</p><div style="margin-top:20px;font-family:var(--font-led);font-size:.76rem;letter-spacing:.14em;text-transform:uppercase;color:var(--led-cyan)">USA Swimming coaching staff</div></div>
    <div class="card reveal" data-d="1"><p style="font-family:var(--font-display);font-size:1.25rem;line-height:1.5;font-weight:600">&ldquo;LOVE my new Pace Pal&reg; digital pace-clock that sits right at the end of my lane&hellip; or even underwater! Larry Day, you are a genius.&rdquo;</p><div style="margin-top:20px;font-family:var(--font-led);font-size:.76rem;letter-spacing:.14em;text-transform:uppercase;color:var(--led-cyan)">Karlyn Pipes<br><span style="color:var(--text-dim)">Int&rsquo;l Swimming Hall of Fame</span></div></div>
  </div>
</div></section>

<section class="section section--tight"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">Also endorsed by</span><h2>Trusted across the sport</h2></div>
  <div class="grid grid-3">
    <div class="card center reveal"><h3>Peter Vanderkaay</h3><p class="muted">4&times; Olympic medalist</p></div>
    <div class="card center reveal" data-d="1"><h3>Gregg Troy</h3><p class="muted">2012 USA Olympic head coach</p></div>
    <div class="card center reveal" data-d="2"><h3>Mike Bottom</h3><p class="muted">University of Michigan head coach</p></div>
  </div>
</div></section>

<section class="section section--tight"><div class="wrap"><div class="cta-band reveal">
  <h2>Train with the clock they trust</h2>
  <p class="lede" style="margin:0 auto 26px">60-day, no-questions-asked refund. Built and milled in the USA.</p>
  <div class="btn-row" style="justify-content:center"><a class="btn btn--primary btn--lg" href="led-pace-clock.html">Shop Pace Pal</a><a class="btn btn--ghost btn--lg" href="training.html">Training ideas</a></div>
</div></div></section>
""",
)

# ---- Stripe success ----
PAGES["success"] = dict(
    title="Order confirmed | Pace Pal®",
    desc="Thank you for your Pace Pal order.",
    body="""
<section class="page-hero" style="padding-bottom:90px"><div class="wrap center">
  <div class="reveal in" style="max-width:620px;margin:40px auto 0">
    <div class="ico" style="width:64px;height:64px;margin:0 auto 24px;border-radius:16px;background:rgba(57,255,136,.12);border:1px solid rgba(57,255,136,.3);color:var(--led-green);display:grid;place-items:center"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg></div>
    <h1>You&rsquo;re on pace.</h1>
    <p class="lede" style="margin:18px auto 30px">Thanks for your order &mdash; a confirmation is on its way to your email. We&rsquo;ll be in touch with shipping details shortly.</p>
    <div class="btn-row" style="justify-content:center"><a class="btn btn--primary btn--lg" href="index.html">Back to home</a><a class="btn btn--ghost btn--lg" href="training.html">Training ideas</a></div>
  </div>
</div></section>
<script>try{localStorage.removeItem('pacepal_cart_v1')}catch(e){}</script>
""",
)

# ---- Stripe canceled ----
PAGES["canceled"] = dict(
    title="Checkout canceled | Pace Pal®",
    desc="Your checkout was canceled.",
    body="""
<section class="page-hero" style="padding-bottom:90px"><div class="wrap center">
  <div class="reveal in" style="max-width:620px;margin:40px auto 0">
    <h1>Checkout canceled</h1>
    <p class="lede" style="margin:18px auto 30px">No charge was made &mdash; your cart is still saved. Pick up where you left off whenever you&rsquo;re ready.</p>
    <div class="btn-row" style="justify-content:center"><button class="btn btn--primary btn--lg" data-open-cart>Open cart</button><a class="btn btn--ghost btn--lg" href="index.html">Back to home</a></div>
  </div>
</div></section>
""",
)

# ---- Legal ----
PAGES["privacy-policy"] = dict(
    title="Privacy Policy | Pace Pal®",
    desc="How Pace Pal handles your information.",
    body="""
<section class="page-hero"><div class="wrap">
  <div class="breadcrumb reveal"><a href="index.html">Home</a> / Privacy</div>
  <h1 class="reveal" data-d="1">Privacy Policy</h1>
</div></section>
<section class="section section--tight"><div class="wrap"><div class="prose reveal">
  <p>This policy explains what information Pace Pal, LLC collects and how it is used. This is a starter template &mdash; have it reviewed before publishing.</p>
  <h2>Information we collect</h2>
  <p>When you contact us or place an order we collect the details you provide: name, email, phone, shipping address and order contents. Payments are processed securely by Stripe; we never see or store your full card details.</p>
  <h2>How we use it</h2>
  <ul><li>To respond to your inquiries</li><li>To process and ship your orders</li><li>To provide support and handle returns under our 60-day policy</li></ul>
  <h2>Sharing</h2>
  <p>We share information only with the providers needed to run the store (such as Stripe for payments and shipping carriers). We do not sell your personal information.</p>
  <h2>Contact</h2>
  <p>Questions about privacy? <a href="contact.html">Get in touch.</a></p>
</div></div></section>
""",
)

PAGES["terms"] = dict(
    title="Terms &amp; Returns | Pace Pal®",
    desc="Pace Pal terms of sale and 60-day refund policy.",
    body="""
<section class="page-hero"><div class="wrap">
  <div class="breadcrumb reveal"><a href="index.html">Home</a> / Terms</div>
  <h1 class="reveal" data-d="1">Terms &amp; Returns</h1>
</div></section>
<section class="section section--tight"><div class="wrap"><div class="prose reveal">
  <p>These terms govern purchases from mypacepal.com. This is a starter template &mdash; have it reviewed before publishing.</p>
  <h2>60-day refund</h2>
  <p>PACE PAL&reg; comes with a 60-day, no-questions-asked, full-refund policy. If you&rsquo;re not satisfied, contact us within 60 days of delivery to arrange a return for a full refund.</p>
  <h2>Warranty &amp; replacement</h2>
  <p>The case is built to last. When the clock inside eventually wears out, it can be replaced in the original case.</p>
  <h2>Trademarks &amp; patents</h2>
  <p>PACE PAL&reg; is a registered trademark of Pace Pal, LLC. Protected under U.S. Patent No. 8,472,285 and related patents.</p>
  <h2>Contact</h2>
  <p>Questions about an order or return? <a href="contact.html">Reach out here.</a></p>
</div></div></section>
""",
)


def build():
    n = 0
    for slug, page in PAGES.items():
        html = SHELL.format(
            title=page["title"], desc=page["desc"], slug=slug,
            fonts=FONTS, header=HEADER, footer=FOOTER, drawer=DRAWER, body=page["body"],
        )
        (ROOT / f"{slug}.html").write_text(html, encoding="utf-8")
        print(f"  wrote {slug}.html")
        n += 1
    print(f"Done — {n} pages generated. (index.html is hand-authored; not touched.)")


if __name__ == "__main__":
    build()
