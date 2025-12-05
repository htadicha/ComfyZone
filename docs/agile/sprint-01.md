# Sprint 01 – Remediation & Evidence

- **Duration:** 2025-12-02 → 2025-12-15
- **Objective:** Close the assessor’s LO1–LO6 gaps by restoring registration, tightening SEO, and documenting the agile/test process.
- **Velocity Target:** 28 points

## Board Snapshot

| Column | Stories |
| --- | --- |
| Backlog | CZ-13 (Wishlist CRUD), CZ-14 (Review moderation queue) |
| Sprint Backlog | CZ-08, CZ-11, CZ-12 |
| In Progress | CZ-08 (SEO remediation), CZ-11 (Auth hardening) |
| In Review | CZ-12 (Agile evidence pack) |
| Done | CZ-01..CZ-07 |

## Committed Stories

| ID | Story | Acceptance Criteria | Points | Status |
| --- | --- | --- | --- | --- |
| CZ-08 | *As a* prospective customer *I want* search engines to understand the site *so that* I can discover products organically | `robots.txt` served at `/robots.txt`; `/sitemap.xml` includes home/shop/about/services/contact/terms/privacy/product URLs; `<meta description>` + canonical tags on every public page; 404 page wired when `DEBUG=False`; all placeholder links replaced | 8 | In Progress |
| CZ-11 | *As a* first-time shopper *I want* registration to just work *so that* I can check out | Registration saves inactive user until verification; resend endpoint exists; admin action to verify/resend; failing SMTP surfaces friendly messaging; PEP8-compliant tests covering the flows | 8 | In Progress |
| CZ-12 | *As an* assessor *I want* evidence of agile+testing *so that* the project meets LO2/LO1.19 | `docs/agile` playbook, sprint log, wireframes, validation summary; README + DEPLOYMENT reference the new artefacts; manual test matrix updated | 5 | In Review |
| CZ-15 | *As a* marketer *I want* newsletter signups to be auditable *so that* I can demonstrate LO5 | GDPR-friendly consent copy, success/failure toasts, admin export, README marketing section updated | 7 | Todo |

## Risks & Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| SMTP provider blocks console emails | Blocks registration acceptance criteria | Added resend flow + admin override; document requirement for production SMTP credentials |
| SEO validator backlog | Could consume entire sprint | Focus on highest-traffic templates first; document outstanding sections for next sprint |
| Evidence drift | Assessors can’t verify improvements | Store artefacts under version control (`docs/agile`, `docs/evidence`) and reference them in README/DEPLOYMENT |

## Retro Notes

- Keep sprint scope tight; tackling all template lint issues would derail schedule.
- Store screenshots of the GitHub Project board at sprint boundaries in `docs/verification-log.md`.
- Automate link checking via GitHub Action in a future iteration.






