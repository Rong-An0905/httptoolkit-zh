# -*- coding: utf-8 -*-
"""恢复 HTTP Toolkit 安装目录里被改过的 API server（撤销 CORS 白名单补丁）。"""
import shutil
from pathlib import Path

P = Path(r"D:\HTTP Toolkit\resources\httptoolkit-server\bundle\index.js")
BAK = P.with_suffix(".js.bak-orig")

if BAK.exists():
    shutil.copy2(BAK, P)
    print("已还原：", P)
else:
    print("没有找到备份文件，安装目录可能本来就是原版：", BAK)
