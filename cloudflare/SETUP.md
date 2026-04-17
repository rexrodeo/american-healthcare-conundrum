# AHC Data Fund — Cloudflare Worker Setup

**Time required:** ~20 minutes (most of that is waiting for npm install).

**What this does:** Deploys a tiny serverless function to Cloudflare's free tier that creates Stripe Checkout sessions with custom amounts. When a reader clicks "Fund this dataset," the browser calls this Worker, which creates the Stripe Checkout session and returns the URL to redirect to.

---

## Prerequisites

- Stripe account (you already have one)
- Cloudflare account — free tier is fine (cloudflare.com)
- Node.js installed (check: `node -v`; install from nodejs.org if not)

---

## Step 1 — Install Wrangler (Cloudflare's CLI)

```bash
npm install -g wrangler
```

Verify:
```bash
wrangler --version
```

---

## Step 2 — Log in to Cloudflare

```bash
wrangler login
```

This opens a browser window. Authorize Wrangler. When the browser says "Wrangler is now authorized," return to the terminal.

---

## Step 3 — Get your Stripe secret key

1. Go to https://dashboard.stripe.com/apikeys
2. Copy the **Secret key** — either:
   - `sk_test_...` for testing (use this first — no real charges)
   - `sk_live_...` for production (swap in before Sunday launch)

**Never paste this key into any file.** You'll add it as a secret in the next step.

---

## Step 4 — Deploy the Worker

From the repo root:

```bash
cd cloudflare
wrangler deploy
```

Wrangler will upload `worker.js` and print a URL like:

```
https://ahc-data-fund.YOUR-SUBDOMAIN.workers.dev
```

Copy that URL — you'll need it in Step 6.

---

## Step 5 — Set the Stripe secret key

```bash
wrangler secret put STRIPE_SECRET_KEY
```

Paste your key when prompted. It's stored encrypted in Cloudflare — never in source code.

---

## Step 6 — Wire the Worker URL into the fund page

Open `docs/index.html` and find this line near the top of the `<script>` block:

```javascript
const WORKER_URL = 'YOUR_WORKER_URL_HERE';
```

Replace it with your Worker URL:

```javascript
const WORKER_URL = 'https://ahc-data-fund.YOUR-SUBDOMAIN.workers.dev';
```

Save the file, commit, and push to GitHub. GitHub Pages will update within a minute or two.

---

## Step 7 — Test end-to-end (do this before going live)

1. Make sure `STRIPE_SECRET_KEY` is currently set to your **test** key (`sk_test_...`)
2. Open the fund page on GitHub Pages
3. Click "Fund this dataset" on DS1
4. Select $25 or type an amount
5. Click "Contribute"
6. On the Stripe Checkout page, use test card: **4242 4242 4242 4242**, any future expiry, any CVC
7. Complete payment
8. You should be redirected back to the fund page with the green success banner

If Step 5 fails (Worker URL error in browser console), double-check the URL and that CORS is not blocking. The Worker allows all origins by default.

---

## Step 8 — Go live with real Stripe key

Once the test flow works:

1. Get your **live** secret key from https://dashboard.stripe.com/apikeys
2. Run `wrangler secret put STRIPE_SECRET_KEY` and paste the live key
3. That's it — the Worker immediately uses the new key

---

## Updating the fund page as donations arrive

When Stripe emails you about a payment:

1. Open `docs/index.html`
2. Find the `DATA` object in the `<script>` block
3. Update the matching dataset's `funded` field and push the donor's display name to `sponsors`:

```javascript
ds1: { goal: 1500, funded: 325, sponsors: ['Sarah M.', 'Anonymous'] },
```

4. Save, commit, push — the page updates automatically.

---

## Optional: Update the fund page URL in wrangler.toml

If you add a custom domain (e.g., ahcdata.fund), update `wrangler.toml`:

```toml
[vars]
FUND_PAGE_URL  = "https://ahcdata.fund/"
ALLOWED_ORIGIN = "https://ahcdata.fund"
```

Then redeploy:
```bash
wrangler deploy
```

---

## Troubleshooting

**"WORKER_URL" fetch error in browser console**
- Check the URL is correct and has no trailing slash issues
- CORS should be open by default (ALLOWED_ORIGIN defaults to `*` if not set)

**Stripe error in Worker logs**
- Check `wrangler tail` (streams live Worker logs) for the full error message
- Common issues: wrong API key format, invalid `custom_fields` structure

**Payment goes through but success banner doesn't show**
- Check that `FUND_PAGE_URL` in `wrangler.toml` matches the actual URL of the fund page
- The Worker uses this to construct the `success_url` Stripe redirects to

**Want to see live Worker logs during testing**
```bash
wrangler tail
```
This streams every request in real time.
