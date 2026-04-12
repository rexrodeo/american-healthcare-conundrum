# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, please report it responsibly. **Do not open a public GitHub issue.**

Email: **vonrexroad@gmail.com**

Include:
- A description of the vulnerability
- Steps to reproduce it
- Any relevant files, commits, or branches involved

I'll acknowledge receipt within 48 hours and work with you on a fix before any public disclosure.

## Scope

This project is an open-source data journalism effort. The primary security concerns are:

- **Accidental credential exposure** in commits or pipeline scripts
- **Malicious code injection** via pull requests (e.g., modified Python scripts that exfiltrate data or phone home)
- **Supply chain risks** in Python dependencies used by analysis pipelines

## What This Repo Does NOT Contain

- No authentication systems, user accounts, or session management
- No web application or API endpoints
- No personally identifiable information (PII) or protected health information (PHI)

All data used in this project comes from publicly available federal datasets (CMS, OECD, SEC EDGAR).

## Dependencies

Analysis scripts use standard Python data science libraries (`pandas`, `matplotlib`, `requests`, `duckdb`). If you notice a dependency with a known CVE, please report it using the process above.
