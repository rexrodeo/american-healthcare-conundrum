# Resend setup for ahcdata.fund contact form

One-time setup. ~15 minutes. Safe to do in any order — the form just won't send until both the domain is verified AND the API key is in the Worker's secrets.

## 1. Create Resend account

1. Go to https://resend.com/signup
2. Sign up with vonrexroad@gmail.com (or whichever email you want to manage this from)
3. Free tier is 3,000 emails/month, 100/day — plenty for contact-form traffic

## 2. Add ahcdata.fund as a sending domain

1. In Resend dashboard → **Domains** → **Add Domain**
2. Enter: `ahcdata.fund`
3. Region: **US East (N. Virginia)** — closest to most readers
4. Resend will show you 3–4 DNS records to add. Leave that tab open.

## 3. Add the DNS records in Cloudflare

Go to Cloudflare → **ahcdata.fund** → **DNS** → **Records**. Add each record Resend gave you exactly as shown. They will look roughly like:

| Type | Name                          | Value (example — use Resend's actual values)                      |
| ---- | ----------------------------- | ----------------------------------------------------------------- |
| MX   | `send`                        | `feedback-smtp.us-east-1.amazonses.com` (priority 10)             |
| TXT  | `send`                        | `v=spf1 include:amazonses.com ~all`                               |
| TXT  | `resend._domainkey`           | `p=MIGfMA0GCSqGSIb3D...` (very long — copy the whole value)       |
| TXT  | `_dmarc` *(optional)*         | `v=DMARC1; p=none;`                                               |

**Important:** These are on the `send.` subdomain — **do not touch the existing root-domain SPF** (`v=spf1 include:_spf.mx.cloudflare.net -all`). Cloudflare Email Routing uses that one for inbound to `contact@ahcdata.fund`, and Resend deliberately uses a separate subdomain so there's no conflict.

Set **Proxy status: DNS only** (gray cloud) for every one of these records.

## 4. Verify the domain

Back in Resend → **Domains** → click **Verify DNS Records**. DNS propagation is usually ~2–5 minutes, occasionally up to an hour. All rows should turn green.

## 5. Create an API key

1. Resend dashboard → **API Keys** → **Create API Key**
2. Name: `ahcdata.fund worker`
3. Permission: **Sending access** (not Full Access — scope it down)
4. Domain: `ahcdata.fund`
5. Copy the key (starts with `re_...`). **You won't see it again.**

## 6. Push the key to the Worker

Two options — pick whichever is easier:

**Option A — wrangler CLI (from your Mac):**

```bash
cd /Users/minirex/healthcare/cloudflare
wrangler secret put RESEND_API_KEY
# paste the re_... key when prompted
wrangler deploy
```

**Option B — Cloudflare dashboard:**

1. https://dash.cloudflare.com → **Workers & Pages** → `ahc-data-fund` → **Settings** → **Variables and Secrets**
2. **Add variable** → Type: **Secret**, Name: `RESEND_API_KEY`, Value: `re_...`
3. Save. The Worker redeploys automatically.

## 7. Test

1. Open https://ahcdata.fund/ in an incognito window
2. Click **Get in touch** (the gold banner) or the **Contact** link in the footer
3. Fill the form with a test message and hit send
4. Expect: green success banner, and an email in vonrexroad@gmail.com within 30 seconds
5. Reply to that email — it should go straight to the submitter's address (via Reply-To)

## Troubleshooting

- **Form shows "Could not send"** → Worker logs will say why. `wrangler tail` from `cloudflare/` shows live logs, or check **Workers → ahc-data-fund → Logs** in the dashboard. Most common cause: `RESEND_API_KEY` not set or domain not yet verified.
- **Email lands in spam** → Give it a day for reputation to warm up. DKIM should carry it through; check Gmail "Show original" to confirm `DKIM=PASS` and `SPF=PASS`.
- **"Domain not verified" error from Resend** → Open the Domains page in Resend and hit Verify again. DNS sometimes takes longer to propagate.
