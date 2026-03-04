# The American Healthcare Conundrum
### Issue #1 — *We're Paying 2.5× What Japan Pays. They Live Longer.*

---

*The Healthcare Conundrum is an investigative data journalism project. Each issue identifies one fixable problem in the US healthcare system, quantifies the waste, and recommends a specific solution. We're building an open-source analysis pipeline to do it. Every number is reproducible. Here's how we track progress:*

---

**SAVINGS TRACKER**

```
Issue #1  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0.02%
          $0.6 billion recovered of a ~$3 trillion annual target
```

*The target is set by Japan — the country with the highest life expectancy in the developed world, the lowest infant mortality rate in the OECD, and a healthcare bill less than half the size of ours. If the US matched Japan's per-capita spending, we'd free up nearly $3 trillion a year. We're going to spend this newsletter series finding out where that gap goes.*

---

## Japan Lives Longer. Pays Less. What's Going On?

In 2023, the United States spent **$14,570 per person on healthcare** — the highest of any country on earth by a wide margin.

Japan spent **$5,790 per person**. And Japan has:

- The **highest life expectancy in the developed world** — 84 years, compared to 78.4 in the US
- The **lowest infant mortality rate in the OECD** — 1.7 deaths per 1,000 live births, compared to 5.6 in the US
- Universal healthcare coverage for all 125 million of its citizens

The United States, meanwhile, ranks **last among high-income countries** on the Commonwealth Fund's 2024 global health system scorecard — dead last on avoidable deaths, last on equity, last on overall outcomes. We're not just paying more. We're paying more and getting less.

The gap between what the US spends per person and what Japan spends per person, multiplied across 335 million Americans, is nearly **$3 trillion a year**.

That's not a statistic. That's a crime scene.

---

## What We're Doing About It

We're not going to write one article and call it a day.

This newsletter is a series — a running investigation. Each issue picks one specific, documented source of healthcare waste, runs the numbers from public data, and puts a dollar figure on the fix. We publish the code. We publish the methodology. We publish the caveats. Anyone can check our work.

At the top of every issue, you'll see the Savings Tracker above — a running total of the waste we've identified and what fixing it would save per year. We started at zero. After this issue, we have our first $600 million.

It's 0.02% of the gap with Japan. We're just getting started.

---

## Issue #1: The $2 Billion Heartburn Tab

Go to any CVS or Walgreens in America. Walk to the pharmacy counter. Pick up a prescription for omeprazole — the generic version of Prilosec, the most common heartburn drug in the country. The pharmacist hands it to you. Medicare pays.

Then walk fifteen feet to the antacid aisle. There's Prilosec OTC. Same active ingredient. Same 20mg dose. Same FDA approval. $14 for a 42-day supply — about 33 cents a pill.

Generic omeprazole has actually become so cheap that Medicare pays *less* per tablet than Prilosec OTC — about 20 cents versus 33 cents on the drugstore shelf. But related drugs in the same heartburn class tell a different story. Medicare paid **nearly $1 per tablet** for esomeprazole, the generic version of Nexium, and **over $100 per unit** for specialty omeprazole formulations like Zegerid. On 83 million claims for drugs like these that have over-the-counter equivalents, Medicare spent **$2 billion in a single year**.

We know this because we built a pipeline and looked.

---

## The Data

Using the Centers for Medicare & Medicaid Services (CMS) Medicare Part D Spending by Drug dataset — public data, downloadable from data.cms.gov — we matched every drug in the Part D formulary against a list of medications available over-the-counter in the same pharmacies where those prescriptions are being filled.

After running validation checks and removing false matches (more on that below), we found:

**In 2023:**
- **$2.0 billion** in Medicare Part D spending on drugs with OTC equivalents
- **83 million claims** covering those drugs
- **28 million beneficiaries** affected
- **Estimated savings** if those patients had used the OTC version: **$600 million**

The trend over five years tells a more complicated story. Medicare has consistently spent around $2 billion a year on these drugs since 2019. The overall savings opportunity has declined — from $1.05 billion in 2019 to $600 million in 2023 — but that headline number obscures two very different things happening underneath it.

Almost the entire decline is attributable to a single drug: esomeprazole (Nexium). The potential savings on esomeprazole fell by roughly $217 million between 2019 and 2023, likely because generic esomeprazole pricing has dropped sharply and Medicare volumes have shifted. That is credit where it is due — market forces appear to be doing some of the work on that one drug, even without a formal OTC-steering policy.

The rest of the picture is not as encouraging. The gaps are actually growing for famotidine (+$92 million), nasal steroids like fluticasone and mometasone (+$35–66 million each), and several others. If you strip esomeprazole out, the remaining savings opportunity is expanding, not contracting. The policy window is narrowing on Nexium; it is widening on Flonase and Pepcid. That distinction matters enormously for which drugs a reform should target first.

The drugs where the gap is largest include:

**Heartburn medications (PPIs):** Esomeprazole (Nexium), lansoprazole (Prevacid), and famotidine (Pepcid) — all available OTC — cost Medicare dramatically more per unit than their shelf equivalents. Specialty formulations of omeprazole combined with sodium bicarbonate (Zegerid) show per-claim costs over $5,800, compared to a monthly OTC cost of under $10.

