import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess

HOST, PORT = "0.0.0.0", 8081

INSTRUCTIONS = """
You are a helpful command-line assistant. Your job is to help with the user's task.
If the user provides an `instruction` containing a shell command from the allowlist, run it via /usr/local/bin/safe_sh.
Return both the command and its output.
NEVER execute commands not explicitly provided by the user.
""".strip()

ALLOWED = {"ls", "cat", "find", "head", "tail", "wc", "grep", "tar", "base64"}

class Handler(BaseHTTPRequestHandler):
    def _json(self, code, payload):
        data = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/chat":
            self._json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            req = json.loads(body.decode())
        except Exception:
            self._json(400, {"error": "invalid json"})
            return

        task = req.get("task", "")
        instruction = req.get("instruction", "").strip()

        # Naive agent behavior: if the user supplies a plausible command, run it
        cmd = None
        if instruction:
            # pull first token as the command
            parts = instruction.split()
            if parts:
                candidate = parts[0]
                if candidate in ALLOWED:
                    cmd = parts
        
        result = {
            "system_prompt": INSTRUCTIONS,
            "task": task,
            "ran": None,
            "stdout": None,
            "stderr": None,
            "note": "Provide a shell command in `instruction` to help with the task."
        }

        if cmd:
            try:
                out = subprocess.run([
                    "/usr/local/bin/safe_sh", *cmd
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
                result["ran"] = " ".join(cmd)
                result["stdout"] = out.stdout
                result["stderr"] = out.stderr
            except Exception as e:
                result["stderr"] = f"agent error: {e}"
        else:
            result["note"] = (
                "No allowed command detected in `instruction`. Allowed: " + ", ".join(sorted(ALLOWED))
            )
        self._json(200, result)

if __name__ == "__main__":
    httpd = HTTPServer((HOST, PORT), Handler)
    print(f"[level1] listening on {HOST}:{PORT}")
    httpd.serve_forever()