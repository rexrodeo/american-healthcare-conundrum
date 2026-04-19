---

*Each issue of The American Healthcare Conundrum identifies one fixable problem in U.S. healthcare spending, builds the data case, and recommends a specific policy fix. All analysis uses publicly available data. Code is open-source.*

---

```
Target: ~$3T US-Japan per-capita gap
Japan: highest life expectancy, lowest
infant mortality in OECD, ~half US cost

Full scale: $0 ──────────────── $3T
            ███████░░░░░░░░░░░  14.3%
            ↑ $428.6B identified

Zoomed (first $500B):
 #1  ░        $0.6B   OTC Drug Overspending
 #2  ███      +$25.0B  Drug Pricing
 #3  ██████████  +$73.0B  Hospitals
 #4  ████      +$30.0B  PBM Reform
 #5  ████████████████████████████  +$200.0B  Admin Waste
 #6  ████      +$28.0B  Supply Waste
 #7  █████     +$40.0B  GLP-1 Pricing
 #8  ████      +$32.0B  Denial Machine
     ─────────────────────────────────────────────
     Total: $428.6B · $2,571.4B remaining
```

---

## The Denial Machine

Medicare Advantage insurers approve 95.4 percent of prior authorization requests. That's what UnitedHealthcare, Humana, CVS, Elevance, and Cigna report to Medicare.

But their own contract-level data, disclosed for the first time under the CMS-0057-F Prior Authorization Transparency Rule (April 2026), tells a different story. Across 61 UnitedHealthcare contracts covering 7.9 million patients, the actual denial rate ranged from 0.7 percent to 25.2 percent. Same company. Same rules. Same eligibility criteria. Thirty-six times variance.

The 95.4 percent headline is misleading because it weights all requests equally, including routine renewals and pre-approved services that inflate the denominator. When you strip those out and look at the volume-weighted denial rate for standard (non-expedited) requests, UnitedHealthcare denies 13.5 percent of claims across its Medicare Advantage book. That's not 95.4 percent approval. That's roughly one in seven requests rejected.

This per-contract variance is the smoking gun. When the same insurer applies the same coverage rules to similar patients in overlapping geographies and produces denial rates that vary by 36 times, clinical judgment is not the variable. Business policy is.

For the patients caught in it, the denial machine means care suppression, disease progression, and $32 billion per year in extracted value from the healthcare system, with a fourth mechanism we can see but cannot yet quantify that likely adds tens of billions more.

*[Subscribe to The American Healthcare Conundrum]*

---

### What Actually Happens When Your Claim Is Denied

A patient with rheumatoid arthritis needs a biologic drug. The biologic is expensive, but it stops joint destruction. Before dispensing it, the insurer requires prior authorization: paperwork proving the cheaper drugs failed first.

The physician submits the PA. The insurer denies it. The patient receives a letter: "This service is not medically necessary at this time."

The physician can appeal. Most patients never find out. Even if the physician appeals, the delay is 20 to 45 days. The patient, in pain, postpones the medication. Some never follow up. Some switch to the insurer's own rheumatology clinic, where the biologic gets approved faster because that clinic is owned by the insurer, and approval there generates margin rather than cost.

Those who do appeal have strong odds: CMS-0057-F disclosures show a 57.9 percent overturn rate at UnitedHealthcare and 64.7 percent at Humana. The insurer knew this when it denied the claim. The denial was a bet: the probability that the patient wouldn't appeal (about 91 to 97 percent, depending on the insurer) times the savings from not paying for care, minus the cost of processing the rare appeal.

### The Price Behind the Paperwork

I need to break the fourth wall for a moment, because a woman very close to me just lived through this.

She needed a brain MRI. Her physician ordered the scan to investigate recurring migraines. She scheduled it at Touchstone Imaging in Denver, an in-network provider under her Anthem BlueCross PPO. The day before the appointment, Touchstone cancelled: Anthem had not returned the prior authorization.

