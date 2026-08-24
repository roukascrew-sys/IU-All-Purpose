#!/usr/bin/env python3
"""
IU Bloomington Schedule of Classes -> normalized scheduler dataset.

SOURCE
------
The official "Schedule of Classes Bulletin" tab-delimited export from the IU
Office of the Registrar (soc4268 = Fall 2026, Bloomington). This is the
registrar's own report, so it is the authoritative section-level record for
the term -- strictly better than anything a Stellic session would expose,
and it needs no authentication to reprocess.

PIPELINE
--------
    RawSource  ->  Parser  ->  Normalizer  ->  Validator  ->  Repository
                                                          ->  Reporter

The source is swappable: anything that can yield the same raw section
records (a Stellic API collector, a different term's export) can feed the
same Normalizer/Validator/Repository chain without touching them.

PROVENANCE RULES
----------------
Every field is one of:
    EXACT    - printed verbatim in the registrar export
    DERIVED  - computed from EXACT values by a documented rule
    UNKNOWN  - the export does not carry it; stored as null, never guessed

Nothing is invented. A field the registrar does not print stays null.
"""

import json
import os
import re
import sys
import csv
import hashlib
import datetime
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')

TERM = 'Fall 2026'
CAMPUS = 'IU Bloomington'
INSTITUTION = 'Indiana University'
SOURCE_SYSTEM = 'IU_REGISTRAR_SOC'

# ---------------------------------------------------------------- line shapes
# A course header: "SUBJ-X 123  TITLE (3 CR)" / "(1-3 CR)" / "(3 CR)"
COURSE_RE = re.compile(
    r'^(?P<code>[A-Z]{2,5}-[A-Z]{1,2}\s*\d{1,3}[A-Z]?)\s\s+'
    r'(?P<title>.+?)\s*\((?P<cr>[\d.]+(?:\s*-\s*[\d.]+)?)\s*CR\)\s*$'
)
# A component label: "Discussion (DIS)", "Laboratory (LAB)"
COMPONENT_RE = re.compile(r'^(?P<name>[A-Za-z /]+?)\s*\((?P<abbr>[A-Z]{2,4})\)\s*$')
# Variable-topic line: "VT: AGENTIC PROGRAMMING"
VT_RE = re.compile(r'^VT:\s*(?P<topic>.+?)\s*$')
# Page-break artifact the registrar report emits mid-table
ERROR_RE = re.compile(r'\*\*\s*ERROR\s*-\s*.*?\*\*')
# "09:35A-10:50A"
TIME_RE = re.compile(r'^(\d{1,2}):(\d{2})([AP])-(\d{1,2}):(\d{2})([AP])$')

# Registrar day letters. R=Thursday, S=Saturday, N=Sunday -- confirmed by the
# export's own 'SN' (weekend) and 'FSN' tokens.
DAY_MAP = {'M': 'MO', 'T': 'TU', 'W': 'WE', 'R': 'TH', 'F': 'FR', 'S': 'SA', 'N': 'SU'}
DAY_ORDER = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']

# 'D' appears on 64 rows across mixed subjects (Slavic and Central Eurasian
# language courses, but also BUS/MUS/CHEM/MATH). The registrar's conventional
# reading is "Daily", i.e. Monday-Friday, and every 'D' row carries a single
# ordinary class hour consistent with that. It is NOT printed as five day
# letters though, so the expansion is DERIVED, never EXACT: days_raw keeps the
# literal 'D' and these sections are counted separately in the report so they
# can be checked against One.IU before anyone schedules around them.
DAY_DERIVED = {'D': ['MO', 'TU', 'WE', 'TH', 'FR']}

# Component abbreviation -> the scheduler's internal meeting types.
COMPONENT_TYPE = {
    'LEC': 'LEC', 'DIS': 'DIS', 'DISC': 'DIS', 'LAB': 'LAB', 'DRL': 'DRL',
    'REC': 'REC', 'SEM': 'SEM', 'IND': 'IND', 'PRA': 'PRA', 'RSC': 'RSC',
    'CLN': 'CLN', 'FLD': 'FLD', 'WKS': 'WKS', 'STU': 'STU', 'PRC': 'PRC',
}


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def to24(h, m, ap):
    h = int(h)
    if ap == 'A':
        if h == 12:
            h = 0
    else:
        if h != 12:
            h += 12
    return '%02d:%02d' % (h, int(m))


