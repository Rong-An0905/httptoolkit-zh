# -*- coding: utf-8 -*-
"""批量机器翻译候选文案（Google gtx 免费端点），结果缓存在 dict.json。"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "strings.json"
CACHE = ROOT / "dict.json"
PROXY = "http://127.0.0.1:7897"
EP = "https://translate.googleapis.com/translate_a/single"

opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
)


def translate_batch(lines):
    q = "\n".join(lines)
    url = EP + "?" + urllib.parse.urlencode(
        {"client": "gtx", "sl": "en", "tl": "zh-CN", "dt": "t", "q": q}
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with opener.open(req, timeout=40) as r:
        data = json.loads(r.read().decode("utf-8"))
    text = "".join(seg[0] for seg in data[0] if seg and seg[0])
    return text.split("\n")


def main():
    src = json.loads(SRC.read_text("utf-8"))
    cache = json.loads(CACHE.read_text("utf-8")) if CACHE.exists() else {}
    todo = [s for s in src if s not in cache]
    print("待翻译:", len(todo), "/", len(src))

    batch_size = 20
    done = 0
    for i in range(0, len(todo), batch_size):
        chunk = todo[i:i + batch_size]
        out = None
        for attempt in range(3):
            try:
                out = translate_batch(chunk)
                break
            except Exception as e:  # noqa: BLE001
                print(f"  重试 {attempt + 1}: {e}")
                time.sleep(2 + attempt * 3)
        if out and len(out) == len(chunk):
            for en, zh in zip(chunk, out):
                cache[en] = zh.strip()
        else:
            print("  批量对齐失败，逐条翻译")
            for en in chunk:
                try:
                    r = translate_batch([en])
                    cache[en] = r[0].strip()
                except Exception as e:  # noqa: BLE001
                    print("   失败:", en, e)
                time.sleep(0.2)
        done += len(chunk)
        if done % 200 < batch_size:
            CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), "utf-8")
            print(f"  进度 {done}/{len(todo)}")
        time.sleep(0.25)

    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), "utf-8")
    print("完成，词条:", len(cache))


if __name__ == "__main__":
    sys.exit(main())
