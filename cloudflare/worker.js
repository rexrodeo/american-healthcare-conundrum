/**
 * AHC Data Fund — Cloudflare Worker
 *
 * Creates Stripe Checkout Sessions with custom amounts per dataset.
 * Deployed to Cloudflare Workers (free tier, no server needed).
 *
 * Environment variables — set via: wrangler secret put STRIPE_SECRET_KEY
 *   STRIPE_SECRET_KEY  sk_live_... or sk_test_... (never commit this)
 *   FUND_PAGE_URL      Full URL of the fund page, e.g. https://rexrodeo.github.io/american-healthcare-conundrum/docs/
 *   ALLOWED_ORIGIN     Same as FUND_PAGE_URL origin, e.g. https://rexrodeo.github.io
 *                      (or your custom domain: https://ahcdata.fund)
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

// ------------------------------------------------------------------ handler

export default {
  async fetch(request, env) {
    const origin  = request.headers.get('Origin') || '';
    const allowed = env.ALLOWED_ORIGIN || origin || '*';
    const cors    = corsHeaders(allowed);

    // Preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors });
    }

    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405, headers: cors });
    }

    // Parse body
    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: 'Invalid JSON body.' }, 400, cors);
    }

    const { amount, datasetId } = body;

    // Validate dataset
    const dataset = DATASETS[datasetId];
    if (!dataset) {
      return json({ error: `Unknown datasetId: ${datasetId}` }, 400, cors);
    }

    // Validate amount (cents: $5.00 = 500, $35,000.00 = 3_500_000)
    const amountCents = Math.round(parseFloat(amount) * 100);
    if (isNaN(amountCents) || amountCents < 500 || amountCents > 3_500_000) {
      return json({ error: 'Amount must be between $5 and $35,000.' }, 400, cors);
    }

    const fundPageUrl = env.FUND_PAGE_URL
      || 'https://rexrodeo.github.io/american-healthcare-conundrum/docs/';

    const successUrl = `${fundPageUrl}?funded=${datasetId}&amount=${amount}`;
    const cancelUrl  = fundPageUrl;

    // Build Stripe Checkout Session params (form-encoded)
    const params = new URLSearchParams({
      // ── Payment mode ────────────────────────────────────────────────────
      mode: 'payment',

      // ── Line item ───────────────────────────────────────────────────────
      'line_items[0][price_data][currency]':                      'usd',
      'line_items[0][price_data][product_data][name]':            `AHC Data Fund — ${dataset.name}`,
      'line_items[0][price_data][product_data][description]':
        `Funds The American Healthcare Conundrum's purchase of the ${dataset.name} dataset. ` +
        `All analysis code and aggregate findings are published open-source on GitHub.`,
      'line_items[0][price_data][unit_amount]':                   amountCents.toString(),
      'line_items[0][quantity]':                                  '1',

      // ── Redirect URLs ───────────────────────────────────────────────────
      success_url: successUrl,
      cancel_url:  cancelUrl,

      // ── Custom fields (shown on Stripe Checkout page) ───────────────────
      // Field 1: display name (optional)
      'custom_fields[0][key]':               'display_name',
      'custom_fields[0][label][type]':       'custom',
      'custom_fields[0][label][custom]':     "Name to display on the fund page (or 'Anonymous')",
      'custom_fields[0][type]':              'text',
      'custom_fields[0][optional]':          'true',

      // Field 2: public message (optional, max 140 chars)
      'custom_fields[1][key]':                    'public_message',
      'custom_fields[1][label][type]':            'custom',
      'custom_fields[1][label][custom]':          'Optional public message (140 chars max)',
      'custom_fields[1][type]':                   'text',
      'custom_fields[1][optional]':               'true',
      'custom_fields[1][text][maximum_length]':   '140',

      // ── Metadata ─────────────────────────────────────────────────────────
      'metadata[datasetId]':                       datasetId,
      'metadata[datasetName]':                     dataset.name,
      'metadata[goal]':                            dataset.goal.toString(),
      'payment_intent_data[metadata][datasetId]':  datasetId,
      'payment_intent_data[metadata][datasetName]':dataset.name,
    });

    // ── Call Stripe API ───────────────────────────────────────────────────
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
  },
};
