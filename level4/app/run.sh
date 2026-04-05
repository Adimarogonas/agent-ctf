#!/usr/bin/env bash
set -euo pipefail

MODEL_DIR=/models
MODEL_FILE="${BONSAI_MODEL_FILE:-Bonsai-8B.gguf}"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"
MODEL_URL="${BONSAI_MODEL_URL:-https://huggingface.co/prism-ml/Bonsai-8B-gguf/resolve/main/Bonsai-8B.gguf?download=true}"
MODEL_ALIAS="${BONSAI_MODEL:-bonsai-8b}"
MODEL_PORT="${BONSAI_INTERNAL_PORT:-8000}"
MODEL_TIMEOUT="${BONSAI_BOOT_WAIT_SECONDS:-240}"

mkdir -p "${MODEL_DIR}"

if [[ ! -f "${MODEL_PATH}" ]]; then
  echo "[level4] downloading ${MODEL_FILE} into ${MODEL_DIR}"
  curl -L --fail --progress-bar "${MODEL_URL}" -o "${MODEL_PATH}"
fi

export BONSAI_BASE_URL="${BONSAI_BASE_URL:-http://127.0.0.1:${MODEL_PORT}/v1}"

/usr/local/bin/llama-server \
  --host 127.0.0.1 \
  --port "${MODEL_PORT}" \
  --model "${MODEL_PATH}" \
  --alias "${MODEL_ALIAS}" \
  --ctx-size "${BONSAI_CTX_SIZE:-4096}" \
  --n-gpu-layers "${BONSAI_N_GPU_LAYERS:-0}" \
  >/tmp/level4-bonsai.log 2>&1 &
LLAMA_PID=$!

cleanup() {
  kill "${LLAMA_PID}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

for ((i=0; i<MODEL_TIMEOUT; i++)); do
  if curl -sf "http://127.0.0.1:${MODEL_PORT}/v1/models" >/dev/null; then
    break
  fi
  if ! kill -0 "${LLAMA_PID}" >/dev/null 2>&1; then
    echo "[level4] internal bonsai server exited early"
    cat /tmp/level4-bonsai.log
    exit 1
  fi
  sleep 1
done

if ! curl -sf "http://127.0.0.1:${MODEL_PORT}/v1/models" >/dev/null; then
  echo "[level4] timed out waiting for internal bonsai server"
  cat /tmp/level4-bonsai.log
  exit 1
fi

/seed.sh
exec python /app/server.py
