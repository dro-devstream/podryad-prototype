"""Собирает prototype/index.html: вставляет иллюстрации и аватары как data URI.

Запуск: python3 -I build.py  (из папки prototype)
Аватары кешируются в src/avatars/, иллюстрации берутся из ../design/img/.
"""
import base64
import pathlib
import re
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
IMG_DIR = ROOT.parent / 'design' / 'img'
AV_DIR = ROOT / 'src' / 'avatars'

# ключ -> (seed, цвет фона); стиль DiceBear Notionists, лицензия CC0 1.0
AVATARS = {
    'ales': ('Ales Kovalchuk', 'ffd5c2'), 'pavel_s': ('Pavel Sidorenko', 'c9b8ff'),
    'viktor': ('Viktor Dubovik', 'bff0df'), 'yana': ('Yana Lis', 'ffe9a8'),
    'oleg': ('Oleg Zhuk', 'bfe3ff'), 'sergey': ('Sergey Neman', 'ffd5c2'),
    'hanna': ('Hanna K', 'ffe9a8'), 'pavel_n': ('Pavel N', 'bfe3ff'),
    'ksenia': ('Ksenia L', 'ffc2d6'), 'dmitry': ('Dmitry V', 'bff0df'),
    'olga': ('Olga Sh', 'c9b8ff'), 'andrei': ('Andrei T', 'ffe9a8'),
    'maria': ('Maria M', 'ffc2d6'), 'ivan': ('Ivan B', 'bfe3ff'),
    'katya': ('Katsiaryna', 'bff0df'), 'me': ('Client Me', 'ffe9a8'),
}


def data_uri(svg: bytes) -> str:
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg).decode()


def avatar(key: str) -> bytes:
    AV_DIR.mkdir(parents=True, exist_ok=True)
    path = AV_DIR / f'{key}.svg'
    if not path.exists():
        seed, bg = AVATARS[key]
        url = ('https://api.dicebear.com/9.x/notionists/svg?seed='
               + urllib.parse.quote(seed) + f'&backgroundColor={bg}&radius=50')
        with urllib.request.urlopen(url, timeout=30) as r:
            body = r.read()
        if not body.lstrip().startswith(b'<svg'):
            sys.exit(f'avatar {key}: not an SVG')
        path.write_bytes(body)
    return path.read_bytes()


def main() -> None:
    html = (ROOT / 'src' / 'index.template.html').read_text(encoding='utf-8')
    html = re.sub(r'__IMG_([a-z-]+)__',
                  lambda m: data_uri((IMG_DIR / f'{m.group(1)}.svg').read_bytes()), html)
    html = re.sub(r'__AV_([a-z_]+)__', lambda m: data_uri(avatar(m.group(1))), html)
    left = re.findall(r'__(?:IMG|AV)_[a-z_-]+__', html)
    if left:
        sys.exit(f'unresolved: {left}')
    (ROOT / 'index.html').write_text(html, encoding='utf-8')
    print(f'index.html: {len(html.encode()) // 1024} KB')


if __name__ == '__main__':
    main()
