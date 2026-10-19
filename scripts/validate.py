import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
d=json.loads((root/'dist/content.json').read_text(encoding='utf-8'))
assert len(d['services'])==9
assert len({p['id'] for p in d['projects']})==len(d['projects'])
for p in d['projects']:
    assert p['status'] in ('draft','published')
    if p['status']=='published':
        for key in ('title','category','video','aspectRatio'): assert p.get(key),key
for path in ('dist/index.html','dist/style.css','dist/app.js','netlify.toml'):
    assert (root/path).is_file(),path
html=(root/'dist/index.html').read_text(encoding='utf-8')
for anchor in ('home','work','about','contact'): assert f'id="{anchor}"' in html
assert d['profile']['instagram']=='https://www.instagram.com/vxnsh.rastogi/'
print('Content, navigation anchors, deployment files and draft visibility checks passed.')

