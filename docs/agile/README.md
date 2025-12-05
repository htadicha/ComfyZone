# Agile Operating Guide

This repository now mirrors the process used during development so an assessor can see *exactly* how work is planned, prioritised, and evidenced.

## Tooling

- **GitHub Project**: <https://github.com/users/husseintadicha/projects/5> (Kanban)
- **Issue templates**: Bug Report, Feature Request, User Story, Spike, Sprint Planning
- **Labels**:
  - Priority – `P0`, `P1`, `P2`, `P3`
  - Type – `bug`, `feature`, `tech-debt`, `doc`, `ux`
  - Status – `todo`, `in-progress`, `qa`, `blocked`
- **Milestones**: Each sprint is a 2-week milestone (`Sprint 01`, `Sprint 02`, etc.).

## Workflow

1. **Capture** – Every story begins life as a GitHub issue with a persona-based user story, acceptance criteria, and estimation (story points).
2. **Sprint Planning** – Issues are pulled into the `Sprint Backlog` column along with a link to the sprint document (see `sprint-01.md`).
3. **Execution** – Developers move cards across `In Progress → In Review → Done`. Pull requests must reference the issue ID (`Closes CZ-04`).
4. **Demo & Retro** – At sprint end we capture demo notes, retro action items, and point to any follow-up tickets created.
5. **Evidence** – Screenshots of the board at sprint boundaries plus QA logs are stored under `docs/verification-log.md`.

## Artefacts

- [`sprint-01.md`](sprint-01.md): detailed backlog for the remediation sprint requested in the assessor feedback.
- [`../wireframes/`](../wireframes/): design decisions (lo-fi wireframes) referenced by user stories CZ-01, CZ-04, and CZ-08.
- [`../evidence/validation-summary.md`](../evidence/validation-summary.md): QA results mapped back to acceptance criteria.

> **Tip:** When you open a new sprint, duplicate `sprint-01.md`, rename it, and update the stories + burndown metrics so the audit trail stays consistent.






