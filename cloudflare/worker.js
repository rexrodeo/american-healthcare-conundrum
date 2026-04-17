/**
 * AHC Data Fund — Cloudflare Worker
 *
 * Two endpoints:
 *   POST /          → Create a Stripe Checkout Session (donations)
 *   POST /contact   → Send a contact-form message via Resend
 *
 * Environment — set via wrangler:
 *   STRIPE_SECRET_KEY   wrangler secret put STRIPE_SECRET_KEY
 *   RESEND_API_KEY      wrangler secret put RESEND_API_KEY
 *   FUND_PAGE_URL       vars in wrangler.toml
 *   ALLOWED_ORIGIN      vars in wrangler.toml
 *   CONTACT_TO          vars in wrangler.toml   (e.g. contact@ahcdata.fund)
 *   CONTACT_FROM        vars in wrangler.toml   (e.g. "AHC Contact Form <noreply@ahcdata.fund>")
 */

const DATASETS = {
  ds1: { name: 'CMS Medicare Claims (5% Sample)',           goal: 1500  },
  ds2: { name: 'Colorado All-Payer Claims Database',         goal: 2000  },
  ds3: { name: 'Hospital Discharge Data (CA + NY)',           goal: 1000  },
  ds4: { name: 'Hospital Price Transparency (Full National)', goal: 3500  },
  ds5: { name: 'Legal Research (Case Law + Antitrust)',       goal: 1200  },
  ds6: { name: 'CMS Full Medicare Claims (65M Patients)',     goal: 35000 },
};

// ------------------------------------------------------------------ helpers

function corsHeaders(allowedOrigin) {
  return {
    'Access-Control-Allow-Origin':  allowedOrigin || '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

function json(data, status, cors) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...cors },
  });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ------------------------------------------------------------------ Stripe

async function handleStripeCheckout(body, env, cors) {
  const { amount, datasetId } = body;

  const dataset = DATASETS[datasetId];
  if (!dataset) {
    return json({ error: `Unknown datasetId: ${datasetId}` }, 400, cors);
  }

  const amountCents = Math.round(parseFloat(amount) * 100);
  if (isNaN(amountCents) || amountCents < 500 || amountCents > 3_500_000) {
    return json({ error: 'Amount must be between $5 and $35,000.' }, 400, cors);
  }

  const fundPageUrl = env.FUND_PAGE_URL || 'https://ahcdata.fund/';

  const successUrl = `${fundPageUrl}?funded=${datasetId}&amount=${amount}`;
  const cancelUrl  = fundPageUrl;

  const params = new URLSearchParams({
    mode: 'payment',

    'line_items[0][price_data][currency]':                      'usd',
    'line_items[0][price_data][product_data][name]':            `AHC Data Fund — ${dataset.name}`,
    'line_items[0][price_data][product_data][description]':
      `Funds The American Healthcare Conundrum's purchase of the ${dataset.name} dataset. ` +
      `All analysis code and aggregate findings are published open-source on GitHub.`,
    'line_items[0][price_data][unit_amount]':                   amountCents.toString(),
    'line_items[0][quantity]':                                  '1',

    success_url: successUrl,
    cancel_url:  cancelUrl,

    'custom_fields[0][key]':               'display_name',
    'custom_fields[0][label][type]':       'custom',
    'custom_fields[0][label][custom]':     "Name to display on the fund page (or 'Anonymous')",
    'custom_fields[0][type]':              'text',
    'custom_fields[0][optional]':          'true',

    'custom_fields[1][key]':                    'public_message',
    'custom_fields[1][label][type]':            'custom',
    'custom_fields[1][label][custom]':          'Optional public message (140 chars max)',
    'custom_fields[1][type]':                   'text',
    'custom_fields[1][optional]':               'true',
    'custom_fields[1][text][maximum_length]':   '140',

    'metadata[datasetId]':                       datasetId,
    'metadata[datasetName]':                     dataset.name,
    'metadata[goal]':                            dataset.goal.toString(),
    'payment_intent_data[metadata][datasetId]':  datasetId,
    'payment_intent_data[metadata][datasetName]':dataset.name,
  });

  const stripeRes = await fetch('https://api.stripe.com/v1/checkout/sessions', {
    method: 'POST',
    headers: {
      'Authorization':  `Bearer ${env.STRIPE_SECRET_KEY}`,
      'Content-Type':   'application/x-www-form-urlencoded',
      'Stripe-Version': '2023-10-16',
    },
    body: params.toString(),
  });

  if (!stripeRes.ok) {
    const errText = await stripeRes.text();
    console.error('Stripe API error:', errText);
    return json({ error: 'Payment initialization failed. Please try again.' }, 502, cors);
  }

  const session = await stripeRes.json();
  return json({ url: session.url }, 200, cors);
}