**Allergy and nasal sprays:** Azelastine (Astepro), mometasone (Nasonex), and cetirizine (Zyrtec) are all available without a prescription. Medicare pays unit prices ranging from 5× to 679× the OTC equivalent, depending on formulation.

**NSAIDs:** Ibuprofen and naproxen — both available in 500-count bottles at Costco for under $20 — appear on Medicare Part D claims at higher per-unit costs than retail.

---

## A Note on Methodology (This Is Part of the Story)

When we first ran this analysis, we got a bigger number: $1.57 billion in potential savings. We ran a validation pass and caught several errors that took it down to $600 million.

The errors were instructive. Fluticasone propionate — one molecule — covers both Flovent HFA, an asthma inhaler with no OTC equivalent, and Flonase, an allergy nasal spray you can buy at any drugstore. Our initial query matched both. The asthma inhaler isn't OTC-equivalent. We removed it. Same issue with dexlansoprazole (Dexilant) — sounds like lansoprazole, but it's a different drug, prescription-only.

We also removed drugs that matched only on a component — H. pylori triple-therapy antibiotics that contain a PPI, hydrocodone combinations that contain ibuprofen. Those aren't OTC drugs. The ibuprofen component is, but the full prescription isn't.

The right number for this analysis is $600 million. Not $1.57 billion. We're going to be precise about this because the point isn't to write a scary headline — it's to make a policy case that holds up.

All code, all exclusion logic, and the full validation report are [published on GitHub](https://github.com/rexrodeo/american-healthcare-conundrum).

---

## Why Does This Happen?

Medicare Part D is legally required to cover prescription drugs. When a physician writes a prescription for omeprazole — even though it's been available over the counter since 2003 — the plan pays.

The fact that a patient could walk to the next aisle and buy the same molecule for a dollar is, from Medicare's legal standpoint, irrelevant.

There's also a structural incentive problem. Pharmacy benefit managers — the intermediaries who negotiate between insurers and drug manufacturers — earn administrative fees and rebates based on the transaction. A prescription filled through Part D generates that revenue. A patient buying Prilosec OTC generates nothing for anyone in the chain except the pharmacy and the patient.

The result is a system that has no financial reason to route patients toward the OTC shelf, even when the OTC version is clinically identical and substantially cheaper.

---

## The Fix

The fix is administratively straightforward: **CMS should require OTC-equivalent step therapy** before covering the prescription version of any drug that has an FDA-approved OTC equivalent at the same active ingredient and dose.

In practice, this means: if your doctor prescribes omeprazole, the Part D plan directs you to try the OTC version first. If OTC treatment fails — documented by the prescriber — coverage of the prescription version kicks in. This is already standard practice for brand-name drugs that have generic equivalents. The same logic applies here.

A complementary fix: CMS could update its formulary guidance to make OTC-equivalent alternatives a required first line of treatment, without new legislation. Congress passed the Inflation Reduction Act in 2022 to let Medicare negotiate a small list of high-cost drugs. CMS can act on OTC equivalents today through administrative guidance.

**Estimated annual savings from this fix: $600 million.**

That's about 3,600 additional nurses at median salary, every year, indefinitely. Or — since this newsletter has a Japanese benchmark — it's the kind of administrative efficiency that doesn't require you to build a new system. It just requires looking at what's on the shelf.

---

## Next Issue

This was the easy one. Oral generic heartburn drugs. Allergy pills. Ibuprofen. Low-hanging fruit.

Issue #2 goes after a larger target: the price differential between what Medicare pays for brand-name drugs and what peer countries pay for identical molecules. Germany, France, and Japan all negotiate drug prices nationally. The US, for most drugs, does not. The gap is not small.

We're also extending the OTC analysis — there are more drugs on the list that we didn't include in this issue. The full scope of OTC-equivalent waste is larger than $600 million, and we'll refine the number as the methodology improves.

If you want to follow the code: https://github.com/rexrodeo/american-healthcare-conundrum

If you want to push back on the methodology: reply to this email, or leave a comment below if you're reading on the web or app.

If you know a CMS official who should read this: forward it.

---

*The Healthcare Conundrum publishes when the data is ready. All analysis uses publicly available CMS data. Code is open-source. Figures are validated before publication.*

*Sources: CMS National Health Expenditure Fact Sheet (2023); CMS Medicare Part D Spending by Drug dataset, 2019–2023; OECD Health at a Glance 2025; Commonwealth Fund Mirror, Mirror 2024; Peterson-KFF Health System Tracker; Socal et al., JAMA Health Forum, December 2023.*

---

**Savings Tracker — Running Total After Issue #1: $0.6 billion / ~$3 trillion (0.02%)**

*The ~$3 trillion target represents the annual gap between US per-capita healthcare spending ($14,570) and Japan's per-capita spending ($5,790), applied to the US population of 335 million — a difference of $8,780 per person. Japan has the highest life expectancy in the developed world (84 years) and the lowest infant mortality rate in the OECD (1.7 per 1,000). Sources: OECD Health at a Glance 2025; CMS National Health Expenditure Data 2023; Peterson-KFF Health System Tracker; Commonwealth Fund Mirror Mirror 2024.*
