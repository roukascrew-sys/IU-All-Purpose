# Crimson Command

An all-purpose semester planner for one IU Bloomington student: Fall 2026,
four courses, McNutt Quad, an unlimited meal plan.

Open `index.html` in a browser. No build step, no server, no dependencies.
Everything is stored in that browser's local storage under one key and never
leaves the machine.

## The six tabs

| # | Tab | What it does |
|---|-----|--------------|
| 01 | General | Every figure on the site in one view: the 168-hour weekly allocation, study load by course, day-by-day load against a ceiling, a semester timeline, and cross-tab signals. |
| 02 | Courses & Study Plan | Catalog facts per course, student-reported hard spots, the four real ways to research an instructor, and a weekly study plan built around actual class, sleep and meal windows. |
| 03 | Dining & Map | Meal-plan structure, a Dining Dollars burn-down against an even-pace line, a cost-per-swipe value engine, a hub diagram of campus destinations, and macronutrient targets. |
| 04 | Deals & Savings | 36 student deals with a source link on every card and a running savings tracker split by how well the dollar figure is evidenced. |
| 05 | Academic Tracker | Grades and GPA on IU's scale, assignment deadlines, a transparent strain index, daily check-ins, and the support services your fees already cover. |
| 06 | Data & Sources | Save and test links, paste `.ics` or line-delimited data in, and the full works-cited list. |

The tabs share one derived model, so a change on any tab recomputes the rest.

## The provenance rule

Every rendered fact carries one of four tags, and nothing appears without one:

- **Verified** — quoted from a named source, with the URL on the card.
- **Reported** — secondary or student-sourced; treat as an estimate.
- **Your input** — you typed it.
- **Computed** — arithmetic whose inputs are all visible on screen.

Where a figure could not be verified, the field is left empty rather than
filled with a guess. The known gaps are listed at the bottom of tab 06.

## Files

- `index.html` — the standalone app.
- `artifact.html` — the same page with the document wrappers stripped, for
  publishing. Generated, never edited by hand.
- `build-artifact.py` — regenerates `artifact.html` from `index.html`.

```
python3 build-artifact.py
```
