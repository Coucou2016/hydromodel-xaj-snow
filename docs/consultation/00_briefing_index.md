# XAJ-Snow consultation briefing index (for ChatGPT web review)

**Public repository:** https://github.com/Coucou2016/hydromodel-xaj-snow  
**Branch:** `master`  
**Purpose:** Read-only briefing so an external reviewer (ChatGPT with web search) can advise on HESS-oriented manuscript revision **without** file attachments.

## How to read (required order)

1. [`01_project_status_and_evidence.md`](01_project_status_and_evidence.md) — verified facts only (metrics + relative source paths)
2. [`02_paper_vs_report_boundary.md`](02_paper_vs_report_boundary.md) — hard boundary rules (paper vs research report)
3. [`03_manuscript_excerpt_for_review.md`](03_manuscript_excerpt_for_review.md) — Abstract / Intro / Methods / Results excerpt (sanitized)
4. [`04_requested_review_tasks.md`](04_requested_review_tasks.md) — **deliverable checklist** (what to return)

## Raw GitHub URLs (prefer these)

Replace `COMMIT_OR_BRANCH` with `master` or a specific commit SHA after push:

- Index: `https://raw.githubusercontent.com/Coucou2016/hydromodel-xaj-snow/master/docs/consultation/00_briefing_index.md`
- Evidence: `https://raw.githubusercontent.com/Coucou2016/hydromodel-xaj-snow/master/docs/consultation/01_project_status_and_evidence.md`
- Boundary: `https://raw.githubusercontent.com/Coucou2016/hydromodel-xaj-snow/master/docs/consultation/02_paper_vs_report_boundary.md`
- Excerpt: `https://raw.githubusercontent.com/Coucou2016/hydromodel-xaj-snow/master/docs/consultation/03_manuscript_excerpt_for_review.md`
- Tasks: `https://raw.githubusercontent.com/Coucou2016/hydromodel-xaj-snow/master/docs/consultation/04_requested_review_tasks.md`

Blob (rendered) alternatives use `/blob/master/docs/consultation/...` on the same repo.

## Companion manuscript (full draft in repo)

- `results/publications/xaj_snow_manuscript.md` (Markdown sibling)
- `results/publications/xaj_snow_manuscript.html` (self-contained HTML; inline CSS + base64 figures; no CDN)
- Research report (engineering detail allowed): `results/publications/report.md`

## Ground rules for the reviewer

- Enable **web search**.
- Do **not** invent metrics; only use numbers listed in file 01 or ask the local team to verify.
- Do **not** recommend claiming “first XAJ+snow”, “global applicability”, or completed `rep=5000` / full 80-basin calibration unless file 01 marks them complete.
- Prefer HESS-style diagnosis / large-sample hydrology rhetoric (Santos, Wu, Premier, Husic, Yeste templates) over product-marketing tone.

## Local executor note

A Cursor agent will independently verify any DOI or numerical claim before adopting text into the manuscript generator (`scripts/generate_publication_outputs.py`).
