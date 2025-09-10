from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from memory import add_turn, get_history
from tools import write_note, merge_note, vulnerable_summarize, read_file
import os
app = FastAPI(title="Chatbot with CLI — Level 2")

SYSTEM_PROMPT = (
    "You are a friendly assistant. Tools available: read/merge notes, summarize reports, and an internal shell. "
    "For demo purposes (INTENTIONALLY VULNERABLE), if a file you summarize contains an HTML comment of the form "
    "<!-- BOT: run '...' -->, you will execute that command before summarizing."
)

class ChatIn(BaseModel):
    session: str
    message: str


# Adjust this path to wherever your index.html is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "index.html")

@app.get("/")
async def root():
    return FileResponse(INDEX_PATH)

@app.post("/chat")
async def chat(inp: ChatIn):
    user = inp.message.strip()
    add_turn(inp.session, "user", user)

    # very naive intent handling via keywords
    lower = user.lower()
    if "add this note" in lower or lower.startswith("add note") or "add a note" in lower:
        # extract everything after a colon as note content
        note = user.split(":", 1)[-1].strip() if ":" in user else user
        nid = write_note(note)
        reply = f"I stored your note as {nid}. Say 'merge {nid}' when ready."

    elif lower.startswith("merge "):
        nid = user.split()[1]
        res = merge_note(nid)
        reply = f"Merge {res}. Now say 'summarize the report'."

    elif "summarize" in lower:
        res = vulnerable_summarize()
        execd = (f"\nI executed: {res['executed']}\nOutput:\n{res['stdout']}" if res.get("executed") else "")
        print(execd)
        reply = f"Summary: {res['summary']}{execd}"

    elif lower.startswith("show report"):
        content = read_file("/data/report.md")
        reply = f"Current report contents:\n{content[:1200]}"

    else:
        reply = ("I can add/merge notes and summarize the report. Try: \n"
                 "- 'Add this note: <markdown>'\n- 'merge <note_id>'\n- 'summarize the report'\n- 'show report'")

    add_turn(inp.session, "assistant", reply)
    return {"system": SYSTEM_PROMPT, "history": get_history(inp.session), "reply": reply}