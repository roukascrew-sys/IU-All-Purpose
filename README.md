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
| 09 | Data | A one-click Canvas bookmarklet, a Stellic schedule importer, a screenshot scanner, link testing, paste import, storage tools, the reset flow, and the works-cited list. |

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

## Stellic import and the screenshot scanner

Stellic replaced the Student Center for registration, but unlike Canvas it has
no student-session-authenticated API — its documented API issues Personal
Access Tokens to the institution for server-to-server use, not to a student's
browser. So the Stellic bookmarklet does not call an endpoint; it copies the
visible page text the same way you would select and copy it yourself, and
that text is fed into a shared miner (`mineScheduleText()`) that regexes out
course codes, meeting types, day letters and time ranges.

The screenshot scanner reuses the same miner as a fallback. It loads
Tesseract.js from a CDN on first use (works in the downloaded file with
internet access; blocked by the hosted Artifact preview's CSP), OCRs the
image, and tries to calibrate a grid from a detected day-header row and hour
axis so it can place each course under the right day and time. When it can't
find both, it falls back to running the raw OCR text through the same text
miner the Stellic box uses. Either way, results land in one shared
preview-and-confirm table (`renderMeetingCandidates()` /
`commitMeetingCandidates()`) — nothing is saved until you approve each row,
and every field stays editable. Grid-calibrated end times run short for
blocks with little text in them, since the calibration reads where the text
sits, not the true height of the calendar block; the scanner's own UI says so.

## The Fall 2026 Schedule of Classes

`tools/ingest_soc.py` turns the IU Office of the Registrar's own Schedule of
Classes export (`soc4268`, Fall 2026 Bloomington) into a normalized
course/section/meeting/instructor dataset. That export is the registrar's
authoritative section-level record for the term, so it needs no
authentication and can be reprocessed at any time from the preserved raw
file in `data/`.

```
python3 tools/ingest_soc.py     # parse -> normalize -> validate -> report
python3 tools/embed_soc.py      # embed the result into index.html
python3 build-artifact.py       # regenerate the derived builds
```

The pipeline is `RawSource -> Parser -> Normalizer -> Validator ->
Repository/Reporter`, and the source is swappable: anything that yields the
same raw section records can feed the rest of the chain untouched.

Current run: **4,875 courses, 11,886 sections, 11,887 meetings, 3,668
instructors, 100 subjects, 76 buildings — 0 validation errors.** Full
per-run statistics land in `data/reports/<run-id>.json`; exports are
`courses.json`, `sections.json`, `meetings.json`, `instructors.json`,
`schedule-data.json` (the compact projection the app embeds) plus
`courses.csv` and `sections.csv`.

Every field is tagged `EXACT` (printed in the export), `DERIVED` (computed
by a documented rule) or `UNKNOWN` (absent — stored null, never guessed).
The export carries no descriptions, prerequisites, corequisites or GenEd
attributes, so those stay null. One value is `DERIVED` and flagged as such:
64 sections print the day code `D`, conventionally "daily", which expands to
Monday–Friday while `days_raw` keeps the literal `D`.

A course is not a section. IU issues a separate class number to each
component, so a lecture and its discussion are two independently
registerable sections; the catalog panel lists both and each carries its own
meetings. Conflict detection runs over every meeting of every added section
through the existing `d.fixedBlocks` / `dayBlocks()` model, so a Friday lab
clashing with a Friday lecture is caught the same way any other overlap is.

## Hand-cited catalog and the building directory

`CATALOG` holds real, individually-sourced IU Bloomington courses — the five
on the owner's own schedule plus nine more spanning CSCI, INFO, MATH, ENG,
Kelley and PSY, each cited to its own catalog page. It is not the whole
university: IU runs thousands of sections across roughly 200 subjects each
term, and this environment cannot bulk-fetch IU's own bulletin any more than
it can query Google's Distance Matrix for walking times. The "Browse the
course catalog" panel on the Courses tab searches what's built in and hands
anything else to a scoped Google search over academics.iu.edu and Coursicle.
The same shape applies to buildings: `PLACES` holds the dozen locations the
owner's own week actually uses, each with a hand-checked address, plus a
free-text box that sends any other IU building straight to Google Maps by
name rather than asserting a location nobody checked.

Every code that flows through an importer — Stellic paste, screenshot OCR,
or the "add a course" dialog — is run through `canonicalizeCode()`, which
snaps it to the exact string an existing course or catalog entry already
uses. Without that, a mined "CSCI-C212" would silently miss `CATALOG['CSCI-C
212']` on an exact-string lookup even though the course is right there. The
same mining pass also runs `mineBuilding()` over the source text, matching a
short list of building keywords so a class's location comes along
automatically when it's mentioned. When a canonicalized code lands a brand
new course, its credit hours are pulled from the catalog entry if verified,
rather than left blank for the owner to re-enter something this page already
knows.

Canvas import used to silently drop weights and due dates for any course
code that didn't match one already on the Courses tab. It now offers to
create the missing course instead — enriched from the catalog when the code
matches, titled from Canvas's own course name otherwise — so nothing Canvas
reports gets lost to a courses-tab gap.

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

## The Trine build

`trine.html` is the same planner rebuilt for **Trine University** in Angola,
Indiana. The engine is byte-identical; what changes is the campus data layer,
the branding and the import route:

| | IU build | Trine build |
|---|---|---|
| Palette | warm limestone + crimson | navy + Vegas gold |
| Storage key | `iu.crimsonCommand.v1` | `trine.thunderCommand.v1` |
| Boots with | the owner's five courses | nothing — you add your own |
| Course list | all 4,875 Fall 2026 courses, from the registrar export | none — Trine publishes no equivalent export |
| Course numbers | three digits (`CSCI-C 212`) | five digits (`CS 24000`) |
| LMS import | Canvas JSON API | Moodle web service + grade report |
| Dining | five AYCTE halls, swipes + Dining Dollars | Whitney Commons, The Depot and two coffee shops; a 10 or 19-meal Bon Appétit plan |
| Athletics | Big Ten, pre-loaded football schedule | MIAA Division III, nothing pre-loaded |

The two keys differ deliberately, so both builds can run in one browser without
overwriting each other.

`make-trine.py` generates it from `index.html` by swapping ~150 named sections.
`index.html` is opened read-only and the script asserts it is unchanged, so the
IU build cannot drift as a side effect:

```
python3 make-trine.py
```

Because it is a transform rather than a fork, an engine fix in `index.html`
reaches the Trine build on the next run. Only the data and copy are duplicated.

## Files

- `index.html` — the standalone app, boots with the owner's Fall 2026 data.
- `trine.html` — the Trine University build. Generated.
- `make-trine.py` — regenerates `trine.html` from `index.html`.
- `byu.html` — the BYU Provo build. Generated.
- `make-byu.py` — regenerates `byu.html` from `index.html`.
- `byu-artifact.html` — body only, for publishing the BYU build. Generated.
- `crimson-command-share.html` — the same app with `BOOT_PROFILE = 'blank'`, so
  it opens empty. This is the copy to send someone. Generated.
- `artifact.html` — body only, for publishing as an Artifact. Generated.
- `build-artifact.py` — regenerates both derived files from `index.html`.

```
python3 build-artifact.py
```

Only `index.html` is edited by hand. Everything else is always rebuilt.

## Keeping the two builds honest

`make-trine.py` regenerates `trine.html` from `index.html` on every run, so
an engine fix in the IU build carries over. The risk that creates is the
opposite one: IU's *content* carrying over too. Reading the built Trine file
end to end surfaced a set of leaks that grepping for "IU" would not have
caught, because they name IU things without naming IU:

- the credits-unset signal told a Trine student about "INFO-T 100"
- the dining-strategy note listed IU's five dining halls
- the social note quoted IU's SRSC fee of $84.68 a semester
- the low-energy recommendation gave IU's CAPS address and phone number
- `mineBuilding()` matched IU building names, so no Trine location could
  ever be detected
- the boot toast announced "your four Fall 2026 courses" in a build that
  ships empty
- the building dropdown filtered on IU's `mcnutt` place id

Several of those fire for a real user, not just in principle. They are all
fixed, and the build now ends with a leak scan asserting that none of
`IU Bloomington`, `One.IU`, `Stellic`, `mcnutt`, `SRSC`, IU course codes or
the embedded registrar dataset appear in the output. The only surviving
`Stellic` strings are internal function and element names, never rendered.

## The Moodle importer

Trine runs Moodle, and the first version of this importer scraped
`/my/courses.php` for `course/view.php?id=` links. That works on Moodle 3.x
and returns **nothing** on Moodle 4.x, which renders the course-overview
block in the browser — the server HTML has no course links in it at all, so
the importer always reported "no courses found". Both layouts are covered by
fixtures in the test suite; the old code was confirmed failing against the
4.x one before the fix and passing against 3.x, which is why the bug looked
intermittent rather than total.

It now calls `core_course_get_enrolled_courses_by_timeline_classification`
through `/lib/ajax/service.php` — the same web service Moodle's own dashboard
calls, same-origin, authenticated by the session cookie plus the page's
`sesskey` (read from `M.cfg`, a `sesskey=` link, or a hidden input). That is
Moodle's real equivalent of the Canvas REST API. Three fallbacks sit behind
it: a scrape of `/my/courses.php`, `/my/` and `/course/index.php`; then any
course links on the page you are standing on. The completion alert names
which route produced the data, and how many courses came back with no
readable grade table, so a partial read is visible rather than silent.

Grades still come from the rendered grade report, because Moodle exposes no
student-facing grade JSON without an institution-issued token. Each graded
item becomes its own weighted grade component, preserving Moodle's weight
column; the course total row is dropped rather than counted twice. A course
with nothing posted yet still imports as a course — the enrolment is the
fact, the assignments are just not there yet, the same standard the IU build
applies to Canvas.

Trine also numbers courses with five digits (`CS 24000`) where IU uses three
(`CSCI-C 212`). The shared schedule miner and the LMS code matcher both
capped at four, so every mined Trine code silently failed to match; both
regexes are widened in the Trine build.

## The BYU build

`byu.html` is the same planner rebuilt for **Brigham Young University** in
Provo, Utah. Same engine, same transform pattern as Trine:

| | IU build | Trine build | BYU build |
|---|---|---|---|
| Palette | warm limestone + crimson | navy + Vegas gold | BYU navy + near-white |
| Storage key | `iu.crimsonCommand.v1` | `trine.thunderCommand.v1` | `byu.cougarCommand.v1` |
| Boots with | the owner's five courses | nothing | nothing |
| Course list | all 4,875 Fall 2026 courses, from the registrar export | none | 16 cited courses + live catalog search |
| Course codes | `CSCI-C 212` | `CS 24000` | `C S 142`, `REL A 275`, `A HTG 100` |
| LMS import | Canvas JSON API | Moodle web service | Canvas JSON API |
| Schedule import | Stellic | myPortal | MyBYU |
| Dining | five AYCTE halls | Whitney Commons + two coffee shops | Cannon Commons, Cougareat, Creamery on Ninth |
| Meal plans | swipes + Dining Dollars | 10 or 19 meals a week | Open Door, Dining Plus, True Blue, EZ Dining |
| Athletics | Big Ten, pre-loaded | MIAA D-III, nothing pre-loaded | Big 12, seven 2026 home games pre-loaded |

```
python3 make-byu.py
```

BYU runs Canvas, so the IU bookmarklet and its whole parse path carry over
unchanged — only the host list and the wording differ. What did *not* carry
over is the parsing, and testing against real BYU rows found five defects
that would each have broken the importer for every BYU student:

1. **Subject codes contain spaces.** `C S 142`, `REL A 275`, `A HTG 100`.
   The IU regex demanded a 2–5 letter first token, so it dropped `C S`
   entirely and read `A HTG 100` as `HTG 100`. The BYU regex takes an
   optional second token and requires a separator before the number — the
   separator matters, because without it a room like `JFSB B037` parses as
   a course.
2. **BYU writes times as `10:00a – 10:50a`** — a bare a/p with no "m",
   which the IU meridiem pattern rejected outright.
3. **The time scanner took the first regex hit only.** On a BYU row that is
   the section number: `C S 142 - 002` reads as 42–00, which carries no
   meridiem, so the function bailed and *every* meeting lost its time. It
   now scans for the first candidate that actually resolves.
4. **The 3-line read-ahead window.** Registration screens wrap a meeting
   across short lines, so the miner reads a window. BYU puts a whole
   section on one line, and reading ahead dragged the next course's days
   and room into the current row. The line alone now wins whenever it
   already carries both a day set and a time.
5. **`matchCourse()` carried its own IU-shaped regex**, so a Canvas course
   named `REL C 225: Foundations of the Restoration` came back as
   `REL-C 225` and stopped matching the catalog.

Rooms are matched on both the long building name and the abbreviation, since
BYU writes them as `TMCB 1170` rather than "Talmage".

One fix landed in `index.html` instead, because it was never BYU-specific: a
lecture and its lab arrive as two rows with the same course code, and both
render as "+ new course" because neither existed when the table was drawn.
`commitMeetingCandidates()` created a duplicate course for the second row.
All three builds get the fix.

### Reading the built file, again

The same end-to-end read that caught the Trine leaks caught these, none of
which contain the word "IU":

- the dining tab asserted, as **verified**, that Dining Dollars "carry from
  fall to spring but expire at the end of the academic year, and can be
  topped up in $5 increments with a $25 minimum" — that is IU's CrimsonCard
  rule, and BYU publishes no rollover rule I could reach
- the support panel opened "You have paid the health fee and the activity
  fee", while the CAPS card three lines down correctly said no fee was
  stated anywhere I could reach
- the professor-research panel described "a school of two thousand", which
  is Trine's enrolment, not BYU's
- the catalog panel said "no course list ships with this build" directly
  above sixteen shipped courses
- the bookmarklet told you to open `iu.instructure.com`
- a `\u2014` escape that landed in static HTML, where nothing interprets it,
  and rendered literally on the page

### What is verified, and what is not

Sixteen courses ship with credit hours, descriptions, prerequisites and
topic lists quoted from `catalog.byu.edu` or from published MAP sheets, each
with its own citation. BYU publishes no downloadable schedule of classes
that this environment could reach, so there is no term-by-term section data
embedded — the catalog panel says so, and the live search hands your query
to `catalog.byu.edu` rather than guessing.

Meal-plan *structures* come from BYU Dining; the *prices* come from
secondary write-ups and are labelled reported, not verified. The $9–$20
student starting wage is BYU's own published figure; the $14.21 median and
$13.46–$15.14 band are an aggregator's. All seven 2026 home football games
come from the published Big 12 schedule, including the Iowa State game moved
to Friday 9 October — the only weeknight game, and the one most likely to
eat an evening. Buildings without a street address I could verify are drawn
with a dashed outline and fall back to a Google Maps name search.

