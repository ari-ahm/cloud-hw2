"""Plain-text HTTP responses backed by the shared file queue."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from app.queue import join, take


class QueueServer(ThreadingHTTPServer):
    request_queue_size = 512
    daemon_threads = True


def serve(host: str, port: int, data_dir: str) -> None:
    path = Path(data_dir) / "queue.txt"
    path.parent.mkdir(parents=True, exist_ok=True)

    class Handler(BaseHTTPRequestHandler):
        def reply(self, status: int, text: str) -> None:
            body = text.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path == "/health":
                self.reply(200, "ok")
            else:
                self.reply(404, "not found")

        def do_POST(self) -> None:
            if self.path == "/join":
                try:
                    size = int(self.headers.get("Content-Length", "0"))
                    if size < 1 or size > 4096:
                        raise ValueError("invalid body length")
                    payload = json.loads(self.rfile.read(size))
                    if not isinstance(payload, dict):
                        raise ValueError("expected object")
                    ticket = join(path, payload.get("name"))
                except (ValueError, UnicodeError):
                    self.reply(400, "invalid name")
                else:
                    self.reply(200, str(ticket))
            elif self.path == "/next":
                try:
                    name = take(path)
                except LookupError:
                    self.reply(404, "empty")
                else:
                    self.reply(200, name)
            else:
                self.reply(404, "not found")

    with QueueServer((host, port), Handler) as server:
        server.serve_forever()


def main() -> None:
    serve("0.0.0.0", int(os.environ.get("PORT", "8000")), os.environ.get("DATA_DIR", "/data"))


if __name__ == "__main__":
    main()