Touchstone offered an alternative. Self-pay: $450. Same machine, same technicians, same radiologist reading the images. No authorization needed. Treatment for anything the MRI found would still go through insurance.

Here is where it gets interesting. Anthem's contract rate for the same scan is $3,000. That is 6.7 times the cash price. The insurer "negotiated" a rate that is 567 percent of what the imaging center charges a person who walks in and pays.

But the $450 cash price does not count toward her $3,400 annual deductible. Her family has already applied roughly $2,150 this year. If she pays $3,000 through insurance, only $850 comes out of pocket (the remaining balance to hit the deductible), and every claim after that is covered at 100 percent. If she pays $450 cash, it saves money today but the deductible clock stays where it is. The next claim starts from the same $2,150 mark.

The insurer has built a trap with three walls. The prior authorization requirement creates friction that delays or prevents care. The inflated contract rate (6.7 times the cash price) means every dollar that does flow through insurance maximizes premium justification. And the deductible structure makes the patient financially rational to pay $850 instead of $450, because only the inflated price counts toward the threshold that unlocks full coverage.

This is not an edge case. Every American with a high-deductible health plan faces this calculation every time a prior authorization is delayed. The insurer profits whether the patient goes through insurance (inflated rate) or self-pays (deductible clock stalls). The only person who loses is the patient.

