/* ============================================================
   PACE PAL® — site behaviour
   nav · reveal-on-scroll · live LED pace clock · cart + Stripe
   No framework, no build step.
   ============================================================ */
(function () {
  "use strict";

  /* ---- Product catalog (display side) ----------------------
     Server (api/checkout.js) keeps its own authoritative price
     map — never trust the client for Stripe amounts.
     NOTE: LED price is a PLACEHOLDER pending confirmation. ---- */
  const PRODUCTS = {
    led: {
      id: "led",
      name: "LED Underwater Pace Clock",
      tag: "Light-Emitting Digits",
      price: 795,            // ← PLACEHOLDER — confirm real LED price
      placeholderPrice: true,
      img: "images/led-clock.jpg",
      url: "led-pace-clock.html",
    },
    lcd: {
      id: "lcd",
      name: "LCD Underwater Pace Clock",
      tag: "Reflects Ambient Light",
      price: 625,            // confirmed from mypacepal.com
      placeholderPrice: false,
      img: "images/lcd-clock.jpg",
      url: "lcd-pace-clock.html",
    },
  };
  const fmt = (n) => "$" + n.toLocaleString("en-US");

  /* ---- Header shadow on scroll ----------------------------- */
  const header = document.querySelector(".site-header");
  const onScroll = () => header && header.classList.toggle("scrolled", window.scrollY > 8);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---- Mobile nav ------------------------------------------ */
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", () => links.classList.toggle("open"));
    links.querySelectorAll("a").forEach((a) =>
      a.addEventListener("click", () => links.classList.remove("open"))
    );
  }

  /* ---- Reveal on scroll ------------------------------------ */
  const io = "IntersectionObserver" in window
    ? new IntersectionObserver((entries) => {
        entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
      }, { threshold: 0.12 })
    : null;
  document.querySelectorAll(".reveal").forEach((el) => io ? io.observe(el) : el.classList.add("in"));

  /* ---- Graceful image placeholders ------------------------- */
  // Add .loaded when a real photo decodes; CSS hides the placeholder.
  document.querySelectorAll(".media-frame img, .pc-media img, .product-card img").forEach((img) => {
    const done = () => { if (img.naturalWidth > 1) { img.classList.add("loaded"); img.closest(".media-frame,.pc-media")?.classList.add("has-img"); } };
    if (img.complete) done();
    img.addEventListener("load", done);
    img.addEventListener("error", () => { img.style.display = "none"; });
  });

  /* ---- Live LED pace clock (hero centerpiece) -------------- */
  const clock = document.querySelector("[data-pace-clock]");
  if (clock) {
    const out = clock.querySelector(".led-time");
    const label = clock.querySelector(".led-label");
    const dots = clock.querySelectorAll(".clock-meta .dot");
    let mode = "up";          // up | down | interval
    let t = 0;                // seconds shown
    const INTERVAL_TARGET = 90; // 1:30 send-off
    let last = performance.now();

    const pad = (n) => String(n).padStart(2, "0");
    const paint = () => {
      const m = Math.floor(Math.abs(t) / 60), s = Math.abs(t) % 60;
      out.innerHTML = `${pad(m)}<span class="sep">:</span>${pad(s)}`;
      const lit = mode === "interval" ? (INTERVAL_TARGET - (t % INTERVAL_TARGET)) % INTERVAL_TARGET : t;
      dots.forEach((d, i) => d.classList.toggle("on", (Math.floor(lit) % 5) > i || (Math.floor(lit) % 5) === 0 && i < 5));
    };
    const tick = (now) => {
      if (now - last >= 1000) {
        last = now;
        if (mode === "up") t++;
        else if (mode === "down") t = t <= 0 ? 99 * 60 + 59 : t - 1;
        else t = (t + 1) % INTERVAL_TARGET; // interval loops at send-off
        paint();
      }
      requestAnimationFrame(tick);
    };
    paint();
    requestAnimationFrame(tick);

    clock.querySelectorAll(".clock-controls button").forEach((b) => {
      b.addEventListener("click", () => {
        clock.querySelectorAll(".clock-controls button").forEach((x) => x.classList.remove("active"));
        b.classList.add("active");
        mode = b.dataset.mode;
        t = mode === "down" ? 10 * 60 : 0;
        if (label) label.textContent = mode === "interval" ? "Interval · 1:30 send-off" : mode === "down" ? "Counting down" : "Counting up · 0–99:59";
        paint();
      });
    });
  }

  /* ===========================================================
     CART  (localStorage-backed, Stripe Checkout for payment)
     =========================================================== */
  const KEY = "pacepal_cart_v1";
  let cart = [];
  try { cart = JSON.parse(localStorage.getItem(KEY)) || []; } catch (_) { cart = []; }
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(cart)); } catch (_) {} };

  const els = {
    count: document.querySelector("[data-cart-count]"),
    drawer: document.querySelector("[data-drawer]"),
    scrim: document.querySelector("[data-drawer-scrim]"),
    items: document.querySelector("[data-cart-items]"),
    total: document.querySelector("[data-cart-total]"),
    checkout: document.querySelector("[data-checkout]"),
  };

  const totalQty = () => cart.reduce((n, l) => n + l.qty, 0);
  const totalUsd = () => cart.reduce((n, l) => n + (PRODUCTS[l.id]?.price || 0) * l.qty, 0);

  function syncCount() {
    if (!els.count) return;
    const q = totalQty();
    els.count.textContent = q;
    els.count.classList.toggle("show", q > 0);
  }

  function renderCart() {
    if (!els.items) return;
    if (!cart.length) {
      els.items.innerHTML = `<div class="drawer-empty"><p>Your cart is empty.</p><p style="margin-top:8px;font-size:.85rem">Pick a pace clock to get started.</p></div>`;
    } else {
      els.items.innerHTML = cart.map((l) => {
        const p = PRODUCTS[l.id]; if (!p) return "";
        return `<div class="cart-line" data-line="${l.id}">
          <div class="thumb">PACE&nbsp;PAL</div>
          <div>
            <div class="nm">${p.name}</div>
            <div class="pr">${fmt(p.price)}${p.placeholderPrice ? " *" : ""}</div>
            <div class="qty">
              <button data-dec aria-label="Decrease">−</button>
              <span>${l.qty}</span>
              <button data-inc aria-label="Increase">+</button>
              <button class="rm" data-rm style="margin-left:10px">Remove</button>
            </div>
          </div>
          <div class="pr">${fmt(p.price * l.qty)}</div>
        </div>`;
      }).join("");
    }
    if (els.total) els.total.textContent = fmt(totalUsd());
    if (els.checkout) els.checkout.disabled = !cart.length;
    syncCount();
  }

  function addToCart(id, qty = 1) {
    if (!PRODUCTS[id]) return;
    const line = cart.find((l) => l.id === id);
    if (line) line.qty += qty; else cart.push({ id, qty });
    save(); renderCart(); openDrawer();
  }
  function changeQty(id, delta) {
    const line = cart.find((l) => l.id === id); if (!line) return;
    line.qty += delta;
    if (line.qty <= 0) cart = cart.filter((l) => l.id !== id);
    save(); renderCart();
  }
  function removeLine(id) { cart = cart.filter((l) => l.id !== id); save(); renderCart(); }

  function openDrawer() { els.drawer?.classList.add("open"); els.scrim?.classList.add("open"); }
  function closeDrawer() { els.drawer?.classList.remove("open"); els.scrim?.classList.remove("open"); }

  // Wire add-to-cart buttons anywhere on the page
  document.querySelectorAll("[data-add]").forEach((b) => {
    b.addEventListener("click", () => {
      const qtyInput = b.closest("[data-buybox]")?.querySelector("[data-qty]");
      addToCart(b.dataset.add, qtyInput ? Math.max(1, parseInt(qtyInput.value, 10) || 1) : 1);
    });
  });
  document.querySelectorAll("[data-open-cart]").forEach((b) => b.addEventListener("click", (e) => { e.preventDefault(); renderCart(); openDrawer(); }));
  document.querySelectorAll("[data-close-cart]").forEach((b) => b.addEventListener("click", closeDrawer));
  els.scrim?.addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeDrawer(); });

  // Quantity steppers inside the drawer (event delegation)
  els.items?.addEventListener("click", (e) => {
    const line = e.target.closest("[data-line]"); if (!line) return;
    const id = line.dataset.line;
    if (e.target.closest("[data-inc]")) changeQty(id, 1);
    else if (e.target.closest("[data-dec]")) changeQty(id, -1);
    else if (e.target.closest("[data-rm]")) removeLine(id);
  });

  // Buybox quantity steppers (product pages)
  document.querySelectorAll("[data-buybox]").forEach((box) => {
    const input = box.querySelector("[data-qty]");
    box.querySelector("[data-qty-dec]")?.addEventListener("click", () => { input.value = Math.max(1, (parseInt(input.value, 10) || 1) - 1); });
    box.querySelector("[data-qty-inc]")?.addEventListener("click", () => { input.value = (parseInt(input.value, 10) || 1) + 1; });
  });

  /* ---- Stripe Checkout ------------------------------------- */
  els.checkout?.addEventListener("click", async () => {
    if (!cart.length) return;
    const btn = els.checkout;
    const original = btn.textContent;
    btn.disabled = true; btn.textContent = "Redirecting…";
    try {
      const res = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: cart.map((l) => ({ id: l.id, qty: l.qty })) }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.url) { window.location.href = data.url; return; }
      throw new Error(data.error || "Checkout is not available yet.");
    } catch (err) {
      btn.textContent = original; btn.disabled = false;
      let note = els.drawer?.querySelector(".checkout-note");
      if (!note) { note = document.createElement("p"); note.className = "fineprint checkout-note"; note.style.color = "var(--led-red)"; els.drawer?.querySelector(".drawer-foot")?.appendChild(note); }
      note.textContent = err.message + " (Set STRIPE_SECRET_KEY in Vercel to enable payments.)";
    }
  });

  renderCart();

  /* ---- Contact / inquiry form ------------------------------ */
  document.querySelectorAll("[data-form]").forEach((form) => {
    const status = form.querySelector(".form-status");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = form.querySelector('[type="submit"]');
      const label = btn?.textContent;
      if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
      if (status) status.className = "form-status";
      const payload = Object.fromEntries(new FormData(form).entries());
      try {
        const res = await fetch("/api/contact", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        if (!res.ok) throw new Error();
        form.reset();
        if (status) { status.className = "form-status ok"; status.textContent = "Got it — thanks. We'll be in touch shortly."; }
      } catch (_) {
        if (status) { status.className = "form-status err"; status.textContent = "Something went wrong. Email info@stellarmediacollective.com and we'll sort it out."; }
      } finally {
        if (btn) { btn.disabled = false; btn.textContent = label; }
      }
    });
  });

  /* ---- Footer year ----------------------------------------- */
  document.querySelectorAll("[data-year]").forEach((el) => (el.textContent = new Date().getFullYear()));
})();
