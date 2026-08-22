#!/usr/bin/env python3
"""Generate the derived builds from index.html.

  artifact.html              — body only, for publishing. Artifacts supply
                               their own <!doctype>/<head>/<body>.
  crimson-command-share.html — standalone, boots blank so it can be handed
                               to anyone without one person's semester in it.

Both are generated, never hand-edited, so they cannot drift from the source.
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

# --- the shareable standalone copy: same app, no personal data ---
share = src.replace("const BOOT_PROFILE = 'owner';", "const BOOT_PROFILE = 'blank';", 1)
if "const BOOT_PROFILE = 'blank';" not in share:
    sys.exit('ERROR: BOOT_PROFILE switch not found')
share = share.replace('<title>Crimson Command</title>',
                      '<title>Crimson Command</title>', 1)
shp = pathlib.Path('crimson-command-share.html')
shp.write_text(share)
print(f'wrote {shp} ({len(share)} bytes, boots blank)')
for tag in ('!doctype', 'html', 'head', 'body'):
    if re.search(r'</?' + tag + r'[\s>]', body, flags=re.I):
        sys.exit(f'ERROR: <{tag}> survived the strip')
if '<title>' not in body[:8192]:
    sys.exit('ERROR: <title> must sit in the first 8KB')
print('checks passed')
