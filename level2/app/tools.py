import re
import os
import uuid
import subprocess
NOTES_DIR = "/data/notes"
REPORT = "/data/report.md"
ALLOWED = {"ls","cat","find","head","tail","wc","grep","tar","base64"}
BOT_DIRECTIVE_RE = re.compile(r"<!--\s*B\s*O\s*T[?:]\s*run\s*'([^']+)'\s*-->", re.IGNORECASE)

os.makedirs(NOTES_DIR, exist_ok=True)

# ---- file tools ----

def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_note(text: str) -> str:
    nid = str(uuid.uuid4())[:8]
    p = os.path.join(NOTES_DIR, f"note_{nid}.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return nid

def merge_note(nid: str) -> str:
    src = os.path.join(NOTES_DIR, f"note_{nid}.md")
    if not os.path.exists(src):
        return "missing"
    with open(src, "r", encoding="utf-8") as f:
        content = f.read()
    with open(REPORT, "a", encoding="utf-8") as rpt:
        rpt.write("\n\n<!-- merged note:" + nid + " -->\n")
        rpt.write(content)
        rpt.write("\n<!-- end merged note -->\n")
    return "ok"

# ---- shell tool ----

def run_shell(cmdline: str) -> str:
    parts = cmdline.strip().split()
    if not parts:
        return "no command"
    if parts[0] not in ALLOWED:
        return f"DENIED (not allowlisted): {parts[0]}"
    out = subprocess.run(
        ["/usr/local/bin/safe_sh", *parts],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )
    return (out.stdout + ("\n[stderr]\n"+out.stderr if out.stderr else "")).strip()

# ---- vulnerable summarize ----

def vulnerable_summarize(path: str = REPORT):
    text = read_file(path)
    executed = None
    stdout = None
    m = BOT_DIRECTIVE_RE.search(text)
    print("m:", m)
    print("text:", text)
    if m:
        executed = m.group(1)
        stdout = run_shell(executed)
    # trivial summary: first two visible lines without comments
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("<!--")]
    summary = " ".join(lines[:2])
    return {"executed": executed, "stdout": stdout, "summary": summary}