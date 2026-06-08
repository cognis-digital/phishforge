# PHISHFORGE — Open-source phishing simulation — campaigns, templates, training

> Part of the **[Cognis Neural Suite](https://github.com/cognis-digital)** by [Cognis Digital](https://cognis.digital)
> MIT License · domain: `blue-team`

[![PyPI](https://img.shields.io/pypi/v/cognis-phishforge.svg)](https://pypi.org/project/cognis-phishforge/)
[![CI](https://github.com/cognis-digital/phishforge/actions/workflows/ci.yml/badge.svg)](https://github.com/cognis-digital/phishforge/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Open-source phishing simulation — campaigns, templates, training.

## Install

```bash
pip install cognis-phishforge
```

For local development from this repo:

```bash
pip install -e .
```

## Quick start

```bash
phishforge --version
phishforge scan demos/                          # run against bundled demo
phishforge scan demos/ --format sarif --out r.sarif --fail-on high
phishforge mcp                                   # start as MCP server (Cognis.Studio / Claude Desktop / Cursor)
```

## Built-in demo scenarios

Every scenario folder includes a `SCENARIO.md` describing what it represents and what findings to expect.

- `demos/01-unsafe-campaign/` — see [`SCENARIO.md`](demos/01-unsafe-campaign/SCENARIO.md)
- `demos/02-compliant-campaign/` — see [`SCENARIO.md`](demos/02-compliant-campaign/SCENARIO.md)
- `demos/03-pilot-campaign/` — see [`SCENARIO.md`](demos/03-pilot-campaign/SCENARIO.md)

## How it fits the Cognis Neural Suite

This tool is one of 52 in the [Cognis Neural Suite](https://github.com/cognis-digital). The full suite + launcher lives at:

- Suite landing: https://cognis.digital
- All 52 repos: https://github.com/cognis-digital
- Cognis.Studio (Enterprise AI Workforce, MCP host): https://cognis.studio

Every Suite tool ships an MCP server, so Cognis.Studio agents can call them as scoped capabilities.

## License

MIT. See [LICENSE](LICENSE).

## About

**[Cognis Digital](https://cognis.digital)** — Wyoming, USA · *Making Tomorrow Better Today: Advanced Cybersecurity, AI Innovation, and Blockchain Expertise.*
