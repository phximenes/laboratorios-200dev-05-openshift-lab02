"""Aplicacao ficticia para a segunda pratica de administracao OpenShift."""
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    # Evita registrar cabecalhos ou a credencial demonstrativa.
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/healthz", "/readyz"):
            status, body = 200, {"status": "ok"}
        elif path == "/":
            status, body = 200, {
                "release": os.getenv("RELEASE", "blue"),
                "message": os.getenv("APP_MESSAGE", "sem configuracao"),
                "credential_configured": bool(os.getenv("API_TOKEN")),
            }
        elif path == "/admin":
            expected = os.getenv("API_TOKEN", "")
            received = self.headers.get("Authorization", "")
            valid = bool(expected) and hmac.compare_digest(received, "Bearer " + expected)
            status, body = (200, {"access": "allowed"}) if valid else (401, {"access": "denied"})
        else:
            status, body = 404, {"error": "not found"}
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.getenv("PORT", "8080"))), Handler).serve_forever()
