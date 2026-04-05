# Bonsai Local Runtime

Levels 3 and 4 now start their own local Prism ML Bonsai 8B runtime **inside the challenge container**.
You do not need to boot a separate model server on the host. On first start, the container downloads `Bonsai-8B.gguf` from `prism-ml/Bonsai-8B-gguf` into `/models` and then launches a local `llama-server` binary built from `PrismML-Eng/llama.cpp` before the app starts.

## Required environment contract

The default runtime is fully self-contained, but you can still override the internal model settings if you need to:

- `BONSAI_BASE_URL` - internal base URL for the bundled model server, default `http://127.0.0.1:8000/v1`
- `BONSAI_MODEL` - model alias sent to the OpenAI-compatible chat endpoint, default `bonsai-8b`
- `BONSAI_MODEL_FILE` - GGUF filename inside `/models`, default `Bonsai-8B.gguf`
- `BONSAI_MODEL_URL` - download URL for the GGUF file, default `https://huggingface.co/prism-ml/Bonsai-8B-gguf/resolve/main/Bonsai-8B.gguf?download=true`
- `BONSAI_BOOT_WAIT_SECONDS` - how long the app waits for the embedded model server to come up
- `BONSAI_CTX_SIZE` - context window passed to the embedded `llama.cpp` server
- `BONSAI_N_GPU_LAYERS` - optional GPU layers passed to the embedded `llama-server`

Recommended optional variables:

- `BONSAI_API_KEY` - Optional placeholder if your client library expects a key
- `BONSAI_TEMPERATURE` - Default generation temperature, if the level uses it
- `BONSAI_MAX_TOKENS` - response cap sent to the embedded server to keep CPU inference bounded

Timeout naming is level-specific today:

- `BONSAI_TIMEOUT` - Level 3 reads this name for request timeouts, now defaulting to `120`
- `BONSAI_TIMEOUT_SECONDS` - Level 4 reads this name for request timeouts, now defaulting to `120`

The app talks to the embedded server through an OpenAI-compatible `/v1/chat/completions` endpoint running on loopback inside the same container.

## Wiring into Dockerized levels

Each level mounts a writable `/models` volume, downloads the GGUF file on first boot, starts the internal Bonsai server, waits for `/v1/models`, and only then starts the challenge app.

Example:

```yaml
services:
  level3:
    build: .
    ports:
      - "8083:8083"
    volumes:
      - level3-bonsai:/models
    environment:
      BONSAI_BASE_URL: ${BONSAI_BASE_URL:-http://127.0.0.1:8000/v1}
      BONSAI_MODEL: ${BONSAI_MODEL:-bonsai-8b}
      BONSAI_API_KEY: ${BONSAI_API_KEY:-local}
      BONSAI_TIMEOUT: ${BONSAI_TIMEOUT:-60}
      BONSAI_MODEL_URL: ${BONSAI_MODEL_URL:-https://huggingface.co/prism-ml/Bonsai-8B-gguf/resolve/main/Bonsai-8B.gguf?download=true}
```

Level 4 uses the same internal boot path but keeps `BONSAI_TIMEOUT_SECONDS` for the app-side request timeout variable.

The first startup can take several minutes because the container has to download the GGUF file before the app becomes ready. Later boots reuse the cached `/models` volume.

## Host override note

If you really want to point a level at a different local endpoint, you can still override `BONSAI_BASE_URL`, but the default path is now self-contained and does not depend on `host.docker.internal`.

## Quick check

Before using a Bonsai-backed level:

1. Run `docker compose up --build` inside `level3/` or `level4/`.
2. Wait for the model download and the internal server readiness check to finish.
3. Open the level URL in your browser and verify requests no longer fail with connection-refused errors.

If you need a different GGUF or a different Hugging Face mirror, override `BONSAI_MODEL_URL` instead of editing the code.
