"""Read-only loopback preview of the D50 tool with the native reader mounted."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

p = argparse.ArgumentParser()
p.add_argument('--reader-root', type=Path, required=True)
p.add_argument('--port', type=int, default=8767)
args = p.parse_args()
tool = Path(__file__).resolve().parents[1] / 'backend/course-capsule-v1/adapters/d50-surface-v1/portable'
reader = args.reader_root.resolve()


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        relative = unquote(urlsplit(path).path).lstrip('/')
        root, part = (reader, relative[7:]) if relative.startswith('reader/') else (tool, relative)
        target = (root / part).resolve()
        if not target.is_relative_to(root.resolve()):
            return str(tool / '__forbidden__')
        return str(target)

    def list_directory(self, path):
        self.send_error(403)
        return None


print(f'D50 read-only preview: http://127.0.0.1:{args.port}/', flush=True)
ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
