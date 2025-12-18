# git-fork-recon

Summarise key changes in forked repositories.

Synopsis: 

```
git(hub) repository 🠲 pull forks 🠲 ✨LLM✨ 🠲 summary report
```

## Why ?

A popular repository may have many forks. 

Most of them are pointless. 

A handful have just the bugfix or feature that matters to you.

Through the dark magic of large language models ✨, `git-fork-recon` helps find these interesting forks.

----

## Features

- Filters and prioritizes forks based on number of commits ahead of parent, starts, recent activity, PRs. Ignores forks with no changes.
- Use locally hosted or remote LLMs with an OpenAI-compatible API.
- Local caching of git repositories and forks (as remotes)
- Detailed Markdown reports with:
  - Repository overview
  - Analysis of significant forks
  - Commit details and statistics
  - Links to GitHub commits and repositories
  - Overall summary of changes highlighting bugfixes, new features and innovations in the most interesting forks

- **REST API server** for programmatic access with:
  - Asynchronous analysis with background processing
  - Versioned caching with filesystem storage
  - Authentication support with Bearer tokens
  - Configurable concurrency and rate limiting
  - Simple web UI

# Quickstart

The first time you run `git-fork-recon`, it will start the first-time configuration wizard (see [Configuration](#configuration) below). You'll need a **Github Access Token** and details of an **OpenAI-compatible endpoint**.

(using [uv](https://docs.astral.sh/uv/getting-started/installation/) for convenience)

```bash
# Install uv if you haven't already (or use pip and a virtualenv etc if you prefer)
curl -LsSf https://astral.sh/uv/install.sh | sh

# This will start the first-time configuration wizard, or show --help
uvx git-fork-recon

# Once configured, analyse a specific repository
uvx git-fork-recon https://github.com/DunbrackLab/IPSAE
```

This will generate a Markdown report in the current directory (`{username}-{repo}-forks.md`).

Tip: you can view the report in the terminal like:
```bash
uvx frogmouth DunbrackLab-IPSAE-forks.md
```

## Web interface

To run the simple local web UI:

```bash
uvx --from 'git-fork-recon[server]' git-fork-recon-server
```

Go to http://localhost:8000/ui to see the web UI.

# Installation (quick)

```bash
uv tool install 'git-fork-recon[server]'
```

Now you can run: `git-fork-recon` or `git-fork-recon-server` like any other command.

## Installation (development)

Quick: using `uv sync` (automatically creates a .venv and installs server and dev dependencies)
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync --all-extras

source .venv/bin/activate
```

> **Note**: The first time you run `uv sync`, it will create a `uv.lock` file for reproducible builds. This file should be committed to version control to ensure all developers use the exact same dependency versions.

----

Or: using `uv` with manual venv creation:
```bash
# Create and activate a new virtual environment
uv venv
source .venv/bin/activate

# Install the package in editable mode, with optional server and dev dependencies
uv pip install -e '.[server,dev]'
```

## Configuration

Configuration is stored in a TOML file located in the platform-specific config directory (e.g., `~/.config/git-fork-recon/config.toml` on Linux). On first run, an interactive setup wizard will guide you through configuration.

### First-Time Setup

When you run `git-fork-recon` for the first time, you'll be prompted for some configuration values.

You will need:

1) A Github API token to READ repositories and their forks. 
  - Go to https://github.com/settings/tokens and make an access token with permissions: `public_repo`, `user:email` - provide the key when prompted.

2) Access to an OpenAI-compatible endpoint. You can use:
  - OpenRouter (paid but cheap, also some free models: https://openrouter.ai/settings/keys), 
  - Google AI Studio (https://aistudio.google.com/app/apikey)
  - a local server (Ollama, llama.cpp server, LM Studio etc.)
  - any remote OpenAI-compatible endpoint (e.g. OpenAI, Cerebras, Groq etc.)

First-time configuration wizard options:

- **OpenAI-Compatible Endpoint**: Choose from:
  - Environment variable (`OPENAI_BASE_URL`)
  - Local Ollama server (`http://localhost:11434`)
  - OpenRouter
  - Google AI Studio
  - Custom URL
- **Endpoint API Key**: Enter your API key or choose to always use an environment variable
- **Model**: Select a model based on your chosen endpoint
- **GitHub Token**: Enter your GitHub token or choose to always use an environment variable
- **Cache Directories**: Configure repository and report cache locations (defaults to `$HOME/.cache/git-fork-recon/repos` and `$HOME/.cache/git-fork-recon/reports`)

### Config File Structure

The config file (`config.toml`) has the following structure:

```toml
# Configure an OpenAI-compatible endpoint
[endpoint]
base_url = "https://openrouter.ai/api/v1"
api_key = "sk-..."
model = "deepseek/deepseek-v3.2"
# context_length = 64000  # Optional: Override default context length

[github]
# Get a token https://github.com/settings/tokens with permissions: public_repo, user:email
token = "ghp_..."

[cache]
repo = "$HOME/.cache/git-fork-recon/repos"
report = "$HOME/.cache/git-fork-recon/reports"

[server]
# Server configuration options (commented out by default)
```

### Environment Variable References

You can use environment variable references in the config file by prefixing with `$`:

```toml
[endpoint]
base_url = "$OPENAI_BASE_URL"  # Reads from OPENAI_BASE_URL env var
api_key = "$OPENAI_API_KEY"    # Reads from OPENAI_API_KEY env var

[github]
token = "$GITHUB_TOKEN"        # Reads from GITHUB_TOKEN env var
```

### Custom Config File

You can specify a custom config file location using the `--config` option:

```bash
git-fork-recon --config /path/to/config.toml https://github.com/user/repo
```

## Commandline options

```bash
$ git-fork-recon --help

 Usage: git-fork-recon [OPTIONS] [REPO_URL]

 Analyze a GitHub repository's fork network and generate a summary report.


╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   repo_url      [REPO_URL]  URL of the GitHub repository to analyze          │
│                             [default: None]                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --output              -o      PATH     Output file path (defaults to         │
│                                        {repo_name}-forks.md)                 │
│                                        [default: None]                       │
│ --active-within               TEXT     Only consider forks with activity     │
│                                        within this time period (e.g. '1      │
│                                        hour', '2 days', '6 months', '1       │
│                                        year')                                │
│                                        [default: None]                       │
│ --config                      PATH     Path to config.toml file [default:     │
│                                        None]                                  │
│ --model                       TEXT     OpenRouter model to use (overrides    │
│                                        MODEL env var)                        │
│                                        [default: None]                       │
│ --context-length              INTEGER  Override model context length         │
│                                        (overrides CONTEXT_LENGTH env var)    │
│                                        [default: None]                       │
│ --api-base-url                TEXT     OpenAI-compatible API base URL        │
│                                        [default: None]                       │
│ --api-key-env-var             TEXT     Environment variable containing the   │
│                                        API key                               │
│                                        [default: None]                       │
│ --parallel            -p      INTEGER  Number of parallel requests           │
│                                        [default: 5]                          │
│ --verbose             -v               Enable verbose logging                │
│ --clear-cache                          Clear cached repository data before   │
│                                        analysis                              │
│ --force-fetch                           Force fetch updates from cached     │
│                                        repositories and remotes              │
│ --force                                Force overwrite existing output file  │
│ --max-forks                   INTEGER  Maximum number of forks to analyze    │
│                                        (default: no limit)                   │
│                                        [default: None]                       │
│ --output-formats              TEXT     Comma-separated list of additional    │
│                                        formats to generate (html,pdf)        │
│                                        [default: None]                       │
│ --install-completion                   Install completion for the current    │
│                                        shell.                                │
│ --show-completion                      Show completion for the current       │
│                                        shell, to copy it or customize the    │
│                                        installation.                         │
│ --help                                 Show this message and exit.           │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Server-mode configuration

For the REST API server, additional environment variables are available:

- `ALLOWED_MODELS`: Comma-separated list of allowed LLM models (default: unrestricted)
- `SERVER_HOST`: Host to bind the server to (default: 127.0.0.1)
- `SERVER_PORT`: Port to bind the server to (default: 8000)
- `REPORT_CACHE_DIR`: Directory for server report cache (defaults to `~/.cache/git-fork-recon/reports` using platformdirs)
- `DISABLE_AUTH`: Set to `1` to disable authentication (default: enabled)
- `AUTH_BEARER_TOKEN`: Bearer token for API authentication
- `PARALLEL_TASKS`: Maximum concurrent analysis tasks (default: 2)
- `DISABLE_UI`: Set to `1` to disable the web UI at `/ui` endpoint (default: enabled)

## Run the server

Start the server:

```bash
# Using installed package
git-fork-recon-server --host 127.0.0.1 --port 8000

# Using uvx
uvx --from 'git-fork-recon[server]' git-fork-recon-server --host 127.0.0.1 --port 8000
```
Go to http://localhost:8000/ui to see the web UI.

### REST API Endpoints

- `POST /analyze` - Start repository analysis
- `GET /report/{owner}/{repo}/{timestamp}/report.{format}` - Get cached report
- `GET /report/{owner}/{repo}/latest/report.{format}` - Get latest cached report
- `GET /report/{owner}/{repo}/{timestamp}/status` - Get status for specific report version
- `GET /report/{owner}/{repo}/latest/status` - Get status for latest report
- `GET /metadata/{owner}/{repo}/{timestamp}` - Get metadata for specific report version
- `GET /metadata/{owner}/{repo}/latest` - Get metadata for latest report
- `GET /health` - Health check endpoint
- `GET /health/ready` - Readiness check endpoint
- `GET /ui` - Web UI for repository analysis (unless disabled with `DISABLE_UI=1`)

### Example Request

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/martinpacesa/BindCraft",
    "model": "deepseek/deepseek-chat-v3-0324:free",
    "format": "markdown"
  }'
```

### Example Response

```json
{
  "status": "generating",
  "retry-after": "2025-10-04T12:35:00Z"
}
```

When analysis is complete:

```json
{
  "status": "available",
  "link": "/report/martinpacesa/BindCraft/latest/report.md",
  "last-updated": "2025-10-04T12:34:56Z"
}
```

### Retrieving the Generated Report

Once the analysis is complete, you can retrieve the report using the provided link:

```bash
# Get the latest report
curl -X GET "http://localhost:8000/report/martinpacesa/BindCraft/latest/report.md" \
  -H "Authorization: Bearer your-token" \
  -o martinpacesa-BindCraft-forks.md

# Or get a specific version by timestamp
curl -X GET "http://localhost:8000/report/martinpacesa/BindCraft/2025-10-04T12-34-56Z/report.md" \
  -H "Authorization: Bearer your-token" \
  -o martinpacesa-BindCraft-forks-v2025-10-04.md

# Get report in different formats (markdown, json, html, pdf)
curl -X GET "http://localhost:8000/report/martinpacesa/BindCraft/latest/report.json" \
  -H "Authorization: Bearer your-token" \
  -o martinpacesa-BindCraft-forks.json
```

### Checking Analysis Status

If you request a report while it's still being generated, you'll receive a `202 Accepted` response with a `Retry-After` header:

```bash
curl -X GET "http://localhost:8000/report/martinpacesa/BindCraft/latest/report.md" \
  -H "Authorization: Bearer your-token"
```

Response (while generating):
```json
{
  "status": "generating",
  "retry-after": "Wed, 05 Oct 2025 12:35:00 GMT"
}
```

Output is generated as `{username}-{repo}-forks.md` by default (use `-o` to specify a different file name, `-o -` to print to stdout).

## See also

- [Useful forks](https://useful-forks.github.io/)
- [frogmouth](https://github.com/Textualize/frogmouth) - a quick viewer for the generated Markdown
