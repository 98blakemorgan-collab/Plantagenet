"""Decode Drive-connector download results (JSON with base64 content) into files."""
import base64, glob, json, os, sys
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for f in glob.glob('/root/.claude/projects/-home-user-Plantagenet/*/tool-results/mcp-Google_Drive-download_file_content-*.txt'):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    name = d.get('title')
    if not name:
        continue
    p = os.path.join(out, name)
    if not os.path.exists(p):
        open(p, 'wb').write(base64.b64decode(d['content']))
        print('saved', name, os.path.getsize(p))