def parse_time_range(raw):
    """'09:35A-10:50A' -> ('09:35','10:50'). 'ARR'/'' -> (None, None)."""
    raw = (raw or '').strip()
    if not raw or raw.upper() == 'ARR':
        return None, None
    m = TIME_RE.match(raw)
    if not m:
        return None, None
    a, b, ap1, c, d, ap2 = m.groups()
    return to24(a, b, ap1), to24(c, d, ap2)


def parse_days(raw):
    """'MW' -> (['MO','WE'], 'EXACT', []).

    Returns (days, provenance, unknown_letters). 'ARR'/'' yields no days.
    A token in DAY_DERIVED expands but is reported as DERIVED, not EXACT.
    """
    raw = (raw or '').strip()
    if not raw or raw.upper() == 'ARR':
        return [], 'EXACT', []
    if raw.upper() in DAY_DERIVED:
        return list(DAY_DERIVED[raw.upper()]), 'DERIVED', []
    days, bad = [], []
    for ch in raw:
        if ch in DAY_MAP:
            d = DAY_MAP[ch]
            if d not in days:
                days.append(d)
        elif not ch.isspace():
            bad.append(ch)
    days.sort(key=lambda d: DAY_ORDER.index(d))
    return days, 'EXACT', bad


def parse_location(raw):
    """'BH 104' -> ('BH','104'). 'OL ONLINE' -> ('OL','ONLINE'). '' -> (None,None)."""
    raw = (raw or '').strip()
    if not raw:
        return None, None
    parts = raw.split(None, 1)
    if len(parts) == 1:
        return parts[0], None
    return parts[0], parts[1].strip()


def parse_credits(raw):
    """'3' -> (3.0,3.0). '1-3' -> (1.0,3.0)."""
    raw = (raw or '').replace(' ', '')
    if '-' in raw:
        lo, hi = raw.split('-', 1)
        try:
            return float(lo), float(hi)
        except ValueError:
            return None, None
    try:
        v = float(raw)
        return v, v
    except ValueError:
        return None, None


def num(raw):
    raw = (raw or '').strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


