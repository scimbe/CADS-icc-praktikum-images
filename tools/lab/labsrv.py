#!/usr/bin/env python3
"""Kleiner Lehr-Webserver fuer das ICC-Praktikum (nur Standardbibliothek).

Verhalten per Umgebungsvariable, damit ein Image viele "Fehlerbilder" erzeugt:

  PORT         Lauschport (Standard 8080)
  NAME         Anzeigename in der Antwort (Standard: Hostname)
  READY_AFTER  Sekunden nach Start, bis /ready 200 liefert (Standard 0)
  DELAY        feste Verzoegerung in Sekunden vor jeder Antwort auf / (Standard 0)
  MODE         ok | err500 | flap | hang
                 err500  jede Antwort auf / ist 500
                 flap    jede zweite Antwort auf / ist 503
                 hang    Verbindung annehmen, nie antworten
"""
import os
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "8080"))
NAME = os.environ.get("NAME", socket.gethostname())
READY_AFTER = float(os.environ.get("READY_AFTER", "0"))
DELAY = float(os.environ.get("DELAY", "0"))
MODE = os.environ.get("MODE", "ok")
START = time.time()
_counter = 0
_lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, code, body, ctype="text/plain; charset=utf-8"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        global _counter
        path = self.path.split("?")[0]
        if path == "/healthz":
            return self._send(200, "ok\n")
        if path == "/ready":
            if time.time() - START >= READY_AFTER:
                return self._send(200, "ready\n")
            return self._send(503, "not ready\n")
        if path.startswith("/status/"):
            try:
                return self._send(int(path.rsplit("/", 1)[1]), "status\n")
            except ValueError:
                return self._send(400, "bad status\n")
        if path == "/slow":
            secs = 3.0
            if "s=" in self.path:
                try:
                    secs = float(self.path.split("s=", 1)[1].split("&")[0])
                except ValueError:
                    pass
            time.sleep(secs)
            return self._send(200, f"slept {secs}s\n")
        if path == "/big":
            kb = 100
            if "kb=" in self.path:
                try:
                    kb = int(self.path.split("kb=", 1)[1].split("&")[0])
                except ValueError:
                    pass
            return self._send(200, "x" * (kb * 1024))
        # Standardpfad
        if MODE == "hang":
            time.sleep(3600)
            return None
        if DELAY:
            time.sleep(DELAY)
        with _lock:
            _counter += 1
            n = _counter
        if MODE == "err500":
            return self._send(500, "boom\n")
        if MODE == "flap" and n % 2 == 0:
            return self._send(503, "flapping\n")
        xff = self.headers.get("X-Forwarded-For", "-")
        return self._send(
            200,
            f"hello from {NAME}\nclient={self.client_address[0]} x-forwarded-for={xff} host={self.headers.get('Host', '-')}\n",
        )

    def log_message(self, fmt, *args):
        print("%s %s" % (self.client_address[0], fmt % args), flush=True)


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    srv.daemon_threads = True
    print(f"labsrv {NAME} listening on :{PORT} mode={MODE}", flush=True)
    srv.serve_forever()
