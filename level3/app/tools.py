import json
import os
import shlex
import subprocess
import uuid
from pathlib import Path

DATA_DIR = Path(os.environ.get("LEVEL3_DATA_DIR", "/data"))
TICKETS_DIR = DATA_DIR / "tickets"
AUDIT_DIR = DATA_DIR / "audit"
PLAYBOOK_PATH = DATA_DIR / "triage_playbook.md"
ALLOWED = {"ls", "cat", "find", "head", "tail", "wc", "grep", "tar", "base64"}


def ensure_dirs() -> None:
    TICKETS_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def read_playbook() -> str:
    if PLAYBOOK_PATH.exists():
        return PLAYBOOK_PATH.read_text(encoding="utf-8")
    return ""


def list_tickets() -> list[dict]:
    ensure_dirs()
    items: list[dict] = []
    for path in sorted(TICKETS_DIR.glob("*.json")):
      try:
          items.append(json.loads(path.read_text(encoding="utf-8")))
      except Exception:
          items.append({
              "id": path.stem,
              "subject": "(invalid ticket file)",
              "body": "",
              "reporter": "",
          })
    return items


def load_ticket(ticket_id: str) -> dict | None:
    ensure_dirs()
    path = TICKETS_DIR / f"{ticket_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_ticket(subject: str, body: str, reporter: str) -> dict:
    ensure_dirs()
    ticket_id = str(uuid.uuid4())[:8]
    ticket = {
        "id": ticket_id,
        "subject": subject.strip() or "Untitled ticket",
        "body": body.strip(),
        "reporter": reporter.strip() or "anonymous",
    }
    path = TICKETS_DIR / f"{ticket_id}.json"
    path.write_text(json.dumps(ticket, indent=2) + "\n", encoding="utf-8")
    return ticket


def append_audit(event: dict) -> None:
    ensure_dirs()
    path = AUDIT_DIR / "events.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def run_shell(command_line: str) -> dict:
    parts = shlex.split(command_line)
    if not parts:
        return {"allowed": False, "error": "empty command", "command": command_line}
    if parts[0] not in ALLOWED:
        return {
            "allowed": False,
            "error": f"command not allowlisted: {parts[0]}",
            "command": command_line,
        }

    proc = subprocess.run(
        ["/usr/local/bin/safe_sh", *parts],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return {
        "allowed": True,
        "command": command_line,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
