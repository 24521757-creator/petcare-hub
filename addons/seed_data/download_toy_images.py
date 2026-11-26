import concurrent.futures
import io
import json
import pathlib
import urllib.request
from PIL import Image

ROOT = pathlib.Path('/mnt/extra-addons/seed_data')
IMG_DIR = ROOT / 'images'
IMG_DIR.mkdir(parents=True, exist_ok=True)
data = json.loads((ROOT / 'toys.json').read_text(encoding='utf-8'))

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'image/jpeg,image/png,image/webp,*/*;q=0.8',
}

def is_valid_image(raw):
    try:
        im = Image.open(io.BytesIO(raw))
        im.verify()
        return True
    except Exception:
        return False

def download_one(row):
    target = IMG_DIR / row['local_image']
    if target.is_file() and target.stat().st_size > 1500 and is_valid_image(target.read_bytes()):
        return ('cached', row['sku'], target.stat().st_size)
    urls = [row['image_url']]
    if '._AC_SS348_V1_.' in row['image_url']:
        urls.insert(0, row['image_url'].replace('._AC_SS348_V1_.', '._AC_SL600_V1_.'))
    last_err = None
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read()
                if len(content) > 1500 and is_valid_image(content):
                    target.write_bytes(content)
                    return ('ok', row['sku'], len(content))
                last_err = f'invalid image ({len(content)} bytes)'
        except Exception as e:
            last_err = str(e)
    return ('fail', row['sku'], last_err)

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(download_one, data))

ok = sum(1 for r in results if r[0] in ('ok', 'cached'))
failed = [r for r in results if r[0] == 'fail']
print(f'DOWNLOADED_OK={ok}/{len(data)} FAILED={len(failed)}')
for r in failed:
    print('FAIL:', r)
