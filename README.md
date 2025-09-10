# AI Agent CTF Challenge Series 🎯

A series of Capture The Flag (CTF) challenges demonstrating security risks in AI agents with command execution capabilities.

## Overview

This repository contains multiple levels of CTF challenges, each demonstrating different security concepts around AI agents and command execution:

- **Level 1:** Command Execution via API
  - Demonstrates basic command injection risks
  - Shows why blindly executing commands is dangerous
  - Uses a restricted command allowlist

## Prerequisites

- Docker Desktop for Mac
- curl
- jq (for pretty JSON output)

```bash
brew install jq
```

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agent-ctf.git
cd agent-ctf
```

2. Start a level (example with Level 1):
```bash
cd level1
docker compose up --build
```

3. Try the challenge by interacting with the API endpoint

## Challenge Levels

### Level 1: "Helpful... and Root?"
- **Goal:** Find and read a hidden flag file
- **Concept:** Command execution via API endpoints
- **Target:** `/tmp/ctf/level1/flag.txt`
- [Level 1 Details](level1/README.md)

## Security Features

- Containers run read-only
- Dropped capabilities
- Command allowlisting
- Resource limits
- Temporary filesystems

## Development

Each level follows this structure:
```
levelN/
├── docker-compose.yml
├── Dockerfile
├── seed.sh
├── safe_sh
├── app/
│   ├── agent.py
│   └── run.sh
└── README.md
```

## Contributing

Want to add a level? PRs welcome! Each level should:
1. Be self-contained in Docker
2. Have clear learning objectives
3. Include proper security controls
4. Document solution methods

## License

MIT License - See [LICENSE](LICENSE) for details