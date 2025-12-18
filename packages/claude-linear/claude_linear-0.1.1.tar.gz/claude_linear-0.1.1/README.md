# Claude-Linear Automation

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/claude-linear.svg)](https://pypi.org/project/claude-linear/)

Automate software development with Claude Code, Linear, and GitHub Actions. Add a label to a Linear issue, and Claude will design, implement, test, and create a pull request.

## Quick Start

### 1. Install the CLI

```bash
pip install claude-linear
```

### 2. Run the Setup Wizard

```bash
claude-linear setup
```

The wizard will:
- Connect to your Linear workspace
- Create all required labels (16 labels in the "Claude" group)
- Generate secure secrets
- Show you exactly what to configure in Vercel and GitHub

### 3. Deploy the Orchestrator

```bash
cd orchestrator
vercel deploy
```

Add the environment variables shown by the setup wizard.

### 4. Create the Linear Webhook

1. Go to Linear Settings > API > Webhooks
2. Create webhook: `https://your-app.vercel.app/webhooks/linear`
3. Enable "Issues" and "Projects" resources
4. Copy the webhook secret to Vercel

### 5. Install Templates in Your Repos

```bash
claude-linear init /path/to/your/repo
```

Add the GitHub secrets shown by the setup wizard.

### 6. Start Automating

Add the **"Ready for Claude Code"** label to any Linear issue. Claude will take it from there!

---

## How It Works

```
┌──────────┐         ┌─────────────────┐         ┌──────────────┐
│  Linear  │ webhook │   Orchestrator  │ dispatch│   GitHub     │
│          │────────>│    (Vercel)     │────────>│   Actions    │
│  Issues  │         │                 │         │              │
└──────────┘         └─────────────────┘         └──────────────┘
      ^                       ^                          │
      │                       │ API calls                │
      │   label updates       │                          v
      │   comments            │                   ┌──────────────┐
      └───────────────────────┼───────────────────│    Runner    │
                              │                   │ (Claude Code)│
                              └───────────────────┴──────────────┘
```

1. **You** add a label to a Linear issue
2. **Linear** sends a webhook to the orchestrator
3. **Orchestrator** dispatches a GitHub Actions workflow
4. **Runner** executes Claude Code to analyze, design, implement, and test
5. **Claude** creates a PR and updates Linear with progress

---

## Features

### Issue Flow (13 Stages)

When you add **"Ready for Claude Code"** to an issue:

1. **Design Doc** — Claude analyzes the codebase and writes a design document
2. **Design Review** — Claude reviews and improves the design
3. **Implementation Plan** — Claude creates a step-by-step implementation plan
4. **Implementation** — Claude writes the code
5. **Browser Tests** — Runs E2E tests (if configured)
6. **Unit Tests** — Runs test suite with auto-fix on failure
7. **Pre-commit** — Runs linters and formatters
8. **Code Review** — Claude reviews its own changes
9. **Create PR** — Creates a pull request
10. **PR Review Loop** — Claude reviews the PR diff and applies fixes
11. **Ready for Human Review** — Final stage for you to review

### Project Flows

- **Enhance with Claude** — Analyzes repo and enriches project description
- **Create issues with Claude** — Generates actionable issues from codebase analysis

---

## Configuration

### Per-Repository Config (`.claude/automation.yml`)

```yaml
# Test commands
tests: "pytest -q"
browser_test: "npx playwright test"
precommit: "pre-commit run --all-files"

# Dev server (for browser tests)
run_dev: "./run-dev"
dev_url: "http://127.0.0.1:3000"
dev_ready_regex: "Listening|ready|started"

# Limits
max_fix_attempts: 4
max_review_iterations: 3
max_code_review_iterations: 2
```

All fields are optional. Skip any test stage by omitting its command.

### Environment Variables

**Vercel (Orchestrator):**

| Variable | Description |
|----------|-------------|
| `LINEAR_API_KEY` | Linear API key (starts with `lin_api_`) |
| `LINEAR_WEBHOOK_SECRET` | From Linear webhook settings |
| `GITHUB_DISPATCH_TOKEN` | GitHub PAT with `repo` scope |
| `AGENT_SHARED_SECRET` | Shared secret for runner auth |
| `DEFAULT_LINEAR_TEAM_ID` | Default team for issue creation |

**GitHub (Per Repository):**

| Secret | Description |
|--------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `CLAUDE_AGENT_API_BASE` | Orchestrator URL |
| `CLAUDE_AGENT_TOKEN` | Same as `AGENT_SHARED_SECRET` |

---

## CLI Commands

```bash
claude-linear setup      # Interactive setup wizard
claude-linear validate   # Validate configuration
claude-linear init       # Install templates to a repo
claude-linear labels     # Manage Linear labels
claude-linear --version  # Show version
```

### Validate Your Setup

```bash
claude-linear validate --api-base https://your-app.vercel.app

Validating configuration...
  ✓ Orchestrator health check passed
  ✓ Linear API key valid
  ✓ Linear labels exist (16/16)
  ✓ GitHub token has required scopes
```

---

## Deployment

### Vercel (Recommended)

1. Fork or clone this repository
2. Connect to Vercel with root directory `orchestrator`
3. Add environment variables from setup wizard
4. Deploy

### Manual / Docker

```bash
cd orchestrator
pip install -e ".[server]"
uvicorn api.index:app --host 0.0.0.0 --port 8000
```

---

## Development

```bash
# Clone the repo
git clone https://github.com/anthropics/claude-linear-automation.git
cd claude-linear-automation

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v

# Run linting
ruff check .

# Run type checking
mypy orchestrator/ cli/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — System design and data flow
- [Troubleshooting](docs/TROUBLESHOOTING.md) — Common issues and solutions
- [Contributing](CONTRIBUTING.md) — Development setup and guidelines

---

## Safety Notes

This automation runs Claude Code with full repository access. Consider:

- Use in trusted repositories only
- Don't expose production secrets to the workflow
- Review PRs before merging (Claude creates them, you approve them)
- Enable GitHub branch protection rules

---

## Secret Rotation

Rotate secrets immediately if you suspect a compromise. Here's the procedure for each secret:

### AGENT_SHARED_SECRET

This is the shared token between the orchestrator and GitHub Actions runners.

1. Generate a new secret:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. Update in **Vercel**: Environment Variables > `AGENT_SHARED_SECRET`
3. Update in **all GitHub repositories**: Settings > Secrets > `CLAUDE_AGENT_TOKEN`
4. Redeploy the orchestrator on Vercel
5. Any in-flight workflows will fail and need to be re-triggered

### LINEAR_API_KEY

1. Go to Linear Settings > API > Personal API Keys
2. Create a new key and copy it
3. Update in **Vercel**: Environment Variables > `LINEAR_API_KEY`
4. Revoke the old key in Linear
5. Redeploy the orchestrator

### LINEAR_WEBHOOK_SECRET

1. Go to Linear Settings > API > Webhooks
2. Delete the existing webhook
3. Create a new webhook with the same URL
4. Copy the new signing secret
5. Update in **Vercel**: Environment Variables > `LINEAR_WEBHOOK_SECRET`
6. Redeploy the orchestrator

### GITHUB_DISPATCH_TOKEN

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a new token with `repo` scope
3. Update in **Vercel**: Environment Variables > `GITHUB_DISPATCH_TOKEN`
4. Revoke the old token in GitHub
5. Redeploy the orchestrator

### ANTHROPIC_API_KEY

1. Go to [console.anthropic.com](https://console.anthropic.com) > API Keys
2. Create a new key
3. Update in **all GitHub repositories**: Settings > Secrets > `ANTHROPIC_API_KEY`
4. Disable or delete the old key in Anthropic Console
5. Any in-flight workflows will fail and need to be re-triggered

### Emergency Rotation (All Secrets)

If you need to rotate all secrets immediately:

```bash
# 1. Generate new secrets locally
export NEW_AGENT_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
echo "New AGENT_SHARED_SECRET: $NEW_AGENT_SECRET"

# 2. Update Vercel (via CLI or dashboard)
# 3. Update GitHub repository secrets
# 4. Regenerate Linear API key and webhook
# 5. Regenerate GitHub PAT
# 6. Regenerate Anthropic API key
# 7. Redeploy orchestrator
# 8. Verify with: claude-linear validate
```

### Recommended Rotation Schedule

- **AGENT_SHARED_SECRET**: Every 90 days
- **LINEAR_API_KEY**: Every 90 days
- **GITHUB_DISPATCH_TOKEN**: Every 90 days
- **ANTHROPIC_API_KEY**: Every 90 days
- **LINEAR_WEBHOOK_SECRET**: Only when compromised (rotating requires webhook recreation)

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Support

- [Report Issues](https://github.com/accomplish-ai/claude-linear-automation/issues)
- [Discussions](https://github.com/accomplish-ai/claude-linear-automation/discussions)
