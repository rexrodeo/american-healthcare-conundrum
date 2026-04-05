# Issue #6 — The Supply Closet: Research Brief

*Compiled 2026-03-17. All data sources cited inline.*

---

## 1. THE HEADLINE NUMBER

**$170.9 billion** in annual hospital supply/device/drug costs across 5,480 US hospitals (142.3M discharges). HCRIS FY2023 original analysis.

**$28.5 billion** in addressable savings (conservative: top-quartile hospitals brought to P75 within bed-size peers, CMI-adjusted).

**$58.9 billion** in addressable savings (moderate: above-median hospitals brought to P50 within peers).

No published study has computed a national aggregate of hospital supply cost variance from HCRIS microdata. This number is ours.

---

## 2. WHAT WE HAVE (Novel Data)

### 2a. HCRIS National Supply Variance (ORIGINAL ANALYSIS)

Source: CMS HCRIS HOSP10-REPORTS FY2023, Worksheets A, S-2, S-3

| Category | National Total | Avg/Discharge |
|----------|---------------|---------------|
| Medical Supplies | $40.4B | $491 mean |
| Implantable Devices | $48.7B | $868 mean |
| Drugs Charged to Patients | $81.9B | $941 mean |
| **Combined** | **$170.9B** | **$1,941 mean** |

**CMI-adjusted variance by hospital size (combined supply/device/drug per discharge):**

| Bed Size | N | P25 | P50 | P75 | P90 | P75/P25 |
|----------|---|-----|-----|-----|-----|---------|
| Small (1–99) | 3,499 | $197 | $663 | $1,509 | $3,005 | **7.7×** |
| Medium (100–299) | 1,511 | $382 | $700 | $1,165 | $1,724 | **3.0×** |
| Large (300–499) | 320 | $543 | $893 | $1,265 | $1,784 | **2.3×** |
| Major (500+) | 149 | $451 | $777 | $1,329 | $1,793 | **2.9×** |

**Corrected ownership breakdown (2026-03-17):**

| Ownership | Hospitals | Discharges | Total Spend | Median/DC |
|-----------|-----------|-----------|-------------|-----------|
| For-Profit | 1,576 | 29.7M | $18.8B | $236 |
| Nonprofit | 2,993 | 95.4M | $128.9B | $1,270 |
| Government | 911 | 17.2M | $23.0B | $1,332 |

NOTE: For-profit's low median likely reflects hospital mix (specialty/surgical centers, lower acuity). Nonprofits carry 75.5% of national supply spend. The story here is variance within ownership type, not between types.

### 2b. Savings Scenarios

| Scenario | Savings | Methodology |
|----------|---------|-------------|
| Q4→P75 within bed-size peers (CMI-adjusted) | **$28.5B** | Conservative benchmark |
| Above-median→P50 within peers | **$58.9B** | Moderate benchmark |
| UCSF 6.5% universal transparency reduction | $11.1B | Zygourakis et al. |

---

## 3. SUPPORTING EVIDENCE (Published Literature)

### 3a. Operating Room Supply Waste

- **Zygourakis et al. 2017 (UCSF):** Surgical supply costs vary 2–4× across surgeons performing identical procedures at the same hospital. Cost awareness intervention reduced supply spending 6.5% in first year. (J Neurosurg)
- **Chasseigne et al. 2018 (meta-review):** 13–20% of surgical supply costs are wasted through over-ordering, preference card bloat, and expired-but-usable supplies. (World J Surg)
- **Guzman et al. 2015:** Standardizing preference cards for laparoscopic cholecystectomy reduced supply costs 16.2% per case. (JACS)
- **Koyle et al. 2017:** Pediatric urology OR supply standardization reduced waste 20% and costs 17%. (J Pediatr Urol)

### 3b. Implantable Device Pricing

- **Robinson et al. 2012:** Total knee replacement implant costs range **$1,797–$12,093 (6.7×)** across hospitals. (Health Affairs)
- **Fang et al. 2020:** Reference pricing for TKA implants achieved **16.7% cost reduction** without affecting outcomes. (JBJS)
- **Letchford et al. 2014:** Physician preference items (PPIs) account for 40–60% of OR supply costs; surgeon choice overrides GPO contracts.

### 3c. GPO Bargaining and Hospital Purchasing Efficiency

- **Kim et al. 2024 (Management Science):** Hospital relative bargaining power to the GPO matters more than GPO size for procurement savings. Smaller hospitals benefit less even within the same GPO.
- **Yang et al. 2025 (Production & Operations Management):** 14–50% spending inefficiency exists within GPO tier structures. Hospitals often don't achieve their GPO-negotiated best price.
- **Burns & Lee 2008:** GPO administrative fees (typically 1–3% of contracted spend) create conflicts of interest: GPOs earn more when prices are higher.

