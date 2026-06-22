// Vercel serverless function — Stripe Checkout Session.
// The browser only sends product IDs + quantities; prices live HERE so a
// tampered client can never change the amount charged. Stripe hosts the
// actual payment page, so no card data ever touches this site.
//
// Required env var:  STRIPE_SECRET_KEY  (sk_test_… or sk_live_…)
// Optional env var:  SITE_URL           (e.g. https://mypacepal.com) for redirects
//
// Until STRIPE_SECRET_KEY is set, this returns a friendly 503 and the cart
// shows a "payments not configured yet" note instead of breaking.

import Stripe from "stripe";

// ---- Authoritative price map (USD cents) -------------------
// NOTE: LED is a PLACEHOLDER ($795) pending confirmation from the client.
const CATALOG = {
  led: { name: "LED Underwater Pace Clock — Light-Emitting Digits", amount: 79500 },
  lcd: { name: "LCD Underwater Pace Clock — Reflects Ambient Light", amount: 62500 },
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
        product_data: { name: product.name },
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

  try {
    const stripe = new Stripe(key);
    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      line_items,
      billing_address_collection: "required",
      shipping_address_collection: { allowed_countries: ["US", "CA"] },
      phone_number_collection: { enabled: true },
      success_url: `${origin}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/canceled`,
    });
    return res.status(200).json({ url: session.url });
  } catch (err) {
    console.error("Stripe error:", err);
    return res.status(502).json({ error: "Could not start checkout. Please try again." });
  }
}
