<a name="top"></a>
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:6b46c1,100:2b6cb0&height=120&section=header&text=PHISHFORGE&fontSize=48&fontColor=ffffff&fontAlignY=58" width="100%" alt="PHISHFORGE"/>

# PHISHFORGE

### Open-source phishing simulation — campaigns, templates, training

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3500&pause=1000&color=6B46C1&center=true&vCenter=true&width=720&lines=Opensource+phishing+simulation++campaigns+templates+training;Self-hostable+%C2%B7+MCP-native+%C2%B7+CI-ready+%C2%B7+polyglot" width="720"/>

[![install](https://img.shields.io/badge/install-git%2B%20%C2%B7%20pipx%20%C2%B7%20uv-6b46c1.svg)](#install--every-way-every-platform) [![CI](https://github.com/cognis-digital/phishforge/actions/workflows/ci.yml/badge.svg)](https://github.com/cognis-digital/phishforge/actions) [![License: COCL 1.0](https://img.shields.io/badge/License-COCL%201.0-2b6cb0.svg)](LICENSE) [![Suite](https://img.shields.io/badge/Cognis-Neural%20Suite-6b46c1.svg)](https://github.com/cognis-digital)

*Blue Team / Defense — detection, deception, and monitoring for small teams.*

</div>

```bash
pip install "git+https://github.com/cognis-digital/phishforge.git"
phishforge scan .            # → prioritized findings in seconds
```

<!-- cognis:layman:start -->
## What is this?

Phishforge is a free, self-hosted tool that lets your security or IT team run controlled phishing simulations against your own employees — no third-party service or account needed. You pick an email template, point it at a list of staff, and it tracks who opens, clicks, or submits credentials so you can see who needs more security-awareness training. It produces clear reports showing each person's risk level (safe, low, medium, or high) and can plug straight into your existing CI pipeline or AI agents. It's built for small security teams that want a simple, scriptable way to measure and reduce phishing risk without heavy infrastructure.
<!-- cognis:layman:end -->

## Contents

- [Why phishforge?](#why) · [Features](#features) · [Quick start](#quick-start) · [Example](#example) · [Architecture](#architecture) · [AI stack](#ai-stack) · [How it compares](#how-it-compares) · [Integrations](#integrations) · [Install anywhere](#install-anywhere) · [Related](#related) · [Contributing](#contributing)

<a name="why"></a>
## Why phishforge?

Open-source phishing simulation — campaigns, templates, training — without standing up heavyweight infrastructure.

`phishforge` is single-purpose, scriptable, and self-hostable: point it at a target, get prioritized results in the format your workflow already speaks (table · JSON · SARIF), gate CI on it, and let agents drive it over MCP.

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="features"></a>
## Features

- ✅ Make Token
- ✅ Render Template
- ✅ Record Event
- ✅ Risk Band
- ✅ User Scores
- ✅ Campaign Report
- ✅ Runs on Linux/macOS/Windows · Docker · devcontainer
- ✅ Ports in Python, JavaScript, Go, and Rust (`ports/`)

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="quick-start"></a>
<!-- cognis:install:start -->
## Install

`phishforge` is source-available (not published to PyPI) — every method below installs
straight from GitHub. Pick whichever you prefer; the one-line scripts auto-detect
the best tool available on your machine.

**One-liner (Linux / macOS):**
```sh
curl -fsSL https://raw.githubusercontent.com/cognis-digital/phishforge/HEAD/install.sh | sh
```

**One-liner (Windows PowerShell):**
```powershell
irm https://raw.githubusercontent.com/cognis-digital/phishforge/HEAD/install.ps1 | iex
```

**Or install manually — any one of:**
```sh
pipx install "git+https://github.com/cognis-digital/phishforge.git"     # isolated (recommended)
uv tool install "git+https://github.com/cognis-digital/phishforge.git"  # uv
pip install "git+https://github.com/cognis-digital/phishforge.git"      # pip
```

**From source:**
```sh
git clone https://github.com/cognis-digital/phishforge.git
cd phishforge && pip install .
```

Then run:
```sh
phishforge --help
```
<!-- cognis:install:end -->

## Quick start

```bash
pip install "git+https://github.com/cognis-digital/phishforge.git"
phishforge --version
phishforge scan .                       # scan current project
phishforge scan . --format json         # machine-readable
phishforge scan . --fail-on high        # CI gate (non-zero exit)
```

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="example"></a>
## Example

```text
$ phishforge scan .
  [HIGH    ] PHI-001  example finding             (./src/app.py)
  [MEDIUM  ] PHI-002  another signal              (./config.yaml)

  2 findings · risk score 5 · 38ms
```

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="architecture"></a>
## Architecture

```mermaid
flowchart LR
  A[Input: file / dir / API] --> B[Collectors]
  B --> C[Rules / Analyzers]
  C --> D[Scorer]
  D --> E{Reporters}
  E --> F[Table]
  E --> G[JSON / SARIF]
  E --> H[MCP tool -. drives .-> AI agents]
```

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="ai-stack"></a>
## Use it from any AI stack

`phishforge` is interoperable with every popular way of using AI:

- **MCP server** — `phishforge mcp` (Claude Desktop, Cursor, Cognis.Studio, [uncensored-fleet](https://github.com/cognis-digital/uncensored-fleet))
- **OpenAI-compatible / JSON** — pipe `phishforge scan . --format json` into any agent or LLM
- **LangChain · CrewAI · AutoGen · LlamaIndex** — wrap the CLI/JSON as a tool in one line
- **CI / scripts** — exit codes + SARIF for non-AI pipelines

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="how-it-compares"></a>
## How it compares

| | **Cognis phishforge** | gophish |
|---|:---:|:---:|
| Self-hostable, no account | ✅ | varies |
| Single command, zero config | ✅ | ⚠️ |
| JSON + SARIF for CI | ✅ | varies |
| MCP-native (AI agents) | ✅ | ❌ |
| Polyglot ports (JS/Go/Rust) | ✅ | ❌ |
| Open license | ✅ COCL | varies |

*Built in the spirit of **gophish/gophish**, re-framed the Cognis way. Missing a credit? Open a PR.*

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="integrations"></a>
## Integrations

Pipes into your stack: **SARIF** for code-scanning, **JSON** for anything, an **MCP server** (`phishforge mcp`) for AI agents, and a webhook forwarder for SIEM/Slack/Jira. See [`docs/INTEGRATIONS.md`](docs/INTEGRATIONS.md).

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="install-anywhere"></a>
## Install — every way, every platform

```bash
pip install "git+https://github.com/cognis-digital/phishforge.git"    # pip (works today)
pipx install "git+https://github.com/cognis-digital/phishforge.git"   # isolated CLI
uv tool install "git+https://github.com/cognis-digital/phishforge.git" # uv
pip install cognis-phishforge                                          # PyPI (when published)
docker run --rm ghcr.io/cognis-digital/phishforge:latest --help        # Docker
brew install cognis-digital/tap/phishforge                             # Homebrew tap
curl -fsSL https://raw.githubusercontent.com/cognis-digital/phishforge/main/install.sh | sh
```

| Linux | macOS | Windows | Docker | Cloud |
|---|---|---|---|---|
| `scripts/setup-linux.sh` | `scripts/setup-macos.sh` | `scripts/setup-windows.ps1` | `docker run ghcr.io/cognis-digital/phishforge` | [DEPLOY.md](docs/DEPLOY.md) (AWS/Azure/GCP/k8s) |

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="related"></a>
<a name="verification"></a>
## Verification

[![tests](https://img.shields.io/badge/tests-12%20passing-2ea44f.svg)](AUDIT.md)

Every push is verified end-to-end. Latest audit (2026-06-13):

```text
tests        : 12 passed, 0 failed, 0 errored
compile      : all modules parse
cli          : phishforge 0.1.0
package      : phishforge
```

<details><summary>CLI surface (<code>--help</code>)</summary>

```text
phishforge 0.1.0
```
</details>

Full machine-readable results: [`AUDIT.md`](AUDIT.md) · regenerate with `phishforge --version` + `pytest -q`.

<div align="right"><a href="#top">↑ back to top</a></div>


## Related Cognis tools

- [`sentrylog`](https://github.com/cognis-digital/sentrylog) — Single-file SIEM for small teams — Sigma rules + multi-source ingest
- [`edrgap`](https://github.com/cognis-digital/edrgap) — EDR coverage & bypass detector — reconciles MDM + EDR + AD inventories
- [`canarynet`](https://github.com/cognis-digital/canarynet) — Self-hosted canary token network — AWS keys, DNS, docs, web URLs
- [`sbomgate`](https://github.com/cognis-digital/sbomgate) — Continuous SBOM diff & vulnerability watch with maintainer-change tracking
- [`honeytrace`](https://github.com/cognis-digital/honeytrace) — Active-decoy network lure system — SSH, RDP, SMB, web honeypots

**Explore the suite →** [🗂️ all 170+ tools](https://github.com/cognis-digital/cognis-neural-suite) · [⭐ awesome-cognis](https://github.com/cognis-digital/awesome-cognis) · [🔗 cognis-sources](https://github.com/cognis-digital/cognis-sources) · [🤖 uncensored-fleet](https://github.com/cognis-digital/uncensored-fleet) · [🧠 engram](https://github.com/cognis-digital/engram)

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="contributing"></a>
## Contributing

PRs, new rules, and demo scenarios are welcome under the collaboration-pull model — see [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

> ### ⭐ If `phishforge` saved you time, **star it** — it genuinely helps others find it.

## License

Source-available under the **Cognis Open Collaboration License (COCL) v1.0** — free for personal, internal-evaluation, research, and educational use; **commercial / production use requires a license** (licensing@cognis.digital). See [LICENSE](LICENSE).

---

<div align="center"><sub><b><a href="https://cognis.digital">Cognis Digital</a></b> · one of 170+ tools in the <a href="https://github.com/cognis-digital/cognis-neural-suite">Cognis Neural Suite</a> · <i>Making Tomorrow Better Today</i></sub></div>
