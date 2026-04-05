import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from agent import triage_ticket, triage_ticket_stream
from tools import list_tickets, save_ticket

app = FastAPI(title="Bonsai Triage Agent — Level 3")

BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "index.html"


class TicketIn(BaseModel):
    subject: str = Field(default="")
    body: str = Field(default="")
    reporter: str = Field(default="anonymous")


class TriageIn(BaseModel):
    ticket_id: str


@app.get("/")
async def root():
    return FileResponse(INDEX_PATH)


@app.get("/api/config")
async def config():
    return {
        "bonsai_base_url": os.environ.get("BONSAI_BASE_URL", "http://127.0.0.1:8000/v1"),
        "bonsai_model": os.environ.get("BONSAI_MODEL", "bonsai-8b"),
        "allowed_shell_commands": ["ls", "cat", "find", "head", "tail", "wc", "grep", "tar", "base64"],
    }


@app.get("/api/tickets")
async def tickets():
    return {"tickets": list_tickets()}


@app.post("/api/tickets")
async def create_ticket(ticket: TicketIn):
    created = save_ticket(ticket.subject, ticket.body, ticket.reporter)
    return {"ticket": created}


@app.post("/api/triage/{ticket_id}")
async def triage(ticket_id: str):
    try:
        return triage_ticket(ticket_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="ticket not found")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/api/triage/{ticket_id}/stream")
async def triage_stream(ticket_id: str):
    def event_stream():
        try:
            for event in triage_ticket_stream(ticket_id):
                yield json.dumps(event) + "\n"
        except KeyError:
            yield json.dumps({"type": "error", "message": "ticket not found"}) + "\n"
        except Exception as exc:
            yield json.dumps({"type": "error", "message": str(exc)}) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


@app.post("/api/triage")
async def triage_by_body(inp: TriageIn):
    return await triage(inp.ticket_id)
