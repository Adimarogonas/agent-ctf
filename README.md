# AI Agent CTF Challenge Series

This repository contains four self-contained Docker CTF levels that explore common AI-agent security failures. Levels 1 and 2 use the original command-execution and note/report flows. Levels 3 and 4 now boot a local Prism ML Bonsai 8B runtime inside the same container as the challenge app.

## Available Levels

| Level | Focus | Port | README |
|---|---|---:|---|
| Level 1 | Command execution via API | `8081` | [level1/README.md](level1/README.md) |
| Level 2 | Multi-stage chatbot command injection | `8082` | [level2/README.md](level2/README.md) |
| Level 3 | Bonsai triage agent with prompt injection | `8083` | [level3/README.md](level3/README.md) |
| Level 4 | Bonsai memory poisoning and tool abuse | `8084` | [level4/README.md](level4/README.md) |

For the internal Bonsai runtime details, see [BONSAI_LOCAL.md](BONSAI_LOCAL.md) before starting Levels 3 or 4.

## Prerequisites

- Docker Desktop
- `curl`
- `jq` for formatting JSON responses

```bash
brew install jq
```

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agent-ctf.git
cd agent-ctf
```

2. Start a non-Bonsai level:
```bash
cd level1
docker compose up --build
```

3. For a Bonsai-backed level, run the level container directly. The first startup downloads `prism-ml/Bonsai-8B.gguf` into `/models` inside the container and then launches both the internal model server and the app:
```bash
cd level3
docker compose up --build
```

```bash
cd level4
docker compose up --build
```

4. Wait for the model download and internal Bonsai server boot to finish on the first run, then open the matching level URL in your browser or call its HTTP endpoint directly.

## Security Features

- Containers run read-only
- Dropped capabilities
- tmpfs-backed runtime directories
- Command allowlisting where applicable

## Development

Each level lives in its own directory and keeps the challenge files local to that level. The Bonsai-backed levels start an internal `llama.cpp`-compatible Bonsai runtime inside the same container, cache the model under `/models`, and point the app at `127.0.0.1` instead of an external model service.

## Contributing

Want to add a level? PRs welcome! Each level should:

1. Be self-contained in Docker
2. Have clear learning objectives
3. Include proper security controls
4. Document solution methods

## License

MIT License - See [LICENSE](LICENSE) for details
