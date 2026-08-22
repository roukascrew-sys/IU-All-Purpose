#!/bin/sh
# Extract the inline script and syntax-check it.
cd /home/user/IU-All-Purpose
python3 -c "
import re
s=open('index.html').read()
m=re.search(r'<script>\n(.*)</script>', s, re.S)
open('/tmp/claude-0/-home-user-IU-All-Purpose/d966d82b-299f-594d-b0a0-42f22774b6a9/scratchpad/app.js','w').write(m.group(1))"
node --check /tmp/claude-0/-home-user-IU-All-Purpose/d966d82b-299f-594d-b0a0-42f22774b6a9/scratchpad/app.js && echo "SYNTAX OK"
