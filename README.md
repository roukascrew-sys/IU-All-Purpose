# Crimson Command

An all-purpose semester planner for one IU Bloomington student: Fall 2026,
five courses, McNutt Quad, the IU 7-Day Expanded meal plan.

Open `index.html` in a browser. No build step, no server, no dependencies.
Everything is stored in that browser's local storage under one key and never
leaves the machine.

## The six tabs

| # | Tab | What it does |
|---|-----|--------------|
| 01 | General | Every figure on the site in one view: the 168-hour weekly allocation, study load by course, day-by-day load against a ceiling, a semester timeline, and cross-tab signals. |
| 02 | Courses & Study Plan | Catalog facts per course, student-reported hard spots, the four real ways to research an instructor, and a weekly study plan built around actual class, sleep and meal windows. |
| 03 | Dining & Map | Meal-plan structure, a Dining Dollars burn-down against an even-pace line, a cost-per-swipe value engine, a hub diagram of campus destinations, walking times between consecutive classes with passing-period slack, and macronutrient targets. |
| 04 | Life & Balance | The social floor that caps study, gym/intramural/club commitments as hard blocks, a trips-home planner that costs each weekend, and home games with clash detection. |
| 05 | Work | Part-time job comparison scored on pay, flexibility, benefits, student experience and schedule fit against your real week. |
| 06 | Deals & Savings | 36 student deals with a source link on every card and a running savings tracker split by how well the dollar figure is evidenced. |
| 07 | Academic Tracker | Grades and GPA on IU's scale, assignment deadlines, a transparent strain index, daily check-ins, and the support services your fees already cover. |
| 08 | Data & Sources | A one-click Canvas bookmarklet, link testing, `.ics` and line-delimited paste import, and the full works-cited list. |

The tabs share one derived model, so a change on any tab recomputes the rest.

## The provenance rule

Every rendered fact carries one of four tags, and nothing appears without one:

- **Verified** — quoted from a named source, with the URL on the card.
- **Reported** — secondary or student-sourced; treat as an estimate.
- **Your input** — you typed it.
- **Computed** — arithmetic whose inputs are all visible on screen.

Where a figure could not be verified, the field is left empty rather than
filled with a guess. The known gaps are listed at the bottom of tab 06.

## The social floor

Most planners treat free time as whatever is left after study. This one inverts
that: `S.social.floorWeek` is protected first, study is capped at
`discretionary − socialNeeded`, and if the cap bites, every course is scaled by
the same factor and the shortfall is stated on screen. Commitments earn social
credit by kind — intramurals and clubs count fully, the gym 30%, a work shift
10%.

## Canvas import

`canvasBookmarkletSource()` builds a bookmarklet that runs on a Canvas page, so
it is same-origin and the session cookie authenticates it — which is why it
works where a `fetch` from this page cannot. It reads
`/api/v1/courses` and `/api/v1/courses/:id/assignment_groups?include[]=assignments&include[]=submission`,
so one click returns assignment-group weights, every assignment with its due
date and points, and your score on each. Read-only, three GETs, clipboard out.
The parser folds weights into the grade table and due dates into the deadline
table together.

## State migrations

Saved state replaces whole arrays on load, so a browser that opened an earlier
version would keep its old timetable forever. `migrate()` applies later
corrections once, on load, and only where the user has not already overridden
them. Bump `v` in `defaults()` and add a branch when the shipped data changes.

## Files

- `index.html` — the standalone app.
- `artifact.html` — the same page with the document wrappers stripped, for
  publishing. Generated, never edited by hand.
- `build-artifact.py` — regenerates `artifact.html` from `index.html`.

```
python3 build-artifact.py
```
