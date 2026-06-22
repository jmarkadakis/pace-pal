// Vercel serverless function — contact / dealer / inquiry delivery via Resend.
// Mirrors the Stellar Media Collective contact pattern used across client sites
// (no CRM/DB — email only). Requires env var RESEND_API_KEY.
//
// WHERE LEADS GO:
//   TO_EMAIL receives every submission. It's set to the Stellar inbox so the
//   form works the moment it deploys. Change it to route to Pace Pal directly,
//   and update FROM once mypacepal.com is a verified Resend sending domain.

import { Resend } from "resend";

const TO_EMAIL = "info@stellarmediacollective.com";
const FROM = "Pace Pal <leads@stellarmediacollective.com>";

const fieldLabels = {
  name: "Name",
  email: "Email",
  phone: "Phone",
  reason: "Reason for Reaching Out",
  message: "Message",
};

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  let body = req.body;
  if (typeof body === "string") {
    try { body = JSON.parse(body); } catch { return res.status(400).json({ error: "Invalid JSON" }); }
  }
  body = body || {};

  // Honeypot — silently accept bot submissions without sending.
  if (typeof body.botcheck === "string" && body.botcheck.trim()) {
    return res.status(200).json({ ok: true });
  }

  const isSubscribe = body.intent === "subscribe";
  const required = isSubscribe ? ["email"] : ["name", "email", "message"];
  for (const field of required) {
    if (typeof body[field] !== "string" || !body[field].trim()) {
      return res.status(400).json({ error: `Missing required field: ${field}` });
    }
  }

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    console.error("RESEND_API_KEY is not set — submission not delivered:", body);
    return res.status(503).json({ error: "Email delivery is not configured" });
  }

  const subject = isSubscribe
    ? `Pace Pal — new subscriber: ${body.email.trim()}`
    : `Pace Pal — ${(body.reason || "message").trim()} from ${body.name.trim()}`;

  const lines = isSubscribe
    ? `New mailing-list signup from mypacepal.com\n\nEmail: ${body.email.trim()}\n`
    : "New inquiry from mypacepal.com\n\n" +
      Object.entries(fieldLabels)
        .filter(([key]) => typeof body[key] === "string" && body[key].trim())
        .map(([key, label]) => `${label}: ${body[key].trim()}`)
        .join("\n");

  try {
    const resend = new Resend(apiKey);
    const { error } = await resend.emails.send({
      from: FROM,
      to: [TO_EMAIL],
      reply_to: typeof body.email === "string" ? body.email.trim() : undefined,
      subject,
      text: lines,
    });
    if (error) { console.error("Resend error:", error); return res.status(502).json({ error: "Email delivery failed" }); }
    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error("Unexpected error sending email:", err);
    return res.status(500).json({ error: "Unexpected server error" });
  }
}