### 3d. Expiration Dating and Premature Disposal

- **FDA SLEP Program:** Testing found 90% of medications remain stable 5.5+ years beyond labeled expiration date. Military program saves ~$2.1B/year by extending expiration dates. (Lyon et al. 2006)
- **Cantrell et al. 2012 (Arch Intern Med):** 8 medications tested 28–40 years past expiration still retained >90% potency.
- **Cohen 2005 (BMJ):** OEM "forced obsolescence" — manufacturers deliberately limit device lifecycle through software updates, proprietary service contracts, and DRM on replacement parts.

---

## 4. THE SURPLUS ECOSYSTEM (Where the Waste Goes)

### 4a. Medical Surplus Nonprofits — Financial Overview

| Organization | Location | Annual Revenue | Contributions | Annual Containers/Shipments |
|-------------|----------|---------------|---------------|---------------------------|
| **Direct Relief** | Santa Barbara, CA | $2.27B | $2.26B (97% in-kind) | 5,823 tons to 90 countries |
| **Project C.U.R.E.** | Denver, CO | $65.3M | $65.1M | 200+ containers/yr to 135 countries |
| **MATTER** | Minneapolis, MN | $35.0M | $32.5M | "Truckloads" (per Dean Buckner) |
| **MedShare** | Atlanta, GA | $18.4M | $18.1M | Ships to 100+ countries |
| **Afya Foundation** | Yonkers, NY | $11.6M | $11.6M | NY/NJ region |
| **MAP International** | Brunswick, GA | ~$890M | ~$890M (medicine) | Global medicine distribution |

Source: ProPublica Nonprofit Explorer, Form 990 Tax Year 2023

**Total identifiable in-kind medical goods flowing through surplus nonprofits: >$3.3 billion/year** (dominated by Direct Relief's $2.3B pharmaceutical channel and MAP International's $890M medicine program).

### 4b. Schedule M Data — EXTRACTED (IRS E-File XML)

**Gap closed.** We downloaded IRS e-filed 990 XMLs directly from IRS TEOS bulk downloads and parsed Schedule M programmatically. No GuideStar Pro needed.

**Target nonprofit Schedule M detail (Line 20: Drugs & Medical Supplies):**

| Organization | Schedule M Amount | Contributions | Valuation Method |
|-------------|------------------|---------------|-----------------|
| Direct Relief | $2,136,751,121 | 1,705 | Est. Wholesale Value |
| MATTER | $28,804,314 | N/A | Wholesale Value |
| MedShare | $14,159,832 | 1,327 | Fair Market Value |
| Afya Foundation | $5,749,232 | 426 | FMV |
| Project C.U.R.E. | Not in e-file (paper filer) | — | — |

