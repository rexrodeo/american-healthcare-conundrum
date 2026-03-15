# The American Healthcare Conundrum
### Issue #3 — *The 254% Problem: Why a Hip Replacement Costs $29,000 in America and $10,000 Almost Everywhere Else*

---

*The American Healthcare Conundrum is an investigative data journalism project. Each issue identifies one fixable problem in the US healthcare system, quantifies the waste, and recommends a specific solution. We publish the code. We publish the methodology. We publish the caveats. Anyone can check our work.*

---

**SAVINGS TRACKER**

```
Target: ~$3T US-Japan per-capita gap
Japan: highest life expectancy, lowest
infant mortality in OECD — ~half US cost

Full scale: $0 ──────────────── $3T
            ██░░░░░░░░░░░░░░░  3.3%
            ↑ $98.6B identified

Zoomed (first $100B):
 #1  ░  $0.6B   OTC Drug Overspending
 #2  ████  +$25.0B  Drug Pricing
 #3  ███████████  +$73.0B  Hospitals
     ─────────────────────────────
     Total: $98.6B · $2,901B remaining
```

---

## Issue #3: The $29,000 Hip Replacement

A quick number to keep in mind: **254.**

That's the percentage of Medicare rates that commercial insurers — your employer's health plan, your marketplace plan — pay US hospitals for the same inpatient procedures that Medicare covers. Not 254 dollars. **254 percent.** The government pays hospitals $15,000 for a hip replacement. Your private insurer pays $29,000 for the identical operation at the same hospital, performed by the same surgeon.

This is not a secret. It is the headline finding of the RAND Corporation's Round 5.1 Hospital Pricing Study — the most rigorous commercial claims analysis ever conducted. More than 4,000 hospitals. Four million admissions from employer-sponsored health plans. Published 2023. Peer reviewed. Unambiguous.

The question is: why does it persist?

---

## The Same Procedure. A Very Different Price.

Let's start with what we can measure directly.

The International Federation of Health Plans (iFHP), in collaboration with the Health Care Cost Institute (HCCI), surveys insurers across 24 countries and collects actual median insurer-paid amounts for identical procedures. Their 2024-2025 report — which we have the primary source for — covers 2022 data across nine countries. Here is what it shows for four common procedures:

**Hip replacement:** US commercial, **$29,006**. Germany, $14,986. New Zealand, $10,944. UK, $9,641. Spain, $9,105. You are paying roughly 2–3× the peer median.

**Coronary bypass surgery:** US, **$89,094**. Germany, $24,044. UK, $16,936. New Zealand, $15,183. Spain, $10,734. The US is buying the same surgery at 3.7–8.3× the price of European peers.

**Appendectomy:** US, **$13,601**. Australia, $7,097. Germany, $5,479. Spain, $4,268. UK, $3,980. A necessary emergency procedure, not an elective upgrade. The US costs 3× what the UK pays.

**Knee replacement:** US, **$26,340**. Germany, $15,216. New Zealand, $12,243. UK, $9,563. Spain, $9,006.

The pattern is so consistent across procedures, countries, and payers that the international cost comparison functions as a controlled experiment. Same technology. Dramatically lower prices — with no measurable penalty in outcomes.

**A note on measuring outcomes.** The OECD's PaRIS initiative (Patient-Reported Indicator Surveys) collects standardized patient-reported outcome measures (PROMs) for hip and knee replacement across 13 programs in 9 countries — including Germany, the UK, Sweden, Australia, and New Zealand. All 13 programs report clinically significant improvement in functional scores (Oxford Hip Score: +21 points, ~44% improvement) and quality of life (EQ-5D: +0.25) at 6–12 months post-surgery. Outcomes are comparable across participating systems. The US does not have a universal national PROM registry — the American Joint Replacement Registry is hospital opt-in and not included in OECD's international comparison — so direct procedure-level US-vs.-peer outcome comparison isn't available from published data. What we can say: the countries charging 2–3× less are participating in rigorous international outcome benchmarking and showing results equivalent to published US clinical benchmarks. *(Source: OECD Working Paper No. 148, "International Comparisons of Patient-Reported Outcomes Following Hip and Knee Replacement," 2022.)*