# ------------------------------------------------------------------- parser
def parse(path, report):
    """Walk the export once, emitting raw section records in document order."""
    with open(path, encoding='utf-8', errors='replace') as fh:
        lines = fh.read().splitlines()
    report['source_lines'] = len(lines)

    school = None          # "Hutton Honors College (HHC)"
    course = None          # current course header dict
    component = None       # current component label, e.g. LAB
    topic = None           # current VT: topic
    last = None            # last emitted section, for notes/extra instructors
    out = []

    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        cells = raw.split('\t')
        tabs = len(cells) - 1
        # cell contents with the leading placeholder spaces removed
        vals = [c.strip() for c in cells]
        text = ' '.join(v for v in vals if v).strip()
        text = ERROR_RE.sub('', text).strip()
        if not text:
            continue

        # -- school / department banner (no tabs, has a parenthesised code)
        if tabs == 0:
            if re.match(r'^.+\([A-Z]{2,6}\)$', text):
                school = text
            continue

        # -- section data row: 11 tabs and a numeric class number in cell 3
        if tabs == 11 and num(vals[3]) is not None:
            if course is None:
                report['warnings'].append('section row before any course header: ' + text[:60])
                continue
            status_raw = vals[2]
            rstr_raw = vals[4]
            start, end = parse_time_range(vals[5])
            days, days_prov, baddays = parse_days(vals[6])
            if baddays:
                report['warnings'].append(
                    'unrecognised day letter(s) %r in class %s' % (''.join(baddays), vals[3]))
            if days_prov == 'DERIVED':
                report['days_derived_sections'].append(vals[3])
            bldg, room = parse_location(vals[7])
            rec = {
                'class_number': vals[3],
                'status_raw': status_raw or None,
                'restricted_raw': rstr_raw or None,
                'time_raw': vals[5] or None,
                'days_raw': vals[6] or None,
                'location_raw': vals[7] or None,
                'instructor_raw': vals[8] or None,
                'max_raw': vals[9],
                'avail_raw': vals[10],
                'waitlist_raw': vals[11],
                # normalized
                'start_time': start,
                'end_time': end,
                'days': days,
                'days_provenance': days_prov,
                'building': bldg,
                'room': room,
                'component': component or 'LEC',
                'topic': topic,
                'course_code': course['code'],
                'school': school,
                'instructors': [],
                'notes': [],
            }
            if vals[8]:
                rec['instructors'].append(vals[8])
            out.append(rec)
            course['sections'].append(rec)
            last = rec
            continue

        # -- continuation instructor line (8 tabs, name in the last cell)
        if tabs == 8 and vals[-1]:
            if last is not None:
                last['instructors'].append(vals[-1])
            continue

        # -- component label / notes / topic / nested course header
        body = ' '.join(v for v in vals[1:] if v).strip()
        body = ERROR_RE.sub('', body).strip()
        if not body:
            continue

        cm = COURSE_RE.match(body)
        if cm:
            lo, hi = parse_credits(cm.group('cr'))
            code = re.sub(r'\s+', ' ', cm.group('code')).strip()
            course = {
                'code': code,
                'title': cm.group('title').strip(),
                'credits_raw': cm.group('cr'),
                'credits_min': lo,
                'credits_max': hi,
                'school': school,
                'sections': [],
            }
            component = None
            topic = None
            last = None
            yield_course(course, out)
            continue

        vt = VT_RE.match(body)
        if vt:
            topic = vt.group('topic').strip()
            continue

        comp = COMPONENT_RE.match(body)
        if comp and course is not None:
            abbr = comp.group('abbr')
            component = COMPONENT_TYPE.get(abbr, abbr)
            continue

        # anything else at note depth attaches to the last section
        if last is not None:
            last['notes'].append(body)
        elif course is not None:
            course.setdefault('notes', []).append(body)

    return out


_COURSES = []


def yield_course(course, _out):
    _COURSES.append(course)


