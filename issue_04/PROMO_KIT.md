# Issue #4 Promo Kit — "The Middlemen" (PBMs)

**Publish date:** Sunday, March 22, 2026
**Substack:** Scheduled and injected (22/22 audit passed)
**Savings booked:** $30.0B/year
**Running total:** $128.6B / $3T (4.3%)

---

## Distribution Strategy

HN is our primary growth channel. GitHub is our storefront. LinkedIn is a notification system. Everything routes readers to the GitHub repo first, where the open-source code builds trust, then to the Substack for the full analysis. Do not link Substack directly on HN (anti-promotion norms). Do not post from Andrew's personal LinkedIn (day job separation).

**Sequence on Sunday March 22:**
1. Issue #4 goes live on Substack (auto-scheduled)
2. Git commit + push Issue #4 code to GitHub (`issue_04/`, figures, `newsletter_issue_04_FINAL.md`)
3. Update GitHub README with "Latest Issue" callout
4. Submit Show HN post (link to GitHub repo, not Substack)
5. Create AHC LinkedIn Company Page (linkedin.com/company/setup — see setup details below)
6. Post Issue #4 announcement from AHC LinkedIn page
7. Comment on Mark Cuban's LinkedIn post (from AHC page)
7. Submit supplemental DOL comment with Substack link (before Apr 15, not necessarily Sunday)

---

## 1. Show HN Post

**Title:**
```
Show HN: We quantified PBM extraction at $30B/yr using FTC data and CMS Part D files (open-source)
```

**URL:** `https://github.com/rexrodeo/american-healthcare-conundrum`

(Link to repo, not Substack. HN readers click through to code first. The repo README links to the newsletter.)

**Comment to post immediately after submission (from your HN account):**

```
Author here. This is Issue #4 of an investigative series quantifying fixable
waste in US healthcare. We identified six distinct PBM extraction mechanisms
totaling ~$30B/year:

- Spread pricing: $3B (Ohio State Auditor found $224.8M from one state alone)
- Rebate opacity: $10B (Senate Finance + IQVIA data)
- Specialty drug markup: $1.5B (FTC documented $7.3B over 5 years)
- Formulary manipulation: $10B (biosimilar adoption near 0% where rebate
  contracts favor brands)
- Admin/network fees: $5.5B

The FTC settled with Express Scripts on Feb 4 and projects $7B in savings
over a decade from one PBM. Congress enacted rebate pass-through in the CAA
2026, but commercial plans don't get it until 2029.

All analysis uses CMS Part D public use files, FTC interim reports, state
audit data, and Mattingly et al. (JAMA Health Forum, 2023). Code and
methodology are in the repo. Happy to answer questions about the data.
```

**Why this works on HN:**
- "Show HN" signals original work, not blogspam
- Links to code, not a newsletter
- Author comment leads with specific numbers and sources
- Invites methodological scrutiny (HN loves this)
- No marketing language, no calls to action beyond "happy to answer questions"

---

## 2. AHC LinkedIn — Inaugural Post (post immediately after creating the page)

This goes up as soon as the page exists. It establishes the project before Issue #4 drops Sunday.

```
The United States spends $14,570 per person on healthcare.
Japan spends $5,790. Its citizens live six years longer.

That gap is roughly $3 trillion a year. We started asking where it goes.

The American Healthcare Conundrum is an investigative data journalism
project. Each issue identifies one fixable problem, quantifies the waste
using publicly available federal data, and recommends a specific policy
solution. All code and methodology are open-source.

Three issues published. $98.6 billion in addressable savings identified
so far across OTC drug overspending, international drug pricing gaps,
and hospital commercial pricing. Fourth issue drops Sunday.

We publish the caveats. We publish the code. Anyone can check the work.

Read the series: andrewrexroad.substack.com
Check the code: github.com/rexrodeo/american-healthcare-conundrum
```

---

## 3. AHC LinkedIn — Issue #4 Post (Sunday March 22)

**Create the page first** at linkedin.com/company/setup if not already done. Use:
- Name: The American Healthcare Conundrum
- Tagline: Investigative data journalism. One problem, one number, one fix.
- Website: andrewrexroad.substack.com
- Industry: Online Media
- Logo: Use the AHC branding (navy background, red title text, gold accent)

**Post text:**

