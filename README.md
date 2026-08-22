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
| 02 | Schedule | **The** week. One grid, six layers, every block owned by another tab and labelled with which one. Conflict detection across all layers. Week / today / printable list views. |
| 03 | Courses & Study | Catalog facts, student-reported hard spots, the four real ways to research an instructor, and the study-plan controls that write into the shared schedule. |
| 04 | Dining | Meal-plan value engine, Dining Dollars burn-down, campus hub diagram, walking times with passing-period slack, and a hall-aware meal builder with diet/allergy filters and a permanent block list. |
| 05 | Life & Balance | The social floor that caps study, commitments as hard blocks, a trips-home planner that prices each weekend, and home games with clash detection. |
| 06 | Work | Job comparison scored on pay, flexibility, benefits, student experience and schedule fit against the real week. A job marked as held becomes shifts on the schedule. |
| 07 | Deals | 36 student deals with a source link on every card and a savings tracker split by how well each figure is evidenced. |
| 08 | Academics | Grades and GPA on IU's scale, deadlines, a transparent strain index, daily check-ins, and the support your fees already cover. |
| 09 | Data | A one-click Canvas bookmarklet, link testing, paste import, storage tools, the reset flow, and the works-cited list. |

## One schedule, not nine

Every tab writes into a single block model built in `derive()`:

```
d.fixedBlocks[dow] = [{a, b, kind, label, sub, color, tab}]
```

`kind` is one of class / commit / work / game, joined at render time by study
blocks from `d.plan` and meal windows from `d.plan.meals`. `dayBlocks(dow)`
returns the merged, layer-filtered list, and it is the *only* function that
composes a day — the Schedule tab, the General tab's Today panel and the
conflict checker all call it. `buildStudyPlan()` excludes `d.fixedBlocks`
wholesale, so marking a job as held or saying you are going to a game moves the
study plan automatically. Nothing keeps a second copy of the week.

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

## Resetting

`resetFlow()` is three screens plus a typed word: choose *hand it to someone
else* (blank) or *start my semester over* (reloads the shipped Fall 2026 data),
see exactly what is about to go with live counts, get pushed to export a copy,
then type `RESET`. Nothing fires on a stray click.

## Files

- `index.html` — the standalone app, boots with the owner's Fall 2026 data.
- `crimson-command-share.html` — the same app with `BOOT_PROFILE = 'blank'`, so
  it opens empty. This is the copy to send someone. Generated.
- `artifact.html` — body only, for publishing as an Artifact. Generated.
- `build-artifact.py` — regenerates both derived files from `index.html`.

```
python3 build-artifact.py
```

Only `index.html` is edited by hand. The other two are always rebuilt.
