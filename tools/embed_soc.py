#!/usr/bin/env python3
"""Inject data/schedule-data.json into index.html's <script id="socData"> tag.

Kept as a build step rather than pasting a megabyte into the source by hand,
so index.html stays reviewable and the embedded copy can never drift from
what tools/ingest_soc.py produced.

    python3 tools/ingest_soc.py     # parse the registrar export
    python3 tools/embed_soc.py      # embed it in the app
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = re.compile(
    r'(<script type="application/json" id="socData">)(.*?)(</script>)', re.S)


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'index.html')
    payload = os.path.join(ROOT, 'data', 'schedule-data.json')
    blob = open(payload, encoding='utf-8').read()

    # The JSON sits in a raw-text element, so the only sequence that could
    # break out of it is a closing script tag.
    if '</script' in blob.lower():
        raise SystemExit('refusing to embed: payload contains a closing script tag')

    html = open(target, encoding='utf-8').read()
    if not TAG.search(html):
        raise SystemExit('no <script id="socData"> placeholder found in ' + target)

    html = TAG.sub(lambda m: m.group(1) + blob + m.group(3), html, count=1)
    open(target, 'w', encoding='utf-8').write(html)

    meta = json.loads(blob)['metadata']
    print('embedded %s -> %s' % (os.path.relpath(payload, ROOT), os.path.relpath(target, ROOT)))
    print('  %s %s | %s courses, %s sections, %s meetings | %.1f KB payload'
          % (meta['term'], meta['campus'], meta['course_count'],
             meta['section_count'], meta['meeting_count'], len(blob) / 1024))
    print('  file now %.1f KB' % (os.path.getsize(target) / 1024))


if __name__ == '__main__':
    main()
