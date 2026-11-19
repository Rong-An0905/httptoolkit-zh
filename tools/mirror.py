# -*- coding: utf-8 -*-
"""把 https://app.httptoolkit.tech 的 UI 静态资源镜像到本地。"""
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

BASE = "https://app.httptoolkit.tech/"
PROXY = "http://127.0.0.1:7897"
OUT = Path(__file__).resolve().parent.parent / "ui"

opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
)

ASSET_RE = re.compile(
    r"""["'\(]([A-Za-z0-9][A-Za-z0-9._\-]{0,150}\.(?:png|jpe?g|gif|svg|webp|ico|woff2?|ttf|eot|css|wasm|json|js|map))["'\)]"""
)
ABS_RE = re.compile(r"""https://app\.httptoolkit\.tech/([A-Za-z0-9._\-/]+)""")


def fetch(name: str) -> bytes:
    url = BASE + name.lstrip("/")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with opener.open(req, timeout=60) as r:
        return r.read()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    seen, queue = set(), ["index.html"]
    errors = []

    while queue:
        name = queue.pop(0)
        if name in seen:
            continue
        seen.add(name)
        target = OUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = fetch(name)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name}: {e}")
            continue
        target.write_bytes(data)
        print(f"[ok] {name} {len(data)}")

        if name.endswith((".html", ".js", ".css")):
            text = data.decode("utf-8", "ignore")
            for m in ASSET_RE.finditer(text):
                cand = m.group(1)
                if cand not in seen and not cand.startswith("http"):
                    queue.append(cand)
            for m in ABS_RE.finditer(text):
                cand = m.group(1)
                if cand not in seen:
                    queue.append(cand)

    print("\n== 完成 ==")
    print("文件数:", len(list(OUT.rglob('*'))))
    if errors:
        print("失败:")
        for e in errors:
            print(" -", e)


if __name__ == "__main__":
    sys.exit(main())
