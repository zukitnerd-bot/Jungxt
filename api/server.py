#!/usr/bin/env python3
"""Jungxt API — the Urban Dictionary for texting, as a JSON API.

Zero dependencies. Run:  python3 server.py  [port]
Then visit http://localhost:8000/ for the docs.

Endpoints:
  GET /api/definitions            all entries (?q=search, ?cat=category, ?limit=n, ?sort=top|new|az)
  GET /api/definition/{term}      single entry by term
  GET /api/random                 random entry
  GET /api/word-of-day            deterministic daily entry
  GET /api/categories             list of categories
  GET /                           this documentation page
"""

import json
import os
import random
import urllib.parse
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "definitions.json"), encoding="utf-8") as f:
    ENTRIES = json.load(f)

BY_TERM = {e["term"].lower(): e for e in ENTRIES}


def entry_to_api(e):
    return {
        "term": e["term"],
        "pronunciation": e.get("pron", ""),
        "part_of_speech": e.get("pos", ""),
        "category": e.get("cat", ""),
        "definition": e.get("def", ""),
        "meant_to_type": e.get("meant", ""),
        "example_thread": [
            {"from": msg[0], "text": msg[1]} for msg in e.get("ex", [])
        ],
        "coined_by": e.get("by", ""),
        "votes": e.get("votes", 0),
    }


def send_json(handler, obj, status=200):
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


DOCS_HTML = """<!doctype html><html><head><meta charset="utf-8">
<title>Jungxt API</title>
<style>body{font-family:system-ui;max-width:720px;margin:40px auto;padding:0 20px;line-height:1.6}
code{background:#f0f0f0;padding:2px 6px;border-radius:4px}pre{background:#111;color:#0f0;padding:16px;border-radius:8px;overflow:auto}</style>
</head><body>
<h1>Jungxt API</h1>
<p>The Urban Dictionary for texting — as JSON. Free for non-commercial use.
Commercial licensing: <b>Zukitnerd@gmail.com</b></p>
<h2>Endpoints</h2>
<ul>
<li><code>GET /api/definitions</code> — all entries. Params: <code>q</code> (search), <code>cat</code> (category), <code>limit</code>, <code>sort</code> (top|new|az)</li>
<li><code>GET /api/definition/{term}</code> — one entry, e.g. <code>/api/definition/sven</code></li>
<li><code>GET /api/random</code> — random entry</li>
<li><code>GET /api/word-of-day</code> — today's featured entry (stable per date)</li>
<li><code>GET /api/categories</code> — list of categories</li>
</ul>
<h2>Example</h2>
<pre>$ curl {base}/api/definition/sven</pre>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            host = self.headers.get("Host", "localhost")
            body = DOCS_HTML.replace("{base}", f"http://{host}").encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/definitions":
            results = ENTRIES
            q = qs.get("q", [""])[0].lower()
            if q:
                results = [e for e in results
                           if q in e["term"].lower() or q in e.get("def", "").lower()]
            cat = qs.get("cat", [""])[0].lower()
            if cat:
                results = [e for e in results if e.get("cat", "").lower() == cat]
            sort = qs.get("sort", [""])[0]
            if sort == "top":
                results = sorted(results, key=lambda e: e.get("votes", 0), reverse=True)
            elif sort == "az":
                results = sorted(results, key=lambda e: e["term"].lower())
            try:
                limit = int(qs.get("limit", ["0"])[0])
            except ValueError:
                limit = 0
            if limit > 0:
                results = results[:limit]
            send_json(self, {"count": len(results),
                             "results": [entry_to_api(e) for e in results]})
            return

        if path.startswith("/api/definition/"):
            term = urllib.parse.unquote(path[len("/api/definition/"):]).lower()
            e = BY_TERM.get(term)
            if e:
                send_json(self, entry_to_api(e))
            else:
                send_json(self, {"error": f"No definition for '{term}'"}, 404)
            return

        if path == "/api/random":
            send_json(self, entry_to_api(random.choice(ENTRIES)))
            return

        if path == "/api/word-of-day":
            seed = int(date.today().strftime("%Y%m%d"))
            rng = random.Random(seed)
            send_json(self, {**entry_to_api(rng.choice(ENTRIES)),
                             "date": date.today().isoformat()})
            return

        if path == "/api/categories":
            send_json(self, {"categories": sorted({e.get("cat", "") for e in ENTRIES})})
            return

        send_json(self, {"error": "Not found. See / for docs."}, 404)


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    srv = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Jungxt API on http://localhost:{port}/  ({len(ENTRIES)} definitions)")
    srv.serve_forever()