*[Chart 1: International Procedure Price Comparison]*

---

## Five Ways to Price the Same Hip

Here is a chart that deserves to be required reading for every member of the House and Senate Commerce Committees.

For a hip replacement — one of the most common elective procedures in the US, with 450,000+ performed annually — there are five economically distinct "prices" in the American system:

**Actual hospital cost: ~$12,000.** This estimate is derived from CMS's own rate-setting methodology. CMS sets the DRG 470 rate at approximately $15,000 after wage-adjustment for a typical large teaching hospital. The IPPS rate is designed to cover operating costs plus a reasonable margin — CMS's cost-finding methodology targets coverage at roughly 125% of actual cost. Working backward: $15,000 ÷ 1.25 = **$12,000**. This is corroborated by CMS HCRIS cost reports, which every Medicare-participating hospital files annually. The cost-to-charge ratio (CCR) for large academic medical centers averages ~0.30 — roughly 30 cents of operating cost for every dollar of gross billed charges. (Note: the CCR reflects the full hospital cost/charge distribution, not a single-procedure ratio; the $12,000 figure is anchored to the Medicare rate derivation.)

**International peer average: $11,169.** Germany pays $14,986. Spain pays $9,105. UK pays $9,641. New Zealand pays $10,944. The average of these four peers is $11,169. Comparable surgical facilities, comparable implant devices, comparable patient outcomes. The peer average is roughly equal to the actual US hospital cost — meaning peer countries are essentially paying operating cost, with a modest margin built into their national tariff systems.

**Medicare rate: ~$15,000.** CMS sets this via the Inpatient Prospective Payment System (IPPS), using a DRG-weighted base rate. DRG 470 (major joint replacement without major complications) at FY2024 rates, wage-adjusted for a typical large teaching hospital: approximately $15,000. (CMS IPPS FY2024 Final Rule Table 5, CMS-1785-F: DRG 470 relative weight 1.8817.) Medicare pays 25% above actual operating cost — a reasonable margin for a well-run institution.

**US commercial rate: $29,006.** This is what private insurers actually pay, per the iFHP/HCCI primary-source data for 2022. Not the list price. Not a worst-case outlier — the median insurer-paid amount. The commercial rate is 93% above Medicare. 142% above actual cost. 160% above the international peer average.

**Chargemaster list price: ~$73,000.** This is what uninsured patients are billed. Almost no one pays it — hospitals are legally required to offer financial assistance to low-income patients, and most negotiate steep "self-pay discounts" on top of that. But *knowing* you qualify for charity care requires navigating a system that has no incentive to tell you. The chargemaster exists because of history and strategy: it originated as a billing list when Medicare arrived in 1965 and needed a "list price" to discount from. It persists because commercial insurance contracts are often structured as "X% off chargemaster" — which means hospitals have a direct incentive to keep inflating the list. The higher the chargemaster, the more room to offer a "discount" while preserving or growing net revenue. Reference pricing severs this mechanism entirely, which is part of why the hospital lobby opposes it.

*[Chart 2: The Price Stack — Hip Replacement]*

The $14,000 gap between Medicare and commercial for hip replacement illustrates the problem — and hip replacement is actually one of the *better-negotiated* common procedures. RAND's Round 5.1 finds that across all inpatient services, commercial payers average 254% of Medicare. For hip replacement specifically, the ratio is 1.93× — still nearly double Medicare, and 2.6× the international peer average, and 3.0× the UK price. The procedures where commercial rates spike highest tend to be less common and harder to shop: cardiac surgery, neurosurgery, oncology.

---

## 3,193 Hospitals. Computed From Raw Federal Data.

The cost-to-charge ratio analysis above is not drawn from a single published study. It is derived from the raw HCRIS cost reports that CMS requires hospitals to file under 42 CFR §413.20, and that CMS makes publicly available at downloads.cms.gov.

For this issue, we downloaded the complete FY2023 HCRIS HOSP10-REPORTS file and computed CCRs for **3,193 acute-care hospitals** with more than $5M in operating costs. The results:

