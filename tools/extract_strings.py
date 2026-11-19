# -*- coding: utf-8 -*-
"""从 UI 打包产物里抽取候选英文界面文案，供机器翻译。"""
import json
import re
from collections import Counter
from pathlib import Path

UI = Path(__file__).resolve().parent.parent / "ui"
OUT = Path(r"D:\huayuncopy\_httptoolkit_work\strings.json")

STR_RE = re.compile(r"""(?<![A-Za-z0-9_])(?:"([^"\\\n]{2,320})"|'([^'\\\n]{2,320})')""")
BAD_CHARS = set('{}<>|`~\\^$=;*')
CODE_WORDS = (
    "=>", "&&", "||", "!==", "===", "!=", "==", "function", "return ", "var ",
    "new ", "throw", "typeof", "this.", "null", "undefined", "prototype",
    "charAt", "substring", ".length", "document.", "window.", "parseInt",
)
SKIP_SUFFIX = (
    ".js", ".css", ".png", ".jpg", ".svg", ".json", ".map", ".ttf", ".woff",
    ".woff2", ".wasm", ".html", ".ico", ".gif", ".bundle",
)
# 这些出现在正文里会被误翻的动态值
BLACKLIST = {
    "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE",
    "HTTP", "HTTPS", "TCP", "UDP", "TLS", "SSL", "DNS", "CORS", "JSON",
}


def unescape(s: str) -> str:
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\n", "\n").replace("\\t", "\t")


def looks_like_ui(text: str) -> bool:
    if not text or len(text) < 2 or len(text) > 300:
        return False
    if not re.match(r"[A-Za-z0-9]", text):
        return False
    if text in BLACKLIST:
        return False
    if not re.search(r"[A-Za-z]", text):
        return False
    if any(c in BAD_CHARS for c in text):
        return False
    lowered = text.lower()
    if any(w in lowered or w in text for w in CODE_WORDS):
        return False
    if lowered.endswith(SKIP_SUFFIX) or "://" in text or lowered.startswith("www."):
        return False
    letters = sum(c.isalpha() or c.isspace() or c in ".,'!?:-()/" for c in text)
    if letters / len(text) < 0.75:
        return False
    if re.fullmatch(r"[a-z0-9_\-.$/]+", text):
        return False
    if re.fullmatch(r"[A-F0-9]{6,}", text):
        return False
    if len(text.split()) > 34:
        return False
    if " " not in text:
        return bool(re.fullmatch(r"[A-Z][A-Za-z\-']{2,20}", text))
    return True


def main():
    counter = Counter()
    for f in [UI / "main.js", UI / "apis.js", UI / "mockttp.js"]:
        text = f.read_text("utf-8", "ignore")
        for m in STR_RE.finditer(text):
            s = unescape((m.group(1) or m.group(2) or "")).strip()
            if looks_like_ui(s):
                counter[s] += 1
    strings = sorted(counter)
    OUT.write_text(json.dumps(strings, ensure_ascii=False, indent=0), "utf-8")
    print("候选文案:", len(strings))
    for s in strings[:40]:
        print("  ", repr(s))
    print("  ...")
    for s in strings[-20:]:
        print("  ", repr(s))


if __name__ == "__main__":
    main()
