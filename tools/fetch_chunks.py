# -*- coding: utf-8 -*-
"""补充下载 UI 里动态加载的分片（lazy chunk）与哈希资源。"""
import re
import urllib.request
from pathlib import Path

BASE = "https://app.httptoolkit.tech/"
PROXY = "http://127.0.0.1:7897"
UI = Path(__file__).resolve().parent.parent / "ui"

opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
)

BUNDLE_RE = re.compile(r"""["'/]([A-Za-z0-9_\-\.]{3,200}\.bundle\.js)["']""")
HASH_RE = re.compile(r"""["'/]([a-f0-9]{16,24}\.(?:js|ttf|woff2?|png|svg|json))["']""")


def collect():
    found = set()
    for f in UI.glob("*.js"):
        text = f.read_text("utf-8", "ignore")
        found |= set(BUNDLE_RE.findall(text))
        found |= set(HASH_RE.findall(text))
    return sorted(found)


def main():
    todo = [n for n in collect() if not (UI / n).exists()]
    print("待下载:", len(todo))
    for name in todo:
        try:
            req = urllib.request.Request(BASE + name, headers={"User-Agent": "Mozilla/5.0"})
            with opener.open(req, timeout=60) as r:
                data = r.read()
            (UI / name).write_bytes(data)
            print(f"[ok] {name} {len(data)}")
        except Exception as e:  # noqa: BLE001
            print(f"[skip] {name}: {e}")


if __name__ == "__main__":
    main()
