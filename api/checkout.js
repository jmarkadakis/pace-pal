// Vercel serverless function — Stripe Checkout Session.
// The browser only sends product IDs + quantities; prices live HERE so a
// tampered client can never change the amount charged. Stripe hosts the
// actual payment page, so no card data ever touches this site.
//
// Required env var:  STRIPE_SECRET_KEY  (sk_test_… or sk_live_…)
// Optional env var:  SITE_URL           (e.g. https://mypacepal.com) for redirects
// Optional env var:  STRIPE_SHIPPING_RATE_IDS  comma-separated Stripe shipping
//                    rate ids (shr_…), made in the Stripe dashboard under
//                    Products → Shipping rates. The amounts live in Stripe, so
//                    the owner sets them there, not in code.
// Optional env var:  STRIPE_AUTOMATIC_TAX=1  turns on Stripe Tax. Only set it
//                    after Stripe Tax is activated in the dashboard (origin
//                    address + where you're registered to collect), or every
//                    checkout fails.
//
// Shipping and tax are charged at checkout (owner's call, 2026-09-30). Both
// are switched on by env so the site keeps working before Stripe is set up.
//
// Until STRIPE_SECRET_KEY is set, this returns a friendly 503 and the cart
// shows a "payments not configured yet" note instead of breaking.

import Stripe from "stripe";

// ---- Authoritative price map (USD cents) -------------------
// Prices confirmed from mypacepal.com/shop — both models $465.
const CATALOG = {
  led: { name: "LED Underwater Pace Clock: Light-Emitting Digits", amount: 46500 },
  lcd: { name: "LCD Underwater Pace Clock: Reflects Ambient Light", amount: 46500 },
};

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  let body = req.body;
  if (typeof body === "string") {
    try { body = JSON.parse(body); } catch { return res.status(400).json({ error: "Invalid request" }); }
  }
  const items = Array.isArray(body?.items) ? body.items : [];
  if (!items.length) return res.status(400).json({ error: "Your cart is empty." });

  // Build Stripe line items from the trusted catalog only.
  const line_items = [];
  for (const it of items) {
    const product = CATALOG[it.id];
    const qty = Math.max(1, Math.min(20, parseInt(it.qty, 10) || 1));
    if (!product) return res.status(400).json({ error: `Unknown product: ${it.id}` });
    line_items.push({
      quantity: qty,
      price_data: {
        currency: "usd",
        unit_amount: product.amount,
        // General tangible goods, so Stripe Tax knows what it's taxing.
        product_data: { name: product.name, tax_code: "txcd_99999999" },
        tax_behavior: "exclusive",
      },
    });
  }

  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) {
    console.error("STRIPE_SECRET_KEY not set — checkout disabled.");
    return res.status(503).json({ error: "Online payment isn't configured yet." });
  }

  const origin =
    process.env.SITE_URL ||
    (req.headers.origin ? req.headers.origin : `https://${req.headers.host}`);

  const shipping_options = (process.env.STRIPE_SHIPPING_RATE_IDS || "")
    .split(",")
    .map((id) => id.trim())
    .filter(Boolean)
    .map((shipping_rate) => ({ shipping_rate }));
  const automatic_tax = { enabled: process.env.STRIPE_AUTOMATIC_TAX === "1" };

  try {
    const stripe = new Stripe(key);
    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      line_items,
      billing_address_collection: "required",
      shipping_address_collection: { allowed_countries: ["US", "CA"] },
      phone_number_collection: { enabled: true },
      ...(shipping_options.length ? { shipping_options } : {}),
      automatic_tax,
      success_url: `${origin}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/canceled`,
    });
    return res.status(200).json({ url: session.url });
  } catch (err) {
    console.error("Stripe error:", err);
    return res.status(502).json({ error: "Could not start checkout. Please try again." });
  }
}
