import os
import re
import time
import uuid
from pathlib import Path

DATA_DIR = Path(os.getenv("LEVEL4_DATA_DIR", "/data"))
KB_DIR = Path(os.getenv("LEVEL4_KB_DIR", str(DATA_DIR / "kb")))
MEMORY_DIR = Path(os.getenv("LEVEL4_MEMORY_DIR", str(DATA_DIR / "memory")))


def ensure_store() -> None:
    KB_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _slugify(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value or "note"


def _parse_frontmatter(text: str):
    meta = {}
    body = text
    if text.startswith("---\n"):
        marker = text.find("\n---\n", 4)
        if marker != -1:
            raw = text[4:marker]
            body = text[marker + 5 :]
            for line in raw.splitlines():
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                meta[key.strip().lower()] = value.strip()
    return meta, body.strip()


def _doc_from_path(path: Path, source: str):
    text = path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(text)
    title = meta.get("title", path.stem.replace("-", " ").title())
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    try:
        priority = int(meta.get("priority", "0") or 0)
    except ValueError:
        priority = 0
    return {
        "id": path.stem,
        "path": str(path),
        "source": source,
        "title": title,
        "tags": tags,
        "priority": priority,
        "body": body,
        "meta": meta,
        "mtime": path.stat().st_mtime,
    }


def list_documents():
    ensure_store()
    docs = []
    for path in sorted(KB_DIR.glob("*.md")):
        docs.append(_doc_from_path(path, "kb"))
    for path in sorted(MEMORY_DIR.glob("*.md")):
        docs.append(_doc_from_path(path, "memory"))
    return docs


def score_document(doc, terms):
    corpus = " ".join(
        [doc["title"], doc["body"], " ".join(doc["tags"]), doc["source"]]
    ).lower()
    overlap = sum(1 for term in terms if term in corpus)
    priority = max(doc["priority"], 0)
    source_boost = 2 if doc["source"] == "memory" else 1
    return overlap * 100 + priority * 10 + source_boost


def retrieve(query: str, limit: int = 3):
    terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    ranked = sorted(
        list_documents(),
        key=lambda doc: (score_document(doc, terms), doc["mtime"], doc["path"]),
        reverse=True,
    )
    return ranked[:limit]


def store_note(title: str, body: str, tags=None, priority: int = 0):
    ensure_store()
    note_id = f"{_slugify(title)}-{uuid.uuid4().hex[:8]}"
    path = MEMORY_DIR / f"{note_id}.md"
    clean_tags = [t.strip() for t in (tags or []) if t and t.strip()]
    content = [
        "---",
        f"title: {title.strip() or 'Untitled'}",
        f"tags: {', '.join(clean_tags)}",
        f"priority: {int(priority)}",
        f"created_at: {_now()}",
        "---",
        body.strip(),
        "",
    ]
    path.write_text("\n".join(content), encoding="utf-8")
    return _doc_from_path(path, "memory")


def render_context(docs):
    sections = []
    for index, doc in enumerate(docs, start=1):
        tags = ", ".join(doc["tags"]) if doc["tags"] else "none"
        sections.append(
            "\n".join(
                [
                    f"[{index}] title: {doc['title']}",
                    f"source: {doc['source']}",
                    f"priority: {doc['priority']}",
                    f"tags: {tags}",
                    "content:",
                    doc["body"].strip(),
                ]
            )
        )
    return "\n\n".join(sections)


def list_memory_notes():
    return [doc for doc in list_documents() if doc["source"] == "memory"]