The median hospital in our analysis charges **2.6× its operating costs.** More than one-third — **37%** — of hospitals charge 3× or more, and the distribution has a long right tail: some hospitals carry markups above 8–10×. When weighted by commercial claims volume — the methodology used by RAND and HCCI, which gives more weight to large hospitals handling the bulk of commercially-insured patients — the effective benchmark is higher. HCCI's peer-reviewed analysis reports a median charge-to-cost ratio of 3.5× for commercially-relevant hospitals. Large academic medical centers in our data confirm this pattern: Cedars-Sinai, 3.5×; NYU Langone, 3.2×.

This is not fraud — it is the rational behavior of institutions operating in a market with no price ceiling for commercial payers. When Medicare pays $15,000 for a procedure and a commercial insurer will pay $29,000 for the identical service, the rational hospital maximizes volume at the commercial rate. The chargemaster becomes the anchor. The commercial negotiation starts from the chargemaster.

Contrast this with regulated systems: German and Spanish hospitals operate under fixed all-payer DRG tariffs set by national rate-setting bodies, with effective margins in the low single digits. They are profitable. They invest in technology. They train physicians. They are not running charities — they are simply operating in an environment where the price is set, not negotiated upward from an opaque list.

*[Chart 3: Hospital Markup Distribution — 3,193 US Hospitals, HCRIS FY2023]*

---

## The Mechanism: Why Prices Stay High

Three structural factors maintain the 254% commercial premium:

**1. Chargemaster opacity and anchoring.** Until the Hospital Price Transparency rule (effective 2021, enforcement still weak), hospitals were not required to publish their negotiated rates. The chargemaster served as both invoice and negotiating anchor. Even with the transparency rule in place, compliance remains incomplete — and rate comparison remains technically difficult for most buyers.

**2. Hospital consolidation.** Between 2010 and 2022, the number of hospital mergers and acquisitions exceeded 1,500. RAND, JAMA, and the FTC have all documented the same effect: when a hospital system acquires its regional competitors, commercial prices rise 20–40% within two years. Consolidation converts competitive markets into regional monopolies, and monopolists set prices above competitive equilibrium. There are now markets — Pittsburgh, Boston, Dallas — where a single system controls 60–80% of inpatient capacity.

**3. No reference price for commercial buyers.** Medicare's administered price creates a functional ceiling for government spending — but not for commercial payers. Unlike France, Germany, and Japan, which set all-payer rates, the US allows each commercial insurer to negotiate bilaterally with each hospital. The result: large insurers extract modest discounts off the chargemaster, small employers and individuals pay more, and the aggregate commercial average settles at 254% of Medicare. Montana demonstrated the alternative in 2016, when it capped state employee plan hospital payments at 234% of Medicare. The independent analysis published by the National Academy for State Health Policy documented **$47.8 million in inpatient and outpatient savings** over the first three fiscal years — without a single hospital dropping out of network.

---

## Who Profits

> **Who Profits: HCA Healthcare (HCA)**
> FY2024 Revenue: $70.6B | Operating Margin: 12.1% | Net Income: $5.8B
> CEO Comp (Sam Hazen): $23.8M | CEO-to-Worker Pay Ratio: 391:1
> Stock Buybacks (2022–2024): ~$16.8B | Lobbying (2021): $3.5M
> **This issue's mechanism:** HCA is the largest for-profit hospital system in the US, operating 186 hospitals and approximately 2,400 care sites. It is the direct beneficiary of the commercial pricing premium documented above. When commercial insurers pay 254% of Medicare for inpatient services, the excess margin flows to HCA's shareholders. In 2024, HCA returned more to shareholders through stock buybacks (~$6B) than most hospital systems spend on patient care in a year.

*This is the first installment of a recurring sidebar. Each issue that implicates a publicly traded company will profile the entity that profits from the mechanism under examination. The sidebar is data only. Sources: HCA Healthcare 10-K and DEF 14A proxy statement (SEC EDGAR); OpenSecrets.org; company earnings releases.*

---

## The Fix: Commercial Reference Pricing

The policy is straightforward. Montana proved it works. Thousands of self-insured employers are implementing versions of it right now.

**Commercial reference pricing** caps what commercial insurers pay hospitals at a defined multiple of Medicare rates — typically 150–200%. The policy does not tell hospitals what to charge. It tells payers what they are allowed to pay. Hospitals remain free to set their chargemaster anywhere. They just cannot collect more than the reference rate from covered payers.