# --------------------------------------------------------------- normalizer
def normalize(courses, run_id, report):
    """Group raw rows into courses -> sections -> meetings.

    One registrar row == one independently-registerable section component
    carrying exactly one meeting pattern. Rows are grouped into a section by
    class number; a class number appearing on several rows (a lecture that
    meets MW in one room and F in another) becomes ONE section with SEVERAL
    meetings, which is what conflict detection has to see.
    """
    norm_courses = {}
    sections = {}
    meetings = []
    instructors = {}
    sec_inst = []

    for c in courses:
        if not c['sections']:
            # A course printed with no section rows. Keep it: the catalog
            # identity is real even when nothing is scheduled yet -- same
            # standard the Canvas importer uses for a course with no
            # assignments posted.
            pass
        code = c['code']
        subject, number = split_code(code)
        if code not in norm_courses:
            norm_courses[code] = {
                'course_id': code,
                'code': code,
                'subject': subject,
                'number': number,
                'title': c['title'],
                'credits_min': c['credits_min'],
                'credits_max': c['credits_max'],
                'credits': c['credits_min'] if c['credits_min'] == c['credits_max'] else None,
                'credits_raw': c['credits_raw'],
                'school': c['school'],
                'level': course_level(number),
                'campus': CAMPUS,
                'term': TERM,
                # the registrar export carries none of these; never guessed
                'description': None,
                'prerequisites': None,
                'corequisites': None,
                'attributes': [],
                'notes': c.get('notes', []),
                'source_system': SOURCE_SYSTEM,
                'scrape_run_id': run_id,
                'provenance': {
                    'code': 'EXACT', 'title': 'EXACT', 'credits': 'EXACT',
                    'subject': 'DERIVED', 'number': 'DERIVED', 'level': 'DERIVED',
                    'description': 'UNKNOWN', 'prerequisites': 'UNKNOWN',
                    'corequisites': 'UNKNOWN',
                },
                'section_ids': [],
            }
        else:
            # same code printed under two schools/topics: keep the first
            report['duplicate_course_headers'] += 1

        for r in c['sections']:
            cn = r['class_number']
            sid = cn
            if sid not in sections:
                sections[sid] = {
                    'section_id': sid,
                    'class_number': cn,
                    'course_id': code,
                    'course_code': code,
                    'component': r['component'],
                    'topic': r['topic'],
                    'term': TERM,
                    'campus': CAMPUS,
                    'school': r['school'],
                    'status': 'CLOSED' if (r['status_raw'] or '').upper() == 'CLSD' else 'OPEN',
                    'status_raw': r['status_raw'],
                    'restricted': bool(r['restricted_raw']),
                    'restricted_raw': r['restricted_raw'],
                    'enrollment': {
                        'capacity': num(r['max_raw']),
                        'available': num(r['avail_raw']),
                        'waitlist': num(r['waitlist_raw']),
                        'enrolled': None,   # DERIVED below when both present
                    },
                    'delivery_mode': None,
                    'notes': [],
                    'instructor_ids': [],
                    'meeting_ids': [],
                    'source_system': SOURCE_SYSTEM,
                    'source_record_id': cn,
                    'scrape_run_id': run_id,
                    'provenance': {
                        'class_number': 'EXACT', 'status': 'EXACT',
                        'capacity': 'EXACT', 'available': 'EXACT',
                        'waitlist': 'EXACT', 'enrolled': 'DERIVED',
                        'component': 'EXACT', 'delivery_mode': 'DERIVED',
                    },
                }
                norm_courses[code]['section_ids'].append(sid)
            s = sections[sid]

            cap, avail = s['enrollment']['capacity'], s['enrollment']['available']
            if cap is not None and avail is not None:
                s['enrollment']['enrolled'] = max(cap - avail, 0)

            for n in r['notes']:
                if n not in s['notes']:
                    s['notes'].append(n)

            # delivery mode is only asserted when the export actually says so
            loc = (r['location_raw'] or '').upper()
            if loc.startswith('OL ') or 'ONLINE' in loc:
                s['delivery_mode'] = 'ONLINE'
            elif r['days'] or r['start_time']:
                s['delivery_mode'] = s['delivery_mode'] or 'IN_PERSON'

            for nm in r['instructors']:
                iid = inst_id(nm)
                if iid not in instructors:
                    last_, first_ = split_name(nm)
                    instructors[iid] = {
                        'instructor_id': iid,
                        'full_name': nm,
                        'last_name': last_,
                        'first_initial': first_,
                        'email': None,        # not in the export
                        'profile_url': None,  # not in the export
                        'source_system': SOURCE_SYSTEM,
                        'provenance': {'full_name': 'EXACT', 'last_name': 'DERIVED',
                                       'email': 'UNKNOWN', 'profile_url': 'UNKNOWN'},
                    }
                if iid not in s['instructor_ids']:
                    s['instructor_ids'].append(iid)
                    sec_inst.append({'section_id': sid, 'instructor_id': iid, 'role': 'INSTRUCTOR'})

            # every row contributes a meeting, even an arranged one
            mid = '%s-m%d' % (sid, len(s['meeting_ids']) + 1)
            meetings.append({
                'meeting_id': mid,
                'section_id': sid,
                'course_code': code,
                'meeting_type': r['component'],
                'days': r['days'],
                'days_raw': r['days_raw'],
                'days_provenance': r['days_provenance'],
                'start_time': r['start_time'],
                'end_time': r['end_time'],
                'time_raw': r['time_raw'],
                'building': r['building'],
                'room': r['room'],
                'location_raw': r['location_raw'],
                'arranged': not r['days'] and not r['start_time'],
                'start_date': None,   # not in the export
                'end_date': None,     # not in the export
                'timezone': None,     # not in the export
                'source_system': SOURCE_SYSTEM,
                'scrape_run_id': run_id,
                'provenance': {
                    'days': r['days_provenance'], 'start_time': 'EXACT', 'end_time': 'EXACT',
                    'building': 'EXACT', 'room': 'EXACT',
                    'start_date': 'UNKNOWN', 'end_date': 'UNKNOWN',
                    'timezone': 'UNKNOWN',
                },
            })
            s['meeting_ids'].append(mid)

    return norm_courses, sections, meetings, instructors, sec_inst


