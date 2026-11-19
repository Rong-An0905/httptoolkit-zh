# -*- coding: utf-8 -*-
"""把词表注入模板，生成 ui/i18n-zh.js，并在 index.html 里挂上。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UI = ROOT / "ui"
TEMPLATE = (ROOT / "i18n-zh.template.js").read_text("utf-8")
DICT = json.loads((ROOT / "dict.json").read_text("utf-8"))
OVERRIDES = json.loads((ROOT / "overrides.json").read_text("utf-8"))
INDEX = UI / "index.html"

clean = {en: zh for en, zh in DICT.items() if zh and zh.strip() and zh.strip() != en.strip()}
clean.update(OVERRIDES)   # 专有名词等人工校正优先
print("词条:", len(clean))

js = TEMPLATE.replace("__DICT__", json.dumps(clean, ensure_ascii=False, separators=(",", ":")))
(UI / "i18n-zh.js").write_text(js, "utf-8")

html = INDEX.read_text("utf-8")
html = re.sub(r'\s*<script[^>]*src="i18n-zh\.js"[^>]*></script>', "", html)
tag = '<script defer="defer" src="i18n-zh.js"></script>'
if 'src="main.js"' in html:
    html = html.replace('<script defer="defer" src="main.js"></script>',
                        '<script defer="defer" src="main.js"></script>' + tag, 1)
else:
    html = html.replace("</body>", tag + "</body>", 1)
INDEX.write_text(html, "utf-8")
print("index.html 已注入 i18n-zh.js")