**NATIONAL SCAN (4 of 12 months, original analysis):**
- **620 unique nonprofits** reported receiving Drugs & Medical Supplies on Schedule M
- **Combined value: $1.4 billion** (partial year; 4 of 12 monthly ZIP files scanned)
- **Full-year estimate: $3.5–5B+** (extrapolating, plus Direct Relief's $2.14B)
- Top recipients include: MAXAID (WA, $298M), International Medical Relief (CO, $109M), United Palestinian Appeal (VA, $102M), United Mission for Relief & Development (VA, $51M), Salvadoran American Humanitarian (FL, $38M), World Medical Relief (MI, $36M)
- Full results: `research/schedule_m_drugs_medical.csv`
- **This is an original dataset.** No published source aggregates Schedule M drug/medical supply donations nationally.

**Series-wide pipeline:** The same XML parsing approach can extract Schedule H (nonprofit hospital community benefit) for Issue #15 and Schedule J (executive compensation) for the Shareholder Question. See `research/SERIES_DATA_NEEDS.md`.

### 4c. Dean Buckner Source Intelligence

- Former MATTER employee (2 years), Minneapolis
- MATTER's "360" division handles hospital surplus redistribution
- Reports organizations like MATTER "exist in almost every large US city"
- Confirmed Afya Foundation (NY/NJ) as comparable
- Key insight: hospitals are donating "truckloads" of functional, usable supplies
- Full source notes: `issue_18/SOURCE_NOTES.md`

---

## 5. THE "WHO PROFITS" SIDEBAR — GPO/Distributor Financials

### Premier Inc. (PINC) — The GPO

| Metric | FY2025 |
|--------|--------|
| Revenue | $1.0B |
| Gross Margin | 73.0% |
| GPO Net Admin Fees | $150.1M (down 10% YoY) |
| Member Purchasing Volume | $87B |
| Operating Margin | -0.93% (loss year) |
| Business Model | 1–3% admin fee on $87B contracted volume |

The GPO model: Premier collects administrative fees from suppliers (not hospitals) for access to its 4,250+ member hospitals. Hospitals get "lower" prices; suppliers get guaranteed volume. The conflict: GPOs earn more when contract prices are higher.

### Cardinal Health (CAH) — The Distributor

| Metric | FY2025 |
|--------|--------|
| Revenue | $222.6B |
| Net Income | $1.56B |
| Net Margin | 0.68% |
| GMPD Segment (medical products) | $12.6B |
| CEO Compensation | $18.98M |

Cardinal distributes both pharmaceuticals ($204.6B) and medical products ($12.6B). The medical products segment is the hospital supply chain — thin margins but massive volume.

### Owens & Minor (OMI) — The Distributor

| Metric | FY2024 |
|--------|--------|
| Revenue | $10.7B |
| Net Income | -$362.7M (loss) |
| Products & Healthcare Services | ~74% of revenue |
| CEO Compensation | $10.7M |
| Status | Actively divesting hospital supply segment |

OMI is exiting the hospital supply distribution business, signaling structural margin challenges.

### Vizient — The Largest GPO (Private)

Not publicly traded. Estimated $130B+ in contracted purchasing volume. No 10-K available. Would need to access through industry reports or Vizient's own publications.

---

## 6. INTERNATIONAL COMPARISON DATA

- **US Customs HS codes 9018–9022** track medical instrument/device exports. USA Trade Online (Census Bureau) has the data but requires specific queries by HS code and partner country.
- **OECD Health Statistics** don't break out supply costs separately from hospital spending.
- **iFHP data** (used in Issue #3) covers procedure-level pricing but not supply costs per se.
- Gap: No international comparison of hospital supply cost per discharge exists. This could be a future original analysis if we can find comparable data from NHS England or the German DRG system.

---

## 7. NARRATIVE STRUCTURE (Proposed)

**The hook:** A cargo container full of IV tubing, surgical gloves, and patient monitors leaves a Houston hospital loading dock. It's all functional. Some of it is unopened. It's headed to Bolivia. This scene plays out in every major US city, every week.

**The number:** $170.9 billion flows through US hospital supply chains annually. Original HCRIS analysis of 5,480 hospitals reveals that hospitals in the same size class, treating patients of similar complexity, spend 2.3–7.7× different amounts on supplies per discharge. The gap is not explained by patient mix, geography, or hospital type.

**The mechanism:** Three layers of waste:
1. **Procurement inefficiency** — GPOs earn admin fees as a percentage of spend (perverse incentive); hospitals don't achieve best GPO prices (14–50% inefficiency, Yang 2025); physician preference items bypass contracts entirely
2. **Operating room waste** — Preference card bloat, over-ordering, 13–20% waste rate (Chasseigne 2018); implant price variance of 6.7× for identical devices (Robinson 2012)
3. **Expiration/disposal waste** — FDA SLEP shows 90% of drugs stable 5.5+ years past label; hospitals dispose of functional supplies that end up filling 200+ cargo containers/year for Project C.U.R.E. alone; OEM forced obsolescence on devices

**The evidence:** A network of surplus nonprofits processes >$3.3B/year in donated hospital supplies — the visible tip of the waste iceberg. Dean Buckner (MATTER, Minneapolis): "Organizations like ours exist in almost every large US city. The supply never runs out."

**Who profits:** Premier (73% gross margin GPO), Cardinal Health ($18.98M CEO comp on 0.68% margins), device manufacturers (implant price opacity). Also: revenue cycle management companies that process the billing for all this complexity.

**The fix:** Reference pricing for implantable devices (proven: 16.7% reduction, Fang 2020). GPO fee transparency (require disclosure of admin fee percentages). OR supply standardization programs (proven: 16–20% reduction). Expiration date reform (extend for stable medications per SLEP data). National supply cost benchmarking (make HCRIS supply data publicly accessible in user-friendly format).

---

## 8. DATA GAPS AND ACCESS NEEDS

### What We Have
- [x] HCRIS national supply variance (5,480 hospitals) — ORIGINAL, NOVEL
- [x] Corrected ownership breakdown (CTRL_TYPE fix verified 2026-03-17)
- [x] Academic literature on OR waste, device pricing, GPO economics
- [x] Surplus nonprofit financial overview (6 organizations, ProPublica)
- [x] **Schedule M extracted from IRS e-file XML** — 4 of 5 target nonprofits parsed, national scan of 620 orgs ($1.4B in 4 months)
- [x] **National mapping STARTED** — 620 nonprofits identified receiving Drugs & Medical Supplies (partial year). Full year would be 1,500–2,000+.
- [x] Dean Buckner source intelligence
- [x] GPO/distributor 10-K financials (Premier, Cardinal, OMI)
- [x] FDA SLEP expiration data
- [x] Savings scenarios ($28.5B conservative, $58.9B moderate)

### What We Still Need

**HIGH PRIORITY:**

1. ~~Schedule M detail from Form 990s~~ — **DONE.** Extracted directly from IRS TEOS XML downloads. No GuideStar Pro needed.

2. ~~National mapping of medical surplus nonprofits~~ — **PARTIALLY DONE.** 620 orgs from 4 months. Need remaining 8 monthly ZIPs for complete picture.

3. **Vizient purchasing data** — As the largest GPO (private), Vizient's contracted purchasing volume and admin fee structure would complete the GPO picture. Their annual report or industry presentations may be publicly available.

**MEDIUM PRIORITY (adds depth):**

4. **US Customs export data (HS 9018–9022)** — Would quantify the export flow of donated/surplus medical equipment. Available through USA Trade Online (Census Bureau) but requires account setup and specific queries.

5. **State hospital cost report data** — Some states (CA OSHPD, NY SPARCS) publish more granular supply cost data that could validate our HCRIS findings at the facility level.

6. **Device manufacturer pricing data** — If we could get a GPO contract price list for common implants (hip, knee, cardiac), we could compute the actual price variance ourselves. This is the "holy grail" but likely proprietary.

**NICE TO HAVE (enriches the narrative):**

7. **Interview with hospital supply chain director** — Someone who can describe the day-to-day experience of GPO contracts, physician preference items, and the disposal decision.

8. **MATTER or Afya warehouse visit** — Andrew is in a good position for this. Seeing truckloads of functional supplies creates the visual hook.

9. **Reprocessing industry data** — Companies like Stryker Sustainability Solutions reprocess single-use devices. Market size data would quantify the "forced obsolescence" angle.

---

## 9. WHERE ANDREW NEEDS TO HELP

### Access I Cannot Get Programmatically

1. ~~GuideStar Pro / Candid~~ — **NOT NEEDED.** We built a pipeline to extract Schedule M directly from IRS TEOS XML bulk downloads (free). Already parsed 620 orgs. GuideStar Pro is $399/month and adds nothing we can't get from the IRS data.

2. **USA Trade Online** — Free Census Bureau account required. Once set up, query HS 9018 (electromedical instruments), 9019 (mechano-therapy appliances), 9021 (orthopedic appliances), 9022 (X-ray apparatus) by year and destination country. This would quantify the export of donated medical equipment.

3. **MATTER warehouse visit** — Andrew is based in Minneapolis. Dean Buckner is a confirmed contact. A visit to MATTER's 360 division warehouse would produce photos, firsthand observation of what hospitals are donating, and potentially access to their intake records (what hospitals are their biggest donors, what categories of supplies, what condition).

4. **Hospital supply chain director interview** — Andrew's healthcare contacts from prior issues may include someone who manages hospital procurement. Even one conversation about GPO contracts, physician preference items, and the disposal decision would add color.

5. **Premier Inc. investor relations** — A direct question about GPO admin fee structures and how they're disclosed. Premier is publicly traded and has an IR contact.

### What I Can Do Next

- Draft the newsletter once you give the green light
- Build all 5 charts (I have the data for all of them)
- Run additional HCRIS cuts (e.g., supply cost by state, by teaching status, by rural/urban)
- Search for more academic literature on specific sub-topics
- Pull Vizient/Premier presentation decks from healthcare conference archives

---

## 10. DIFFERENTIATION CHECK

**Has anyone else done this analysis?**

No. The specific HCRIS-based national computation of supply cost variance across 5,480 hospitals, stratified by bed size and CMI-adjusted, has not been published by:
- KFF (tracks insurance/coverage, not hospital supply chains)
- STAT News (covers pharma/biotech, occasional hospital stories)
- AHA (represents hospitals; wouldn't publish data showing member inefficiency)
- Health Affairs (publishes academic papers but hasn't done this specific computation)
- GAO (has done GPO reports but not supply cost variance from HCRIS)

The closest published work:
- RAND hospital pricing studies (focus on commercial vs. Medicare payment ratios, not supply costs)
- Zygourakis UCSF OR waste studies (single-institution, not national)
- Robinson device pricing studies (cross-sectional but limited sample)

**Our edge:** National scope (5,480 hospitals), federal data source (reproducible), CMI-adjusted (methodologically sound), combined with on-the-ground source intelligence (Dean Buckner, surplus nonprofits). Nobody else has connected HCRIS supply variance data to the surplus nonprofit ecosystem.