**Why 200% of Medicare?** At the DRG 470 Medicare rate of ~$15,000 for a hip replacement, 200% = **$30,000**. That is more than twice the hospital's actual operating cost of $12,000. It is more than double the international peer average. It is a generous rate — it preserves an operating margin that supports capital investment, clinical education, and research. What it does not preserve is the 254% premium that flows disproportionately to hospital system executives and, in the for-profit sector, to shareholders.

**The savings math.** CMS National Health Expenditure accounts show **$1.36 trillion** in total US hospital spending in 2023. Private health insurance accounts for approximately **38.8%** of that — roughly **$528 billion**. Not all of that is addressable: capitated contracts (where hospitals are paid a fixed monthly amount per patient regardless of procedures performed, eliminating per-procedure pricing), out-of-network payment caps, and plans already negotiating below 200% of Medicare together account for roughly 35% of commercial hospital spending. The addressable fraction — traditional fee-for-service commercial contracts where the 254% premium is fully in play — is approximately **65%**, or **$343 billion**. Bringing those contracts from 254% to 200% of Medicare requires an average price reduction of 21.3%. The math: $343B × 21.3% = **$73 billion per year**. That is what we carry in the Savings Tracker.

*[Chart 4: Reference Pricing Savings Scenario]*

To be explicit about what this does *not* include: no savings from outpatient procedures (a growing share of hospital revenue with similar commercial premia); no savings from Medicare Advantage hospital pricing; no second-order effects from consolidation reversal via FTC enforcement. This is strictly the inpatient commercial pricing gap, conservatively scoped.

---

## What Would Actually Have to Change

This is not a technocratic fix. It requires political will to confront the hospital lobby — among the best-funded in Washington. The American Hospital Association alone spent **$29 million lobbying in 2024** (OpenSecrets). That's just the trade association; individual hospital systems and for-profit chains layer in tens of millions more on top. Hospital systems are also among the largest employers in most congressional districts, which creates structural legislative resistance independent of any checkbook.

The viable legislative pathways, in rough order of political tractability:

**Reference pricing for federal employee plans** (FEHB covers 8M+ lives): Congress could mandate it unilaterally for its own employees. Estimated savings: $6–8B/year. A proof of concept.

**Medicaid all-state reference pricing**: CMS could condition federal Medicaid matching funds on states adopting reference pricing. Montana's program already uses 234% of Medicare. Scaling nationally would generate $15–20B in state plus federal savings.

**ACA marketplace plans**: Reference pricing could be required for qualified health plans sold on the exchanges as a condition of federal subsidy eligibility. Coverage affects ~15 million people.

**Employer plan safe harbor**: Self-insured employers using reference pricing face the risk of balance billing litigation. Federal legislation creating a clear safe harbor — similar to the No Surprises Act for emergency care — would accelerate adoption. Thousands of employers are already there; tens of thousands would follow with legal cover.

**All-payer reference pricing** (the full version): Effective immediately in any Congress willing to confront the hospital lobby. Saves $73B+/year in year one, scaling up as contracts renew.

None of these requires technological innovation. None requires new agencies. The data infrastructure — Medicare's DRG rate schedule — already exists. The gap is political will.

---

## Savings Tracker: $98.6 Billion and Counting

After three issues:

- **Issue #1** — OTC Drug Overspending: **$0.6B/year**
- **Issue #2** — Drug Reference Pricing (brand-name drugs vs. international peers): **$25.0B/year**
- **Issue #3** — Hospital Commercial Reference Pricing: **$73.0B/year**

**Running total: $98.6B/year — 3.3% of the $3 trillion annual gap between US and Japanese per-capita healthcare spending.**

We are $98.6 billion into a three trillion dollar problem. The hospital sector alone has identified multiples of this number in correctable inefficiency. Future issues will cover: outpatient pricing, administrative overhead, the hundreds of billions in unnecessary procedures driven by fee-for-service incentives, pharmaceutical pricing (Round 2), and more.

The math on fixing American healthcare is not complicated. The politics are. The purpose of this newsletter is to make the math so clear that the politics have nowhere to hide.

*[Chart 5: Savings Tracker — 98.6B of 3T Gap]*

