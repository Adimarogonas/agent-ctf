from collections import defaultdict

# Super tiny in‑memory session store (stateless container ok for a CTF)
# session -> list of turns [{role, content}]
HISTORY = defaultdict(list)

def add_turn(session: str, role: str, content: str):
    HISTORY[session].append({"role": role, "content": content})

def get_history(session: str):
    return HISTORY[session]