def split_code(code):
    m = re.match(r'^([A-Z]{2,5})-([A-Z]{1,2})\s*(\d{1,3}[A-Z]?)$', code)
    if m:
        return m.group(1), m.group(3)
    m = re.match(r'^([A-Z]{2,5})\s*(\d{1,3}[A-Z]?)$', code)
    if m:
        return m.group(1), m.group(2)
    return None, None


def course_level(number):
    if not number:
        return None
    d = re.match(r'^(\d+)', number)
    if not d:
        return None
    n = int(d.group(1))
    if n < 200:
        return 100
    return (n // 100) * 100


def split_name(nm):
    parts = nm.rsplit(' ', 1)
    if len(parts) == 2 and len(parts[1]) <= 2:
        return parts[0], parts[1]
    return nm, None


def inst_id(nm):
    return 'i' + hashlib.sha1(nm.encode('utf-8')).hexdigest()[:10]


# --------------------------------------------------------------- validator
def validate(courses, sections, meetings, instructors, sec_inst, report):
    errs = report['validation_errors']
    warns = report['warnings']

    for sid, s in sections.items():
        if s['course_id'] not in courses:
            errs.append('section %s references missing course %s' % (sid, s['course_id']))
        if not s['meeting_ids']:
            errs.append('section %s has no meetings' % sid)
        e = s['enrollment']
        if e['capacity'] is not None and e['available'] is not None:
            if e['available'] > e['capacity']:
                warns.append('section %s: available %s exceeds capacity %s'
                             % (sid, e['available'], e['capacity']))

    seen_m = set()
    for m in meetings:
        if m['section_id'] not in sections:
            errs.append('meeting %s references missing section %s' % (m['meeting_id'], m['section_id']))
        if m['meeting_id'] in seen_m:
            errs.append('duplicate meeting id %s' % m['meeting_id'])
        seen_m.add(m['meeting_id'])
        for d in m['days']:
            if d not in DAY_ORDER:
                errs.append('meeting %s has invalid day %s' % (m['meeting_id'], d))
        if m['start_time'] and m['end_time'] and m['end_time'] <= m['start_time']:
            errs.append('meeting %s ends at or before it starts (%s-%s)'
                        % (m['meeting_id'], m['start_time'], m['end_time']))
        if m['days'] and not m['start_time']:
            warns.append('meeting %s has days but no time' % m['meeting_id'])

    for r in sec_inst:
        if r['section_id'] not in sections:
            errs.append('instructor link references missing section %s' % r['section_id'])
        if r['instructor_id'] not in instructors:
            errs.append('instructor link references missing instructor %s' % r['instructor_id'])

    for code, c in courses.items():
        if c['credits_min'] is not None and c['credits_min'] < 0:
            errs.append('course %s has negative credits' % code)
        if c['term'] != TERM:
            errs.append('course %s is not %s' % (code, TERM))
        if c['campus'] != CAMPUS:
            errs.append('course %s is not %s' % (code, CAMPUS))


# ------------------------------------------------------------------ exports
def compact_for_app(courses, sections, meetings):
    """A size-optimised shape for the browser app.

    Arrays instead of objects, minutes-since-midnight instead of 'HH:MM',
    a day bitmask instead of string lists. The full-fidelity records stay in
    courses.json / sections.json; this is only the scheduling projection.
    """
    by_sec = collections.defaultdict(list)
    for m in meetings:
        by_sec[m['section_id']].append(m)

    def mins(t):
        if not t:
            return None
        h, mm = t.split(':')
        return int(h) * 60 + int(mm)

    def mask(days):
        b = 0
        for d in days:
            b |= 1 << DAY_ORDER.index(d)
        return b

    out_courses = []
    for code in sorted(courses):
        c = courses[code]
        secs = []
        for sid in c['section_ids']:
            s = sections[sid]
            ms = []
            for m in by_sec.get(sid, []):
                ms.append([
                    m['meeting_type'], mask(m['days']),
                    mins(m['start_time']), mins(m['end_time']),
                    m['building'] or '', m['room'] or '',
                ])
            secs.append([
                s['class_number'], s['component'],
                1 if s['status'] == 'OPEN' else 0,
                s['enrollment']['capacity'], s['enrollment']['available'],
                s['enrollment']['waitlist'],
                [i for i in s['instructor_ids']],
                ms, s['topic'] or '', 1 if s['restricted'] else 0,
                s['delivery_mode'] or '',
            ])
        out_courses.append([
            c['code'], c['title'], c['credits_min'], c['credits_max'],
            c['subject'] or '', c['level'], secs,
        ])
    return out_courses


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DATA, 'soc4268-fall2026-raw.tsv')
    run_id = 'soc4268-' + datetime.datetime.now().strftime('%Y%m%dT%H%M%S')

    report = {
        'scrape_run_id': run_id,
        'source_system': SOURCE_SYSTEM,
        'source_file': os.path.basename(src),
        'source_endpoint': 'IU Office of the Registrar, Schedule of Classes Bulletin export (soc4268)',
        'institution': INSTITUTION,
        'campus': CAMPUS,
        'term': TERM,
        'retrieved_at': now_iso(),
        'source_lines': 0,
        'duplicate_course_headers': 0,
        'validation_errors': [],
        'warnings': [],
        'days_derived_sections': [],
    }

    _COURSES.clear()
    rows = parse(src, report)
    courses, sections, meetings, instructors, sec_inst = normalize(_COURSES, run_id, report)
    validate(courses, sections, meetings, instructors, sec_inst, report)

    scheduled = [c for c in courses.values() if c['section_ids']]
    report.update({
        'raw_section_rows': len(rows),
        'courses': len(courses),
        'courses_with_sections': len(scheduled),
        'courses_without_sections': len(courses) - len(scheduled),
        'sections': len(sections),
        'meetings': len(meetings),
        'meetings_arranged': sum(1 for m in meetings if m['arranged']),
        'meetings_days_derived': sum(1 for m in meetings if m.get('days_provenance') == 'DERIVED'),
        'instructors': len(instructors),
        'section_instructor_links': len(sec_inst),
        'subjects': len({c['subject'] for c in courses.values() if c['subject']}),
        'schools': len({c['school'] for c in courses.values() if c['school']}),
        'buildings': len({m['building'] for m in meetings if m['building']}),
        'sections_multi_meeting': sum(1 for s in sections.values() if len(s['meeting_ids']) > 1),
        'sections_multi_instructor': sum(1 for s in sections.values() if len(s['instructor_ids']) > 1),
        'sections_open': sum(1 for s in sections.values() if s['status'] == 'OPEN'),
        'sections_closed': sum(1 for s in sections.values() if s['status'] == 'CLOSED'),
        'sections_online': sum(1 for s in sections.values() if s['delivery_mode'] == 'ONLINE'),
        'pagination': 'n/a - single complete registrar export, not a paged API',
        'termination_condition': 'end of source file reached',
        'failed_requests': 0,
        'complete': len(report['validation_errors']) == 0,
    })

    os.makedirs(os.path.join(DATA, 'reports'), exist_ok=True)
    w = lambda name, obj: json.dump(
        obj, open(os.path.join(DATA, name), 'w', encoding='utf-8'),
        ensure_ascii=False, separators=(',', ':'))

    w('courses.json', list(courses.values()))
    w('sections.json', list(sections.values()))
    w('meetings.json', meetings)
    w('instructors.json', list(instructors.values()))

    compact = compact_for_app(courses, sections, meetings)
    w('schedule-data.json', {
        'metadata': {
            'institution': INSTITUTION, 'campus': CAMPUS, 'term': TERM,
            'retrieved_at': report['retrieved_at'],
            'scrape_run_id': run_id,
            'source': report['source_endpoint'],
            'course_count': len(courses), 'section_count': len(sections),
            'meeting_count': len(meetings),
            'day_order': DAY_ORDER,
            'schema': ['code', 'title', 'cr_min', 'cr_max', 'subject', 'level', 'sections'],
            'section_schema': ['class_number', 'component', 'open', 'capacity', 'available',
                               'waitlist', 'instructor_ids', 'meetings', 'topic',
                               'restricted', 'delivery_mode'],
            'meeting_schema': ['type', 'day_mask', 'start_min', 'end_min', 'building', 'room'],
        },
        'instructors': {i['instructor_id']: i['full_name'] for i in instructors.values()},
        'courses': compact,
    })

    with open(os.path.join(DATA, 'courses.csv'), 'w', newline='', encoding='utf-8') as fh:
        cw = csv.writer(fh)
        cw.writerow(['code', 'subject', 'number', 'title', 'credits_min', 'credits_max',
                     'level', 'school', 'section_count'])
        for c in sorted(courses.values(), key=lambda x: x['code']):
            cw.writerow([c['code'], c['subject'], c['number'], c['title'], c['credits_min'],
                         c['credits_max'], c['level'], c['school'], len(c['section_ids'])])

    with open(os.path.join(DATA, 'sections.csv'), 'w', newline='', encoding='utf-8') as fh:
        cw = csv.writer(fh)
        cw.writerow(['class_number', 'course_code', 'component', 'status', 'topic',
                     'capacity', 'available', 'waitlist', 'delivery_mode',
                     'instructors', 'days', 'start', 'end', 'building', 'room'])
        by_sec = collections.defaultdict(list)
        for m in meetings:
            by_sec[m['section_id']].append(m)
        for s in sorted(sections.values(), key=lambda x: x['class_number']):
            names = '; '.join(instructors[i]['full_name'] for i in s['instructor_ids'])
            for m in by_sec[s['section_id']]:
                cw.writerow([s['class_number'], s['course_code'], m['meeting_type'], s['status'],
                             s['topic'] or '', s['enrollment']['capacity'],
                             s['enrollment']['available'], s['enrollment']['waitlist'],
                             s['delivery_mode'] or '', names, ''.join(m['days']),
                             m['start_time'] or '', m['end_time'] or '',
                             m['building'] or '', m['room'] or ''])

    rpt_path = os.path.join(DATA, 'reports', run_id + '.json')
    json.dump(report, open(rpt_path, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    print('=' * 62)
    print('INGEST REPORT  %s' % run_id)
    print('=' * 62)
    for k in ['institution', 'campus', 'term', 'retrieved_at', 'source_file',
              'source_lines', 'raw_section_rows', 'courses', 'courses_with_sections',
              'courses_without_sections', 'sections', 'meetings', 'meetings_arranged',
              'meetings_days_derived',
              'sections_multi_meeting', 'sections_multi_instructor',
              'sections_open', 'sections_closed', 'sections_online',
              'instructors', 'subjects', 'schools', 'buildings', 'complete']:
        print('  %-26s %s' % (k, report[k]))
    print('  %-26s %d' % ('validation_errors', len(report['validation_errors'])))
    print('  %-26s %d' % ('warnings', len(report['warnings'])))
    for e in report['validation_errors'][:10]:
        print('     ERR  ' + e)
    for wn in report['warnings'][:10]:
        print('     WARN ' + wn)
    print('  report -> %s' % os.path.relpath(rpt_path, ROOT))
    for f in ['courses.json', 'sections.json', 'meetings.json', 'instructors.json',
              'schedule-data.json', 'courses.csv', 'sections.csv']:
        p = os.path.join(DATA, f)
        print('  %-22s %8.1f KB' % (f, os.path.getsize(p) / 1024))


if __name__ == '__main__':
    main()
