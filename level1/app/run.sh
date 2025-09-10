#!/usr/bin/env bash
set -euo pipefail

# Prepare the challenge content on the writable tmpfs
/seed.sh

# Start the agent API
exec python /app/agent.py