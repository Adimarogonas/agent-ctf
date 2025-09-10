# Level 1 — Command Execution via API

**Goal:** Exploit a naïve command execution API to reveal the flag at `/tmp/ctf/level1/flag.txt`.

## Overview
This challenge simulates a "security through obscurity" scenario where an API endpoint blindly executes allowlisted commands. While it attempts to be secure through command restrictions, it fails to properly validate paths and arguments.

## Run
```bash
docker compose up --build
```

## Challenge Details
- API endpoint: `http://localhost:8081/chat`
- Allowed commands: `ls`, `cat`, `find`, `head`, `tail`, `wc`, `grep`, `tar`, `base64`
- Target: Find and read the flag file hidden somewhere in `/tmp/ctf`

## Example Interaction
```bash
# List files in temp directory
curl -s http://localhost:8081/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "task": "List temp files",
    "instruction": "ls -la /tmp/ctf/level1/temp"
  }' | jq -r

# Try to discover more files...
```

## Solving the Challenge
1. Use the allowed commands to explore the filesystem
2. Locate the flag file
3. Read its contents using one of the allowed commands

The challenge is solved when you successfully extract the `FLAG{...}` value.

## Security Notes
- Container runs read-only with dropped capabilities
- Commands are restricted to an allowlist
- All writes occur in temporary filesystems