```
Three companies process 80% of the 6.6 billion prescriptions Americans fill
each year.

The FTC spent two years investigating them and documented billions in
extraction. Congress enacted reform in February 2026. The FTC secured its
first settlement days later.

Issue #4 of The American Healthcare Conundrum quantifies the six mechanisms:
spread pricing, rebate retention, specialty drug markup, formulary
manipulation, network self-preferencing, and independent pharmacy destruction.
Total: $30 billion per year.

All code and methodology are open-source.

Read the full analysis: [Substack link]
Check the code: [GitHub link]
```

**Formatting notes:**
- No hashtags (they look spammy on company pages for this audience)
- No emojis
- Keep it under 150 words
- Link to both Substack (for the reader) and GitHub (for the skeptic)

---

## 4. Cuban LinkedIn Comment

**Post this as a comment on Mark Cuban's March 18 post** (from AHC LinkedIn page):

```
We quantified the six PBM extraction mechanisms at $30 billion per year using
FTC data, CMS Part D spending files, and state audit records. Ohio's auditor
found $224.8 million in spread pricing from a single state in a single year.
The FTC documented $7.3 billion in specialty drug markups over five years.
Biosimilar adoption is near zero where formulary rebate contracts favor
brand originators.

Full analysis with open-source code published today:
github.com/rexrodeo/american-healthcare-conundrum
```

**Why from the AHC page, not personal:**
- Keeps Andrew's personal LinkedIn clean (day job)
- Consistent branding (comments from a publication carry different weight than from an individual)
- Cuban's audience sees a research project, not a person with an opinion
- Links to GitHub (the trust signal), not Substack

---

## 5. GitHub README Update

Add to the top of README.md, below the project description:

```markdown
### Latest Issue

**Issue #4 — "The Middlemen": Pharmacy Benefit Managers** (March 22, 2026)
Six extraction mechanisms. $30 billion per year. FTC data, CMS Part D files,
state audits. [Read on Substack](https://andrewrexroad.substack.com) ·
[View the code](issue_04/)

Running total: **$128.6B** of $3T target identified (4.3%)
```

Also add a contributor callout responding to Issue #2 ("How can we help?"):

```markdown
### Want to Help?

Pick a data point from any published issue and verify it against the source.
Open a PR or issue with what you find. We're especially looking for:
- International drug price verification (Issues #2, #7)
- HCRIS data validation (Issues #3, #6)
- State PBM audit data beyond Ohio and Kentucky (Issue #4)
```

---

## 6. DOL Supplemental Comment

**Not Sunday. Submit anytime before April 15.**

Go to regulations.gov/commenton/EBSA-2026-0001-0001 and submit a brief supplemental:

```
Supplemental to comment submitted March 18, 2026, by The American Healthcare
Conundrum.

The full quantitative analysis referenced in our original comment has been
published with open-source methodology:

Newsletter: https://andrewrexroad.substack.com/p/[issue-4-slug]
Code and data: https://github.com/rexrodeo/american-healthcare-conundrum/tree/main/issue_04

The analysis documents six PBM extraction mechanisms totaling $30 billion
annually and supports the proposed rule's disclosure requirements for spread
pricing, manufacturer payments, and formulary placement incentives.

Andrew Rexroad
The American Healthcare Conundrum
```

---

## Timing Checklist (Sunday March 22)

- [ ] Issue #4 auto-publishes on Substack (confirm it went live)
- [ ] `git add issue_04/ newsletter_issue_04_FINAL.md` + commit + push
- [ ] Update README.md with Latest Issue + contributor callout
- [ ] Submit Show HN post with GitHub link
- [ ] Post author comment on HN immediately after
- [ ] Create AHC LinkedIn Company Page (if not done)
- [ ] Post Issue #4 announcement from AHC LinkedIn page
- [ ] Comment on Cuban's post from AHC LinkedIn page
- [ ] Check HN monitor digest for any related threads to engage with
- [ ] Update PROJECT_JOURNAL.md with publish date and engagement actions

---

## Metrics to Track After Publish

- GitHub stars (track daily for 7 days post-publish)
- HN post points and comments
- Substack subscriber count (check dashboard Mon morning)
- Substack email open rate for Issue #4
- LinkedIn page followers (baseline → +7 days)
- DOL docket views (check if comment gets cited)

---

*This kit is for Issue #4 only. Future issues should follow the same pattern: promo kit in `issue_NN/PROMO_KIT.md` with platform-specific copy, timing sequence, and metrics tracking.*
