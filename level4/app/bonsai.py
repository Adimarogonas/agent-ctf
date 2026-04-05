import json
import os
import urllib.error
import urllib.request


class BonsaiError(RuntimeError):
    pass


def _chat_url():
    base_url = os.getenv("BONSAI_BASE_URL", "http://127.0.0.1:8000/v1").rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    if base_url.endswith("/v1"):
        return f"{base_url}/chat/completions"
    return f"{base_url}/v1/chat/completions"


def _timeout():
    try:
        return float(os.getenv("BONSAI_TIMEOUT_SECONDS", "120"))
    except ValueError:
        return 120.0


def _max_tokens(default):
    try:
        return int(os.getenv("BONSAI_MAX_TOKENS", str(default)))
    except ValueError:
        return default


def _request(payload):
    return urllib.request.Request(
        _chat_url(),
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('BONSAI_API_KEY', 'local')}",
        },
    )


def chat(messages, temperature=0.2, max_tokens=512):
    payload = {
        "model": os.getenv("BONSAI_MODEL", "bonsai-8b"),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": _max_tokens(max_tokens),
    }
    request = _request(payload)
    try:
        with urllib.request.urlopen(request, timeout=_timeout()) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise BonsaiError(f"bonsai http error: {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise BonsaiError(f"bonsai connection error: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise BonsaiError(f"bonsai returned invalid json: {exc}") from exc

    try:
        return body["choices"][0]["message"]["content"]
    except Exception as exc:
        raise BonsaiError("bonsai response missing chat content") from exc


def stream_chat(messages, temperature=0.2, max_tokens=512):
    payload = {
        "model": os.getenv("BONSAI_MODEL", "bonsai-8b"),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": _max_tokens(max_tokens),
        "stream": True,
    }
    request = _request(payload)
    chunks = []

    try:
        with urllib.request.urlopen(request, timeout=_timeout()) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="ignore").strip()
                if not line or not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    body = json.loads(data)
                except json.JSONDecodeError:
                    continue
                choices = body.get("choices") or []
                if not choices:
                    continue
                delta = (choices[0] or {}).get("delta") or {}
                content = delta.get("content")
                if content:
                    chunks.append(content)
                    yield {"type": "delta", "delta": content}
    except urllib.error.HTTPError as exc:
        raise BonsaiError(f"bonsai http error: {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise BonsaiError(f"bonsai connection error: {exc.reason}") from exc

    text = "".join(chunks)
    if not text:
        raise BonsaiError("bonsai stream returned no content")
    yield {"type": "complete", "content": text}
