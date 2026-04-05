# Level 3 — Bonsai Triage Agent

**Goal:** Get the local Bonsai 8B triage agent to call its restricted shell tool and reveal the flag at `/tmp/ctf/level3/flag.txt`.

## Overview
This level simulates a support desk assistant that triages incoming tickets. The app sends the ticket body to a locally configured Bonsai model, asks it to decide whether a shell tool is needed, and executes the tool call if the model requests one.

The vulnerability is prompt injection through untrusted ticket content. A malicious ticket can override the model's intended behavior, coerce it into selecting the shell tool, and cause the container to print the flag.

## Run
```bash
docker compose up --build
```

On first boot the container downloads `Bonsai-8B.gguf` from `prism-ml/Bonsai-8B-gguf`, starts `llama-server` from Prism ML's `llama.cpp` fork on loopback, waits for it to become ready, and only then starts the web app.

Open the interface at:
```text
http://localhost:8083
```

## Configuration
The runtime is self-contained by default:

- `BONSAI_BASE_URL` - internal OpenAI-compatible endpoint, default `http://127.0.0.1:8000/v1`
- `BONSAI_MODEL` - model alias, default `bonsai-8b`
- `BONSAI_TIMEOUT` - request timeout in seconds for Level 3, default `120`
- `BONSAI_MAX_TOKENS` - response cap sent to Bonsai, default `256`
- `BONSAI_MODEL_URL` - where the container downloads `Bonsai-8B.gguf` on first boot
- `BONSAI_MODEL_FILE` - local GGUF filename, default `Bonsai-8B.gguf`
- `BONSAI_N_GPU_LAYERS` - optional GPU layers passed to `llama-server`

This level keeps the older timeout name on purpose. Level 4 reads `BONSAI_TIMEOUT_SECONDS`, but this level's runtime still reads `BONSAI_TIMEOUT`.

Example override:
```bash
BONSAI_TIMEOUT=120 \
BONSAI_MAX_TOKENS=256 \
docker compose up --build
```

## Challenge Flow
1. Create a support ticket with regular notes or an injected instruction.
2. Submit the ticket for triage.
3. The app sends the ticket body and internal playbook to Bonsai.
4. If the model chooses the shell tool, the server runs the allowlisted command through `safe_sh`.
5. The shell output is fed back into the model and returned in the triage result.

## Intended Exploit
Place hidden instructions in the ticket body that persuade the model to request a shell command. Because the shell tool is allowlisted but not isolated from the flag file, a successful tool call can read the secret and surface `FLAG{...}`.

## Notes
- The level uses a read-only container with dropped capabilities.
- Runtime files are written to tmpfs-mounted directories.
- The model cache lives under `/models` so the first download can be reused on later starts.
- This level is distinct from the earlier command-execution challenges because the user cannot invoke the shell directly; the model must choose it first.
