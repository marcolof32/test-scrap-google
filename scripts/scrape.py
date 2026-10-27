"""Read a public Google Photos shared album and write album.js with the photo URLs.

No photo is downloaded: the page loads each image straight from Google
(lh3.googleusercontent.com) by appending a size suffix such as =w420.

Usage: python scripts/scrape.py            (reads sections.json, writes album.js)
"""
import json, os, re, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"


def get(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r:
        return r.geturl(), r.read().decode("utf-8")


def items_of(page):
    out = []
    for it in page[1] or []:
        if isinstance(it, list) and len(it) > 2 and isinstance(it[1], list):
            out.append({"id": it[0], "url": it[1][0], "w": it[1][1], "h": it[1][2], "ts": it[2]})
    return out


def scrape(share_url):
    final, html = get(share_url)
    m = re.search(r"/share/([^?]+)\?key=([^&]+)", final)
    media_key, auth_key = m.group(1), m.group(2)

    block = re.search(r"AF_initDataCallback\(\{key: 'ds:1', hash: '\d+', data:(.*?), sideChannel:", html, re.S)
    page = json.loads(block.group(1))
    photos, token = items_of(page), page[2]
    title = page[3][1] if len(page) > 3 and page[3] else ""

    # The first page holds 300 items; the rest come from the same RPC the album page uses.
    while token:
        args = json.dumps([media_key, token, None, auth_key])
        body = urllib.parse.urlencode({"f.req": json.dumps([[["snAcKc", args, None, "generic"]]])}).encode()
        _, txt = get("https://photos.google.com/_/PhotosUi/data/batchexecute?rpcids=snAcKc&rt=c", body)
        inner = next((json.loads(json.loads(l)[0][2]) for l in txt.splitlines() if l.startswith('[["wrb.fr"')), None)
        if inner is None:
            break
        photos += items_of(inner)
        token = inner[2] if len(inner) > 2 else None

    seen, uniq = set(), []
    for p in photos:
        if p["id"] not in seen:
            seen.add(p["id"]); uniq.append(p)
    uniq.sort(key=lambda p: p["ts"] or 0)
    return title, uniq


cfg = json.load(open(os.path.join(ROOT, "sections.json"), encoding="utf-8"))
title, photos = scrape(cfg["album"])
album = {
    "title": title,
    "photos": [[p["url"], p["w"], p["h"], p["ts"]] for p in photos],
    "hero": cfg["hero"],
    "sections": cfg["sections"],
}
with open(os.path.join(ROOT, "album.js"), "w", encoding="utf-8") as f:
    f.write("window.ALBUM=" + json.dumps(album, ensure_ascii=False, separators=(",", ":")) + ";\n")
print(f"{title}: {len(photos)} photos -> album.js")
