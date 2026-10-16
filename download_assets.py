"""Download only the public assets referenced by the supplied page and CSS."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import re
from urllib.parse import urljoin, urlsplit, unquote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
BASE = 'https://www.fsi.net.tw/'
html = '\n'.join(p.read_text(encoding='utf-8-sig') for p in ROOT.glob('source-training*.html'))
css = (ROOT / 'css/training.css').read_text(encoding='utf-8-sig')
paths = set()
for path in re.findall(r'(?:src)=["\']([^"\']+)["\']', html, re.I):
    if path.startswith(('images/', 'upload/', '/upload/')):
        paths.add(path.lstrip('/'))
for path in re.findall(r'url\(\s*["\']?([^\)"\']+)', css):
    paths.add(urlsplit(urljoin(BASE + 'css/training.css', path)).path.lstrip('/'))

def download(path):
    target = ROOT / unquote(path)
    if target.exists():
        return {'path': path, 'status': 'exists'}
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(Request(urljoin(BASE, path), headers={'User-Agent': 'Mozilla/5.0'}), timeout=40) as response:
            target.write_bytes(response.read())
        return {'path': path, 'status': 'downloaded', 'bytes': target.stat().st_size}
    except Exception as exc:
        return {'path': path, 'status': 'failed', 'error': str(exc)}

with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(download, sorted(paths)))
(ROOT / 'reference/assets.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'assets': len(results), 'failed': [r for r in results if r['status']=='failed']}, ensure_ascii=False))
