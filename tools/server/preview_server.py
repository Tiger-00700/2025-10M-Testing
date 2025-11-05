#!/usr/bin/env python3
import argparse
import http.server
import io
import os
import socketserver
import sys
from pathlib import Path

INJECT_MARKER = "__watchReloadInjected"
RELOAD_PATH = "/__reload"

CLIENT_SNIPPET = f"""
<script id=\"{INJECT_MARKER}\">(function(){{
  const url = '{RELOAD_PATH}';
  let last = '';
  async function tick(){{
    try {{
      const r = await fetch(url, {{ cache: 'no-store' }});
      if (!r.ok) throw new Error('bad response');
      const text = (await r.text()).trim();
      if (last && text !== last) {{ location.reload(); return; }}
      last = text;
    }} catch(e) {{ /* ignore */ }}
    setTimeout(tick, 1000);
  }}
  tick();
}})();</script>
""".strip()

class PreviewHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, token_file=None, **kwargs):
        self._token_file = Path(token_file) if token_file else None
        super().__init__(*args, directory=directory, **kwargs)

    def _read_token(self):
        if not self._token_file:
            return ""
        try:
            return self._token_file.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return ""

    def do_GET(self):
        if self.path == RELOAD_PATH:
            body = self._read_token().encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        # For HTML files, inject the reload client snippet just before </body>
        if self.path.endswith('.html'):
            full_path = self.translate_path(self.path)
            p = Path(full_path)
            if p.exists() and p.suffix.lower() == '.html':
                try:
                    raw = p.read_text(encoding='utf-8', errors='ignore')
                    if INJECT_MARKER not in raw:
                        if '</body>' in raw:
                            raw = raw.replace('</body>', f"\n{CLIENT_SNIPPET}\n</body>")
                        else:
                            raw = raw + "\n" + CLIENT_SNIPPET
                    data = raw.encode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Cache-Control', 'no-store')
                    self.send_header('Content-Length', str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                except Exception:
                    pass
        return super().do_GET()


def main():
    ap = argparse.ArgumentParser(description='Preview server with live reload for book HTML')
    ap.add_argument('--dir', required=True, help='Directory to serve (preview output dir)')
    ap.add_argument('--port', type=int, default=9876)
    ap.add_argument('--token', default='reload.token', help='Reload token filename inside dir')
    args = ap.parse_args()

    root = Path(args.dir).resolve()
    if not root.exists():
        print(f"Directory not found: {root}", file=sys.stderr)
        return 2
    os.chdir(root)
    token_path = root / args.token

    handler = lambda *h_args, **h_kwargs: PreviewHandler(*h_args, directory=str(root), token_file=str(token_path), **h_kwargs)
    with socketserver.ThreadingTCPServer(('127.0.0.1', args.port), handler) as httpd:
        print(f"[server] Serving {root} at http://127.0.0.1:{args.port}/book.html")
        print(f"[server] Reload token: {token_path}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("[server] Stopping...")
            return 0

if __name__ == '__main__':
    sys.exit(main())
