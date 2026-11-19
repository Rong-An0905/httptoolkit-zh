# -*- coding: utf-8 -*-
"""给 HTTP Toolkit 本地 API server 的 CORS 白名单补上本地 UI 源（可逆）。"""
import shutil
from pathlib import Path

P = Path(r"D:\HTTP Toolkit\resources\httptoolkit-server\bundle\index.js")
BAK = P.with_suffix(".js.bak-orig")

OLD = b"eg?[/^https:\\/\\/app\\.httptoolkit\\.tech$/]:"
NEW = b"eg?[/^https:\\/\\/app\\.httptoolkit\\.tech$/,/^http:\\/\\/127\\.0\\.0\\.1(:\\d+)?$/]:"

data = P.read_bytes()

if OLD not in data:
    if NEW in data:
        print("已经打过补丁，跳过")
    else:
        print("未找到目标片段，未修改")
    raise SystemExit(0)

if not BAK.exists():
    shutil.copy2(P, BAK)
    print("已备份 ->", BAK.name)

data = data.replace(OLD, NEW, 1)
P.write_bytes(data)
print("补丁完成：CORS 白名单已加入 http://127.0.0.1:<port>")