// ------------------------------------------------------------------ Contact

async function handleContact(body, env, request, cors) {
  const { name, email, subject, message, website } = body || {};

  // Honeypot: real humans leave `website` blank. Silently succeed so bots don't retry.
  if (website && String(website).trim() !== '') {
    return json({ ok: true }, 200, cors);
  }

  const nm  = (name    || '').toString().trim();
  const em  = (email   || '').toString().trim();
  const sb  = (subject || '').toString().trim();
  const msg = (message || '').toString().trim();

  if (!nm || !em || !msg) {
    return json({ error: 'Name, email, and message are all required.' }, 400, cors);
  }
  if (nm.length > 80 || em.length > 120 || sb.length > 120 || msg.length > 2000) {
    return json({ error: 'Field length exceeded.' }, 400, cors);
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em)) {
    return json({ error: 'Please enter a valid email address.' }, 400, cors);
  }

  const to       = env.CONTACT_TO   || 'contact@ahcdata.fund';
  const fromAddr = env.CONTACT_FROM || 'AHC Contact Form <noreply@ahcdata.fund>';

  const ip   = request.headers.get('CF-Connecting-IP') || 'unknown';
  const ua   = request.headers.get('User-Agent')       || 'unknown';
  const ref  = request.headers.get('Referer')          || 'unknown';
  const when = new Date().toISOString();
  const emailSubject = `[ahcdata.fund] ${sb || 'Contact form'} — from ${nm}`;

  const textBody = [
    `Name:    ${nm}`,
    `Email:   ${em}`,
    `Subject: ${sb || '(none)'}`,
    ``,
    msg,
    ``,
    `----`,
    `Sent via ahcdata.fund contact form`,
    `Time:    ${when}`,
    `IP:      ${ip}`,
    `UA:      ${ua}`,
    `Referer: ${ref}`,
  ].join('\n');

  const htmlBody = `
    <div style="font-family:-apple-system,system-ui,sans-serif;line-height:1.5;color:#1A1F2E;">
      <h2 style="margin:0 0 12px;font-size:16px;color:#0E8A72;">New contact form message</h2>
      <table style="border-collapse:collapse;font-size:13px;margin-bottom:16px;">
        <tr><td style="padding:4px 12px 4px 0;color:#6b7280;"><b>Name</b></td><td>${escapeHtml(nm)}</td></tr>
        <tr><td style="padding:4px 12px 4px 0;color:#6b7280;"><b>Email</b></td><td><a href="mailto:${escapeHtml(em)}">${escapeHtml(em)}</a></td></tr>
        <tr><td style="padding:4px 12px 4px 0;color:#6b7280;"><b>Subject</b></td><td>${escapeHtml(sb || '(none)')}</td></tr>
      </table>
      <div style="background:#F8F8F6;border-left:3px solid #0E8A72;padding:14px 16px;white-space:pre-wrap;font-size:14px;">${escapeHtml(msg)}</div>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0 12px;">
      <div style="font-size:11px;color:#9CA3AF;font-family:ui-monospace,monospace;">
        ${escapeHtml(when)} · ${escapeHtml(ip)}<br>
        UA: ${escapeHtml(ua)}<br>
        Ref: ${escapeHtml(ref)}
      </div>
    </div>
  `;

  const resendRes = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type':  'application/json',
    },
    body: JSON.stringify({
      from:     fromAddr,
      to:       [to],
      reply_to: em,
      subject:  emailSubject,
      text:     textBody,
      html:     htmlBody,
    }),
  });

  if (!resendRes.ok) {
    const errText = await resendRes.text();
    console.error('Resend API error:', resendRes.status, errText);
    return json({ error: 'Could not send message. Please try again in a moment.' }, 502, cors);
  }

  return json({ ok: true }, 200, cors);
}

// ------------------------------------------------------------------ router

export default {
  async fetch(request, env) {
    const origin  = request.headers.get('Origin') || '';
    const allowed = env.ALLOWED_ORIGIN || origin || '*';
    const cors    = corsHeaders(allowed);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors });
    }

    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405, headers: cors });
    }

    const url      = new URL(request.url);
    const pathname = url.pathname.replace(/\/+$/, '') || '/';

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: 'Invalid JSON body.' }, 400, cors);
    }

    if (pathname === '/contact') {
      return handleContact(body, env, request, cors);
    }

    // Default: Stripe checkout (backward-compatible with existing frontend calling POST /)
    return handleStripeCheckout(body, env, cors);
  },
};
