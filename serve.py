# -*- coding: utf-8 -*-
"""本地静态服务器：托管汉化后的 HTTP Toolkit UI。"""
import http.server
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
UI = os.path.join(ROOT, "ui")
LOG = os.path.join(ROOT, "http.log")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8899


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI, **kwargs)

    def log_message(self, fmt, *args):
        line = "%s %s\n" % (self.log_date_time_string(), fmt % args)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
