#!/usr/bin/env bash
set -euo pipefail
/seed.sh
exec uvicorn server:app --host 0.0.0.0 --port 8082