---

## What's Next

Issue #3 examined what hospitals charge. Issue #4 examines who stands between the pharmacy and the patient.

Three companies — CVS Caremark, Express Scripts, and OptumRx — process 80% of the 6.6 billion prescriptions Americans fill each year. They are called Pharmacy Benefit Managers, and most patients have never heard of them. The FTC has. In 2024, the Commission published the most detailed investigation of PBM business practices ever conducted and documented billions in markups, opaque rebate flows, and formulary manipulation that systematically favors expensive brand drugs over cheaper generics. In September 2024, the FTC sued all three over insulin pricing alone.

Issue #4 follows the money through the prescription drug supply chain — from manufacturer rebate to PBM spread to patient copay — and asks why the middlemen keep more than the pharmacies that actually dispense the drugs.

If you want to follow the code: [github.com/rexrodeo/american-healthcare-conundrum](https://github.com/rexrodeo/american-healthcare-conundrum)

If you want to push back on the methodology: reply to this email, or leave a comment below.

If you know someone who works in pharmacy, insurance, or drug pricing policy who should read this: forward it.

---

*Sources: CMS HCRIS HOSP10-REPORTS FY2023 (downloads.cms.gov); RAND Corporation, "Nationwide Evaluation of Health Care Prices Paid by Private Health Plans," Round 5.1, 2023; International Federation of Health Plans, "2024-2025 International Health Cost Comparison Report" (produced with HCCI), primary source; Peterson-KFF Health System Tracker, US vs. peer-nation procedure cost comparisons; CMS National Health Expenditure Accounts 2023 (cms.gov/research-statistics-data-and-systems/statistics-trends-and-reports/nationalhealthexpenddata); CMS IPPS FY2024 Final Rule Table 5 (CMS-1785-F), DRG 470 relative weight 1.8817; National Academy for State Health Policy (NASHP), "Independent Analysis: Estimating the Impact of Reference-Based Hospital Pricing on the Montana State Employee Plan," April 2021 (nashp.org/wp-content/uploads/2021/04/MT-Eval-Analysis-Final-4-2-2021.pdf); OpenSecrets.org, American Hospital Association federal lobbying expenditures, 2024 (opensecrets.org/orgs/american-hospital-assn/lobbying?id=D000000116); American Hospital Association Annual Survey / Irving Levin Associates Health Care M&A Report, hospital consolidation 2010–2022.*

---

**Savings Tracker — Running Total After Issue #3: $98.6 billion / ~$3 trillion (3.3%)**

*The tracker image above shows two panels: the full $3T scale (where $98.6B is a thin sliver at the far left), and a $100B zoom window showing per-issue contributions. The sliver is the point — the gap is enormous, and we are mapping it piece by piece.*

*Issue #1 ($0.6B): OTC-equivalent step therapy for Medicare Part D — savings from requiring patients to try OTC alternatives before prescription coverage activates. Issue #2 (+$25.0B): International reference pricing for Medicare brand drug negotiations — benchmarking against the average paid by Germany, France, Japan, UK, and Australia, applied to high-spend brand drugs; $25B figure applies a ~49% net adjustment to gross savings of $48.9B. Issue #3 (+$73.0B): Commercial hospital reference pricing — capping commercial insurer payments at 200% of Medicare for inpatient services. Methodology: $528B commercial hospital spend × 65% addressable fraction × 21.3% price reduction (254%→200% of Medicare) = $73B. Sources: RAND Round 5.1 (commercial = 254% of Medicare); CMS NHE 2023 (private insurance = 38.8% of $1.361T hospital spend).*

*The ~$3 trillion target represents the annual gap between US per-capita healthcare spending ($14,570) and Japan's per-capita spending ($5,790), multiplied by the US population of 335 million. Japan has the highest life expectancy in the developed world (84 years) and the lowest infant mortality rate in the OECD (1.7 per 1,000). Sources: OECD Health at a Glance 2025; CMS National Health Expenditure Data 2023; Peterson-KFF Health System Tracker; Commonwealth Fund Mirror Mirror 2024.*

---

*The American Healthcare Conundrum publishes when the data is ready. All analysis uses publicly available data. Code is open-source. Figures are validated before publication.*
