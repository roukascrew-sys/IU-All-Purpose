#!/usr/bin/env python3
"""Generate the Artifact-ready body from index.html.

Artifacts are published into a host-supplied <!doctype>/<head>/<body>
skeleton, so the standalone wrappers have to come off. Everything else —
title, font link, styles, markup, script — is carried through verbatim so
the two files can never drift.
"""
import re, sys, pathlib

src = pathlib.Path('index.html').read_text()
body = src
for pat in (r'^<!DOCTYPE html>\s*', r'<html lang="en">\s*', r'</html>\s*$',
            r'<head>\s*', r'</head>\s*', r'<body>\s*', r'</body>\s*'):
    body = re.sub(pat, '', body, flags=re.M)
body = re.sub(r'<meta[^>]*>\s*', '', body)
out = pathlib.Path('artifact.html')
out.write_text(body.strip() + '\n')
print(f'wrote {out} ({len(body)} bytes)')
for tag in ('!doctype', 'html', 'head', 'body'):
    if re.search(r'</?' + tag + r'[\s>]', body, flags=re.I):
        sys.exit(f'ERROR: <{tag}> survived the strip')
if '<title>' not in body[:8192]:
    sys.exit('ERROR: <title> must sit in the first 8KB')
print('checks passed')