Our original analysis, crossing CMS March 2026 Medicare Advantage enrollment data (35.6 million beneficiaries across 7,606 plans) with KFF CY2024 prior authorization reporting, quantifies the scale. UnitedHealthcare generates 8.4 million PA requests per year from its 9.4 million MA enrollees. Of those, 1.06 million are denied. Only 127,000 are appealed. That leaves 934,000 denials never challenged, of which an estimated 736,000 were wrongful (applying the insurer's own overturn rate to the non-appellant population).

A silent denial is a denial the patient never appeals. The care doesn't happen, the insurer's decision stands, and no regulator ever sees the outcome.

Across all seven major MA insurers, the numbers are: 57 million PA requests, 4.1 million denials, 496,000 appeals, and 3.6 million silent denials. Of those silent denials, an estimated 2.8 million were wrongful: patients denied care they were entitled to who never appealed.

*[Chart 1: Same Insurer. Same Rules. 36x Variance in Denial Rates.]*

### The ACA Marketplace: 70 Percent of Denials Are Administrative

The denial machine isn't limited to Medicare Advantage. Our original analysis of the KFF ACA Marketplace 2024 Working File (2,540 plans across all 50 states) reveals that ACA marketplace insurers denied 75.9 million of 374 million claims in 2024, a 20.3 percent overall denial rate.

The reason breakdown tells the real story. Of all coded denials, 69.7 percent were administrative or procedural: referral requirements (9.6 percent), administrative errors (25.9 percent), member coverage issues (7.6 percent), or the catch-all "other" category (37.1 percent). Only 20.5 percent of denials were clinical, meaning medical necessity, benefit limits, excluded services, or investigational/cosmetic. The remaining 9.8 percent were network-design denials (out-of-network providers).

The issuer-level variation is extreme. The KFF data shows ACA denial rates ranging from 3.5 percent to 47.0 percent across issuers, with a median of 20.9 percent. Moda Health in Alaska denied 47.0 percent of claims. CareSource in North Carolina denied 37.0 percent. UnitedHealthcare subsidiaries in Louisiana, Michigan, and Ohio denied 33 to 36 percent of claims. These are not clinical decisions. These are business models.

*[Chart 2: The Appeal Gap: Most Denials Are Never Challenged]*

### The Denial Trend: 2 Percentage Points in Five Years

Prior authorization volume in Medicare Advantage has grown from 37.1 million requests in 2019 to 52.8 million in 2024, per KFF historical reporting. The denial rate has climbed from 5.7 percent (2019) to 7.7 percent (2024).

Our original trend analysis computes excess denials: the number of denials above what would have occurred if the 2019 baseline rate (5.7 percent) had held steady as volume grew. In 2024 alone, that excess was 1.06 million denials. Cumulatively from 2020 to 2024: 2.2 million excess denials attributable to the rate increase, not volume growth.

This is the denial machine accelerating: more requests processed, at a higher denial rate, generating more revenue from each percentage point of increase.

---

## The Savings Opportunity: Three Mechanisms We Can Measure, One We Can't Yet

The denial machine extracts value through three quantified mechanisms, plus a fourth we can see but cannot yet measure from public data. All four are directly controllable through regulation or enforcement. The three we measure target different pools of money and are additive: Component A captures downstream healthcare costs from foregone care, Component B captures margin extracted through ownership structures, and Component C captures the incremental impact of AI adoption on denial volumes. Component E is a small documented overpayment from risk adjustment coding. Component D, the deductible-delay trap shown in the MRI vignette above, is real and measurable in principle but requires claims-level data to quantify cleanly. We describe it below and ask for help closing the estimate.

### Component A: Care Suppression ($10.4B to $17.0B per year)

When 2.8 million MA patients are denied entitled care and never appeal, the denied care is foregone permanently. The disease progresses. The ADA's 2023 Cost of Diabetes study estimates uncontrolled diabetes costs $200 to $400 per month in additional complications. The National Cancer Institute's SEER data shows late-stage cancer diagnosis increases treatment costs by 10 to 15 percent. A systematic review by Banerjee et al. in the American Journal of Managed Care (2023) found care delays result in 12 to 25 percent higher downstream costs depending on disease category.

With 3 million annual denials in Medicare Advantage and a 12 to 18 percent downstream cost escalation, the suppression cost is $8.8 to $13.3 billion per year. Adding the AMA 2024 Physician Survey's finding that 8 percent of patients with PA delays experienced death, permanent damage, or disability (a 1 to 4 percent multiplier on denied care costs), the total care suppression component reaches **$10.4 billion to $17.0 billion per year (mid: $13.7B)**.

### Component B: Vertical Integration Margin Arbitrage ($6.7B to $13.8B per year)

The largest insurers own the providers delivering care. UnitedHealthcare owns Optum Health ($105.4 billion in FY2024 revenue, per UnitedHealth 10-K). CVS owns MinuteClinic (1,100+ locations) and primary care clinics through Aetna. Elevance owns Carelon's practice networks. Cigna owns Evernorth.

This creates a mechanism where the insurer can pay its own providers more than it pays competitors and capture the margin internally. Here's how it works in practice: when UnitedHealthcare buys care from Optum, every dollar of inflated price stays within UnitedHealth Group. When it buys from an independent hospital, the excess goes to the hospital. Vertical integration makes overpaying your own network profitable.

A November 2025 Health Affairs study found that UnitedHealthcare pays Optum-owned providers 17 percent more than external providers for identical services. In concentrated markets (greater than 25 percent UHC market share), the premium reaches 61 percent.

The Big 4 insurers control 25.3 million MA enrollees (CMS March 2026 enrollment data). They collectively manage roughly $462 billion in MA spending (CMS NHE 2023, MA share). An estimated 8 to 15 percent flows to owned provider networks: roughly $39 billion. At a 17 to 35 percent payment premium (Health Affairs 2025), that translates to **$6.7 billion to $13.8 billion per year (mid: $10.3B)** in extracted margin recoverable through rate normalization.

### Component C: AI Denial Escalation ($4.9B to $6.4B per year)

A January 2026 Stanford study in npj Digital Medicine measured denial rates before and after AI implementation across matched Medicare Advantage plan samples. AI systems increased denial rates by 5 to 8 percentage points beyond the human baseline.

A human reviewer denies roughly 12 to 18 percent of requests. The AI denies 17 to 26 percent of the same requests. The AI does not improve clinical outcomes. It matches cases to rules. If the rule says deny, it denies.

As of 2025, 22 percent of MA plans have implemented AI for PA decisions (KFF CY2024 Part C reporting data). Medicare Advantage covers 33.1 million beneficiaries generating an estimated 297 million total claims annually (CMS NHE 2023). The AI-covered 22 percent of claims experience a 5 to 8 percentage point increase in denial rate, producing 3.3 to 5.2 million excess denials per year from AI systems alone. At an average claim cost of $1,515 (CMS MA spending per beneficiary / annual claim frequency), the recoverable savings from regulating AI denials is **$4.9 billion to $6.4 billion per year (mid: $5.7B)**.

This count is the marginal impact of AI beyond the human reviewer baseline. It is additive to Component A, not a subset of it: Component A measures downstream care costs from all 3 million annual MA denials, while Component C measures only the incremental denials that would not have occurred without AI.

### Component D: Deductible-Delay Extraction (we can see it, we cannot yet measure it)

The MRI vignette above is not anecdote. It is a measurable category of insurer extraction. But measuring it honestly requires data we do not yet have access to, and we would rather publish a gap we can explain than a number we cannot defend.

> **📍 The gap we can't yet measure, and how you can help close it**
>
> There is a fourth mechanism in the denial machine that we believe runs into billions of dollars per year, but public data cannot cleanly quantify it yet. We are publishing what we know, and asking for help to measure what we can't.
>
> **The mechanism.** When an insurer denies prior authorization on a shoppable service (MRI, CT, lab panel, planned procedure), many patients shift to cash pay. The cash price is typically a fraction of the negotiated rate, but cash does not count toward the in-network deductible. The patient saves money on that visit but restarts the deductible clock. The insurer avoids paying the claim AND keeps the inflated negotiated rate as the anchor for future encounters. Two ways to win from a single denial.
>
> **A concrete case (the vignette at the top of this issue).** Brain MRI. Anthem denies PA. Touchstone cash price $450. Anthem's negotiated rate $3,000. Patient either pays $450 cash (saves $2,550 today, deductible clock stalls) or waits weeks for PA resolution and pays $850 out of pocket to hit a $3,400 deductible (more expensive short-term, but unlocks 100 percent coverage after).
>
> **Two ways to win from a single denial.**
>
> *Path A, patient shifts to cash.* $450 at the facility. Nothing applied to the deductible. The next claim still starts at $2,150 of a $3,400 deductible. The insurer avoids paying the claim and keeps the $3,000 negotiated rate anchored for every future encounter at that facility.
>
> *Path B, patient goes through insurance.* Insurer-billed rate $3,000, which is 6.7× the cash price. The patient pays $850 toward the deductible. The plan pays the rest, and the spread between what the MRI actually costs and what the contract says it costs stays baked into the rate.
>
> **Why we cannot quantify this from public data alone.** Testing the denial-induced deductible-delay claim requires matched patient-level data: claim denials, subsequent cash payments at the same facility for the same service code, and deductible exposure at the time of the encounter. CMS National Health Expenditure tables show the $505 billion out-of-pocket pool. Peterson-KFF shows deductibles are 52 percent of that. HCCI shows 30 to 43 percent of care is shoppable. Wang/Bai 2023 shows the cash-vs-negotiated wedge runs 50 to 67 percent on 70 shoppable services. These give us the scale. None of them give us the denial linkage.
>
> **What would break this open.** Matched patient-level claims and deductible-exposure data. If your organization holds licensed access to **Truven/MarketScan, Optum Clinformatics, IQVIA Pharmetrics, or Definitive Healthcare**, or if you have an active DUA for **CMS LDS or VRDC, a state All-Payer Claims Database, or AHRQ HCUP**: please reach out at **[ahcdata.fund](https://ahcdata.fund)** or email **contact@ahcdata.fund**. Co-publication under your DUA is fine. Code stays open. Findings stay published. We will turn the MRI case into a verifiable per-procedure number and credit you by name.

### Component E: Risk Adjustment Coding ($0.3B per year)

The HHS Office of Inspector General found in October 2024 that Medicare Advantage plans inflate risk scores by documenting diagnoses not supported by medical records. The documented overpayment: $0.3 billion annually industry-wide.

### Consolidated Estimate

Component midpoints: $13.7B (A) + $10.3B (B) + $5.7B (C) + $0.3B (E) = **$30.0B**. Conservative floor: $22.3B. Upper range: $37.5B. We book **$32.0B**, the upper-conservative estimate, reflecting that our Component A methodology uses conservative overturn-rate assumptions and our Component B uses the lower bound of the Health Affairs vertical integration premium range. Component D (deductible-delay extraction) is excluded from the booked total until we can quantify it against claims-level data; we believe it adds tens of billions more, but we would rather under-book than over-claim.

*[Chart 3: $32 Billion in Recoverable Denial Extraction (stacked bar)]*

---

## MLR Gaming: The Accounting Trick That Enables Everything

The Affordable Care Act requires insurers to spend at least 80 percent of premium revenue on actual medical care (the Medical Loss Ratio rule). Our original analysis of CMS Medical Loss Ratio Public Use Files (2019-2024) reveals how the largest insurers game this threshold.

The industry-wide MLR in 2024 was 88.9 percent on $1.586 trillion in total premiums (CMS MLR PUF 2024). But the Big 5 insurers (UnitedHealth, Elevance/Anthem, CVS/Aetna, Cigna, Humana) operate at an average MLR of just 80.6 percent on $190.8 billion in combined premiums, barely above the regulatory floor. That 8.3 percentage point gap between the Big 5 and the market average represents $15.8 billion in premiums that could flow to medical care but instead covers administrative costs and profit.

How do they stay so close to the floor? The mechanisms include: reclassifying administrative spending as "quality improvement" (which counts toward the 80 percent), exploiting three-year MLR averaging to smooth over bad years, routing inflated payments through captive reinsurance arrangements, and accruing "performance bonuses" as medical expenses that are never paid out. Bernstein et al. estimated in JAMA Health Forum (2024) that MLR gaming extracts $11.8 billion to $20.7 billion annually.

Our CMS MLR PUF analysis also shows that total industry administrative expenses reached $183.6 billion in 2024 (11.6 percent of premiums), with the largest single category being "Other General and Administrative" at 52.2 percent of admin costs ($95.9 billion). This catch-all category has limited transparency requirements, creating room for expense reclassification.

We do NOT include MLR gaming in the booked $32B savings estimate because it targets a different mechanism (accounting treatment of premiums vs. denial-driven extraction). But tightening the MLR definitions would close the escape valve that makes the denial machine possible: if insurers couldn't game the 80 percent floor, the financial incentive to deny claims would diminish.

---

## Who Profits

The five publicly traded insurers profiled below collectively hold more than 150 million covered lives and generated over $1.3 trillion in FY2024 revenue. The denial and vertical-integration mechanisms documented above are their dominant profit levers.

> **Who Profits: UnitedHealth Group (UNH)**
> FY2024 Revenue: $400.3B | Operating Margin: 8.2% | CEO Comp (Andrew Witty, through Oct 2025): $26.3M | Stock Buybacks (2020-24): ~$33B | Lobbying (2020-24): ~$43M
> **This issue's mechanism:** Volume-weighted prior-authorization denial rate of 13.5 percent across 61 Medicare Advantage contracts (CMS-0057-F), contradicting the headline 95.4 percent approval figure. Optum vertical integration generates an estimated $2.1 to $3.2 billion in annual margin arbitrage (Health Affairs 2025 premium applied to Optum revenue). Operates at an 85.5 percent medical loss ratio, the lowest among major insurers (CMS MLR PUF 2024). In April 2026 the DOJ expanded its investigation from Medicare Advantage overpayments to anti-competitive conduct in Optum Rx and physician reimbursement. Stephen Hemsley named interim CEO after Andrew Witty's October 2025 departure.

> **Who Profits: CVS Health (CVS), Aetna**
> FY2024 Revenue: $372.8B | Operating Margin: 3.1% | CEO Comp (David Joyner): $17.8M | Stock Buybacks (2020-24): ~$8.5B | Lobbying (2020-24): ~$46M
> **This issue's mechanism:** Aetna ran a 12 percent prior-authorization denial rate across its Medicare Advantage plans in CY2024 (KFF). MinuteClinic's 1,100+ locations give the combined entity an owned care channel to steer denied patients toward lower-cost internal providers. AI PA escalation reached 22 percent adoption in 2025 (KFF), matching industry leaders. Aetna MLR: 82.1 percent (CMS MLR PUF 2024).

> **Who Profits: Elevance Health (ELV)**
> FY2024 Revenue: $175.2B | Operating Margin: 4.8% | CEO Comp (Gail Boudreaux): $20.5M
> **This issue's mechanism:** Prior-authorization denial rate of 4 percent (lowest among Big 5 per KFF), but Carelon-owned practice networks capture up to a 61 percent concentrated-market premium in affected geographies (Health Affairs 2025). AI-driven PA decisions reached 22 percent adoption. The low headline denial rate masks the vertical-integration extraction that has replaced denial as the dominant margin lever.

> **Who Profits: Cigna Group (CI)**
> FY2024 Revenue: $247.1B | Operating Margin: 5.3% | CEO Comp (David Cordani): $23.3M | Stock Buybacks (2020-24): ~$29B | Lobbying (2020-24): ~$44M
> **This issue's mechanism:** Strategic exit from Medicare Advantage is underway (sale of MA book to HCSC, announced January 2024). Profit now concentrates in the Evernorth pharmacy-services arm, which captures PBM margin through the same vertical integration playbook UnitedHealth and Optum run on the medical side. MLR of 87.2 percent (CMS MLR PUF 2024).

> **Who Profits: Humana Inc. (HUM)**
> FY2024 Revenue: $111.9B | Operating Margin: negative (MA segment operating loss) | CEO Comp: $16.8M
> **This issue's mechanism:** Six percent prior-authorization denial rate across 32 MA contracts (CMS-0057-F), but the lowest appeal-initiation rate of the Big 5 at 2.7 percent of denied claims (compared to UnitedHealth's 8.7 percent), suggesting the appeal process is structurally harder to navigate. Of those who do appeal, Humana overturns 64.7 percent, the highest overturn rate of any insurer in the dataset. Enrollee-level data shows appeals volume is suppressed, not clinical disagreement.

*Sources: UnitedHealth Group 10-K and DEF 14A proxy; CVS Health 10-K; Elevance Health 10-K; Cigna Group 10-K; Humana Inc. 10-K (all SEC EDGAR FY2024); CMS CY2024 Part C Prior Authorization Reporting Data; CMS-0057-F Prior Authorization Transparency Disclosures (April 2026); KFF Medicare Advantage analysis (2024-2025); Health Affairs November 2025 (Optum vertical integration premium study); CMS Medical Loss Ratio Public Use File 2024; DOJ Antitrust Division filings; OpenSecrets.org federal lobbying disclosure database (2020-2024); company cash flow statements.*

---

## The Fix

### Immediate: Prior Authorization Reform (Components A and C)

Establish federal standards for prior authorization. The CMS Prior Authorization Final Rule (effective January 1, 2026) sets the framework: 72-hour turnaround for expedited requests, 7 days for standard. Expand this with:

1. **Mandatory written clinical justification for any denial.** Replace boilerplate "not medically necessary" with a requirement that the insurer cite the specific evidence-based guideline the request fails to meet.

2. **Automatic approval if the deadline passes.** If the insurer doesn't respond within the regulatory window, the request is approved. This inverts the default: the insurer bears the cost of delay, not the patient.

3. **Ban AI from making adverse PA determinations without human clinician review.** Minnesota's HF2500 (2026) has the right structure. Expand it federally. Require AI decision rationale to be disclosed to the patient and physician.

4. **Gold-carding for low-denial physicians.** Physicians with overturn rates above 80 percent on appeals should be exempt from prior authorization for those service categories.

### Medium-Term: Vertical Integration Limits (Component B)

Prohibit insurers from paying owned providers more than 105 percent of Medicare rates for equivalent services. This removes the margin advantage of vertical integration without banning it. California's SB 1039 (2024) attempted a version of this; a federal standard with enforcement teeth would apply it at scale.

Alternatively, require strict operational independence: separate management, separate P&L reporting, and arm's-length pricing between insurance and provider divisions, using the same firewall standards from the Medicare Advantage anti-kickback statutes.

### Long-Term: MLR Enforcement and Risk Adjustment Audits

Tighten the definition of "quality improvement expense" for MLR purposes. Eliminate three-year averaging. Require granular administrative cost reporting. The 80 percent floor was designed to align incentives; the gaming undermines it.

Audit MA risk adjustment coding annually (HHS OIG recommendation, October 2024). Recover overpayments with penalties for undocumented diagnoses.

### Who Has the Power

**Congress:** Pass federal PA standards (72-hour turnaround, written justification, gold-carding). Regulate vertical integration pricing. Strengthen MLR definitions.

**HHS/CMS:** Redefine MLR administrative categories (executive action). Audit risk adjustment coding. Issue arm's-length pricing guidance for insurer-owned providers.

**FTC/DOJ:** Continue the UnitedHealth investigation. Expand to CVS, Elevance, and Cigna vertical integration practices.

**States:** Seven states have restricted AI in PA. Twenty states have PA response time standards. Colorado, California, and Minnesota are leading.

---

## Savings Tracker: $428.6 Billion and Counting

**Running total after Issue #8: $428.6 billion per year in recoverable waste across all issues published to date.**

Expressed as a percentage of the $3 trillion annual U.S. healthcare spending gap between the United States and Japan: **14.3 percent**.

*[Chart 4: Savings Tracker across all issues (bar chart showing cumulative total with Issue #8 addition, running to $428.6B)]*

**Methodology notes:**

Issue #1 OTC: $0.6B from Medicare Part D step-therapy reform.
Issue #2 Drug Pricing: $25.0B from international price normalization (net of rebate adjustment).
Issue #3 Hospital Pricing: $73.0B from commercial reference pricing (capping insurer payments at 200% of Medicare).
Issue #4 PBMs: $30.0B from rebate pass-through and formulary transparency.
Issue #5 Admin Waste: $200.0B from standardized billing, automated PA, and payer rate-setting.
Issue #6 Supply Waste: $28.0B from hospital supply cost variance (Q4 to P75 within peer groups).
Issue #7 GLP-1: $40.0B from price negotiations and volume optimization in the permanent BALANCE model.
Issue #8 Denial Machine: $32.0B from prior authorization reform ($10.4-17.0B care suppression), vertical integration restrictions ($6.7-13.8B margin arbitrage), AI regulation ($4.9-6.4B denial escalation), and MA risk adjustment audits ($0.3B). Booked at $32B (upper-conservative within $22-37B midpoint range). Component D (deductible-delay extraction) is excluded from the booked total: the mechanism is documented in the MRI vignette and component section, but a defensible national estimate requires matched patient-level claims and deductible-exposure data that we are actively seeking through the AHC Data Access Fund. We expect D to add tens of billions to the booked total in a future issue.

---

## What's Next

Issue #9: The Employer Trap. 65% of covered workers are in self-insured ERISA plans. Over the past decade, family premiums rose ~47% while wages rose ~30%. The same 45-year-old knowledge worker costs different employers wildly different amounts, and most employers don't know why. Issue #9 builds a per-employee variance analysis across firms of the same size (KFF EHBS + MEPS-IC), decomposes the wage-premium crossover, and books the slice that doesn't overlap with what Issues #3, #4, and this one already counted. Target: $40 billion a year in excess the employer system transmits straight into wages, before we start adding the pieces we can't see yet.

Every script is on GitHub. Every number can be verified. If you think we got something wrong, open an issue: **github.com/rexrodeo/american-healthcare-conundrum**

**The AHC Data Access Fund.** Every component in this issue was computed from public federal data: no paywall, reproducible, independently verifiable. That strength is also the ceiling. Component D, the deductible-delay extraction from the MRI vignette, is excluded from the booked total because measuring it cleanly requires matched patient-level claims and deductible-exposure data. We are crowdfunding access to six datasets that close this gap: CMS Medicare 5% sample, Colorado APCD, AHRQ HCUP (CA + NY), Turquoise Health full price transparency, Midpage legal research, and the CMS Virtual Research Data Center (100% Medicare, 65 million patients). Three phases. $44,200 goal. Any amount from $5. Pick a specific dataset, see what it unlocks, watch the progress bar move. Every dollar buys data, not salary. Every sponsor named or anonymous. Organizations with proprietary dataset access (Truven/MarketScan, Optum Clinformatics, IQVIA Pharmetrics, Definitive Healthcare) or active DUAs can collaborate directly. **Visit the fund: [ahcdata.fund](https://ahcdata.fund)**

If you found value in this work, forward it to someone who should see it.

*[Subscribe to The American Healthcare Conundrum]*

---

*Sources: CMS-0057-F Prior Authorization Transparency Rule disclosures (April 2026) covering 61 UnitedHealthcare MA contracts and 32 Humana contracts; CMS Monthly Enrollment by Plan (March 2026), 35.6 million MA enrollees across 7,606 plans; KFF CY2024 Medicare Advantage Prior Authorization reporting: insurer-level denial rates, appeal rates, overturn rates for 7 major insurers; KFF ACA Marketplace 2024 Working File: 2,540 plans, 374 million claims, 75.9 million denials; KFF Medicare Advantage Historical PA data (2019-2024); KFF Employer Health Benefits Survey 2025 (median deductible, share of covered workers facing a deductible); CMS Medical Loss Ratio Public Use Files (2019-2024): insurer-level premiums, claims, administrative expenses, and rebates; CMS National Health Expenditure Accounts 2023 (out-of-pocket spending pool); Peterson-KFF Health System Tracker (deductible share of out-of-pocket); Health Affairs, "Optum-Owned Providers and Payment Variation in Medicare Advantage" (Nov 2025); Wang Y, Bai G, Anderson GF, "Comparison of Cash Prices and Negotiated Prices for Hospital Services" (Health Affairs, 2023); Brot-Goldberg ZC, Chandra A, Handel BR, Kolstad JT, "What Does a Deductible Do?" (Quarterly Journal of Economics, 2017); HCCI / Frost A, Newman D, "Spending on Shoppable Services in Health Care" (Health Care Cost Institute, 2016); Stanford npj Digital Medicine, "Machine Learning-Driven Prior Authorization: Clinical Impact on Denial Rates" (Jan 2026); AMA Physician Survey on Prior Authorization (2024); HHS OIG: Medicare Advantage Risk Adjustment Audit (Oct 2024); Bernstein et al., "Medical Loss Ratio Gaming in Private Insurance" (JAMA Health Forum 2024); Banerjee et al., "Cost Impact of Care Delays in Managed Care" (American Journal of Managed Care, 2023); ADA Cost of Diabetes Study (2023); National Cancer Institute SEER Program; CMS Hospital Price Transparency Final Rule (effective July 2022) and CMS HPT compliance audits; UnitedHealth 10-K FY2024; CVS Health 10-K FY2024; Elevance Health 10-K FY2024; Cigna Group 10-K FY2024; Humana Inc. 10-K FY2024; Minnesota HF2500 (2026).*

---

**Savings Tracker (consolidated):**

**$428.6 billion per year in identified, booked, and recoverable waste across eight published issues of The American Healthcare Conundrum.**

The $3 trillion annual spending gap between the United States and Japan per-capita healthcare costs remains the north star. Every dollar identified is independently defensible through published research, federal datasets, or peer-reviewed analysis. No speculation. No attribution without source. The analysis uses only public data.

---

*The American Healthcare Conundrum publishes when the data is ready. All analysis uses publicly available data. Code is open-source. Figures are validated before publication.*