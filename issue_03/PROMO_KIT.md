# Issue #3 Promotion Kit — The 254% Problem: Hospital Pricing

Generated 2026-03-15. Copy-paste each post to the target platform.

---

## Hacker News

**Title:** (paste as the title when submitting)
```
Analysis of 3,193 hospital cost reports: commercial insurers pay 254% of Medicare for identical procedures
```

**URL:** (paste as the link)
```
https://github.com/rexrodeo/american-healthcare-conundrum
```

---

## Reddit: r/healthcare

**Title:**
```
I analyzed 3,193 hospital cost reports from CMS. Commercial insurers pay 254% of Medicare rates for the same procedures. All code is open-source.
```

**Body:**
```
I built an open-source data pipeline that pulls raw CMS HCRIS cost reports and computes cost-to-charge ratios for every hospital in the US.

Key findings from FY2023 data:

- Commercial insurers pay 254% of Medicare rates for identical hospital procedures (RAND Round 5.1)
- A hip replacement costs $29,006 commercially in the US vs. $11,169 international peer average
- For-profit hospitals have a median markup of 4.11x their actual operating costs (the highest of any ownership type)
- 37% of all hospitals charge 3x or more above actual costs

The fix already exists: "commercial reference pricing" caps commercial payments at 200% of Medicare. Montana Medicaid implemented it and saved $47.8 million. Thousands of self-insured employers already use it.

Estimated national savings: $73 billion per year.

All Python code, data sources, and methodology: https://github.com/rexrodeo/american-healthcare-conundrum

Full writeup: https://andrewrexroad.substack.com

Happy to answer questions about the methodology.
```

---

## Reddit: r/healthpolicy

**Title:**
```
Commercial reference pricing could save $73B/year: original analysis of 3,193 CMS hospital cost reports (open-source)
```

**Body:**
```
I published an analysis of the commercial-to-Medicare hospital pricing gap using CMS HCRIS FY2023 data and the RAND Round 5.1 findings.

The core policy question: if Montana Medicaid can cap hospital payments at a percentage of Medicare and save $47.8 million, what happens at national scale?

The math: $528B in commercial hospital spending × 65% addressable × 21.3% price reduction (254% → 200% of Medicare) = $73 billion per year.

The analysis also computes cost-to-charge ratios for 3,193 hospitals by ownership type. For-profit hospitals have a median markup of 4.11x actual operating costs, compared to 2.46x for nonprofits and 2.22x for government hospitals.

The fix mechanism (commercial reference pricing) is already in use:
- Montana Medicaid (state-level)
- Thousands of self-insured employers (ERISA-protected)
- Several state employee health plans

Code and methodology are open-source: https://github.com/rexrodeo/american-healthcare-conundrum

Would welcome discussion on feasibility and political obstacles.
```

---

## Reddit: r/dataisbeautiful

**Title:**
```
[OC] A hip replacement costs $29,006 in the US vs. $11,169 peer average. I analyzed 3,193 hospital cost reports to quantify the markup.
```

**Body:**
```
Data sources: CMS HCRIS HOSP10-REPORTS FY2023, RAND Round 5.1 Hospital Pricing Study (2023), International Federation of Health Plans 2024-2025.

Tools: Python (pandas, matplotlib). Full code: https://github.com/rexrodeo/american-healthcare-conundrum

Key finding: commercial insurers pay 254% of Medicare rates for identical hospital procedures. For-profit hospitals show a median markup of 4.11x above actual operating costs.
```

(Post your best chart — chart1_international_comparison.png or chart2_price_stack.png)

---

## Reddit: r/publichealth

**Title:**
```
US commercial hospital prices are 254% of Medicare: an open-source analysis of 3,193 CMS cost reports
```

**Body:**
```
I've been analyzing federal healthcare data and publishing the findings as an open-source newsletter. The latest issue examines hospital pricing.

The gap is staggering when you look at international comparisons. Same hip replacement:
- US commercial rate: $29,006
- Germany: $14,500
- Australia: $12,000
- Spain: $9,300
- International peer average: $11,169

These aren't different procedures. Same operation, same outcomes. The US price is driven by market consolidation (the top 10 systems now control 25% of beds) and the absence of any reference pricing mechanism for commercial insurance.

A policy fix already exists and is working at smaller scale. Full analysis with reproducible code: https://github.com/rexrodeo/american-healthcare-conundrum

Writeup: https://andrewrexroad.substack.com
```

---

## Substack Notes

```
Commercial insurers pay 254% of Medicare for identical hospital procedures.

I analyzed 3,193 hospital cost reports from CMS. For-profit hospitals mark up 4.11x above actual costs. A hip replacement: $29,006 here, $11,169 peer average.

The fix already exists. Montana proved it works. Estimated savings: $73 billion per year.

Issue #3 of The American Healthcare Conundrum. All code open-source.
```

---

## Gmail Drafts Already Created

✅ Bob Herman (STAT News) — 254% finding, Healthcare Inc. angle
✅ Tara Bannow (STAT News) — nonprofit markup angle
✅ Marshall Allen (ProPublica) — open-source pipeline angle

### Additional Emails to Draft

Request Claude to draft these by saying "draft outreach for [target]":

- [ ] KFF Health News — general health costs desk
- [ ] HFMA newsletter editor — hospital CFO angle
- [ ] Self-Insurance Institute of America — employer angle
- [ ] NASHP — state policy angle (Montana reference pricing)
- [ ] RAND hospital pricing team (Chapin White et al.) — "built on your study"
- [ ] Health policy faculty at Harvard Chan / Johns Hopkins Bloomberg

---

## Posting Order (Recommended)

1. **Substack Notes** — post immediately (warms up the Substack algorithm)
2. **Hacker News** — submit the GitHub link (best time: 9-11am ET weekdays)
3. **r/dataisbeautiful** — post with the best chart image
4. **r/healthcare** and **r/healthpolicy** — stagger by 1-2 hours
5. **r/publichealth** — post same day
6. **Send Gmail drafts** — review and send all outreach emails
7. **GitHub** — create Discussion thread for Issue #3

---

*Generated by the ahc-growth-hacker skill. Run "promote issue N" after each publication.*
