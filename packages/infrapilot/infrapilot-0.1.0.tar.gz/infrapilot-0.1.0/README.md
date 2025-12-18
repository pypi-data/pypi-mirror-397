# InfraPilot CLI

The InfraPilot CLI is an interactive REPL that talks to the local InfraPilot backend to manage workspaces, threads, and chat sessions. It ships with persistent command history, tab-completion, Auth0 login flow, and a local SQLite cache so you can pick up where you left off between sessions.

This README explains how to install dependencies, configure the CLI, run it, and extend it during development.

---

## 1. Prerequisites

| Requirement | Notes |
| ----------- | ----- |
| Python 3.13 | The CLI targets 3.13 (see `pyproject.toml`). |
| [`uv`](https://github.com/astral-sh/uv) | Handles installs + command execution. |
| InfraPilot backend | Default: `https://infrapilot.dev` (override via `INFRAPILOT_API_URL` for local dev). |
| Auth0 access | Needed for the login/refresh/logout flows. |

Install `uv` once:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# or
brew install uv
```

---

## 2. Install

Registry install (recommended for day-to-day use):

```bash
pipx install infrapilot
# or
pip install infrapilot
```

Git install (internal/early users, pinned to a tag):

```bash
pipx install git+https://github.com/<org>/infrapilot.git@v0.3.1#subdirectory=cli
# or
pip install git+https://github.com/<org>/infrapilot.git@v0.3.1#subdirectory=cli
```

Upgrade:

```bash
pipx upgrade infrapilot
# or
pip install --upgrade infrapilot
```

Local editable install for development:

```bash
pipx install -e ./cli
```

```bash
cd cli
uv sync --group dev           # installs deps pinned in uv.lock
uv run infrapilot --help      # smoke test the entrypoint
```

### Environment Variables

| Var | Description | Default |
| --- | ----------- | ------- |
| `INFRAPILOT_API_URL` | Base URL for the backend | `https://infrapilot.dev` |
| `INFRAPILOT_API_PREFIX` | API prefix appended to the base URL | `/infrapilot/api/v1` |
| `INFRAPILOT_HOME` | Overrides the config/db root (default: `~/.infrapilot`) | – |
| `INFRAPILOT_DB_PATH` | Forces the SQLite file path | `~/.infrapilot/infrapilot.db` |

For development, you can skip the Auth0 browser flow:

```bash
uv run infrapilot -- --skip-auth
```

The flag only works for local builds; production usage should go through `login`.

---

## 3. Running the REPL

```bash
uv run infrapilot
```

Features:

- **Persistent history** – Commands you run in the REPL are stored under `~/.infrapilot/repl_history`. Use ↑/↓ to cycle through them across sessions.
- **Tab completion** – Press Tab to auto-complete any top-level command (case-insensitive).
- **Colorized output** – Driven by `rich` + the selected theme.
- **Event logging** – Every significant action (login, workspace CRUD, thread CRUD) is logged via `component_logger`.

---

## 4. Command Reference

| Command | Description |
| ------- | ----------- |
| `help` | Show all commands and descriptions. |
| `login` / `logout` / `refresh` | Auth0 login flow, logout, or force-refresh tokens. |
| `whoami` | Display the authenticated Auth0 profile and sync workspaces. |
| `workspaces` | Interactive list picker (with select/delete). |
| `workspaces create [name] [region] [aws_profile]` | Create a workspace. Random name generated if omitted. |
| `workspaces delete <id|name>` | Delete a workspace via CLI (default workspace is protected). |
| `threads` | Interactive picker in the active workspace (select or delete). |
| `threads delete <id|title>` | Delete a thread and its messages. |
| `chat [title]` | Start or continue a thread, then send chat messages. |
| `files` | List runs for the **active workspace** and browse their artifacts (view/download). |
| `files all` | List runs across **all** workspaces and browse their artifacts. |
| `theme` | Toggle between light/dark themes. |
| `clear` / `exit` / `quit` | Clear the console or leave the REPL. |

### Interactive Pickers

Both `workspaces` and `threads` launch a radio-list dialog with **Select / Delete / Cancel** buttons. When you choose Delete, a confirmation dialog reminds you that the action is permanent. The CLI logs every attempt, including blocked deletes (e.g., trying to delete the auto-provisioned default workspace).

---

## 5. Artifact browsing (CLI UX)

- `files` shows only runs for the **current workspace**, using the existing select UI. Selecting a run reveals its metadata and lets you view or download any generated artifact (Terraform, CI, Dockerfiles, logs, metadata). Downloads use presigned URLs and save to the current folder; views render inline.
- `files all` lists runs across **all** workspaces, then lets you drill into a run and its artifacts with the same UI.
- Artifacts are always scoped to their run/workspace; nothing leaks between workspaces.

---

## 6. Local Persistence

- **Config & history** – Stored under `~/.infrapilot/` (or `INFRAPILOT_HOME`). Includes `config.json`, `repl_history`, and cached theme/user metadata.
- **Tokens** – Managed by `keyring` + `TokenStore`. The CLI never writes raw tokens into plain-text config files.
- **SQLite cache** – `~/.infrapilot/infrapilot.db` stores users, workspaces, threads, and messages for offline access. Schema migrations run on CLI startup; if you upgrade branches frequently, simply re-run the CLI and it will patch the local DB.

---

## 7. Development Tasks

| Task | Command |
| ---- | ------- |
| Format | `uv run black . && uv run isort .` |
| Lint | `uv run flake8 .` |
| Tests | `uv run pytest` |
| Pre-commit install | `uv run --group dev python -m pre_commit install` |

Run commands from the `cli/` directory so `uv` picks up the correct `pyproject.toml`.

---

## 8. Troubleshooting

| Symptom | Fix |
| ------- | --- |
| `Authentication required. Please run 'login'.` | Run `login` or `refresh`. When scripting, export a valid Access Token via `TokenStore`. |
| `Backend request failed: Not Found` after deleting | The CLI handles stale cache entries automatically; rerun the command and the cache will resync. |
| SQLite `NOT NULL` constraint errors | Make sure you’re on the latest CLI build. Migrations run on startup, but you can delete `~/.infrapilot/infrapilot.db` if needed (tokens/config remain intact). |
| Tab completion not working | Ensure you’re at the top-level REPL prompt (`infrapilot>`). Inside `chat` mode, prompt-toolkit falls back to plain input so chats aren’t stored in history. |

---

## 9. Extending the CLI

- Commands live in `infrapilot_cli/ui/repl.py`. Add new `_cmd_*` handlers and register them in `self.commands`.
- HTTP interactions go through `infrapilot_cli/backend/client.py`. Always wrap backend calls with `_call_backend` so auth + error handling stays consistent.
- Local persistence helpers live in `infrapilot_cli/database/store.py`. Use them to keep the SQLite cache synchronized.
- Logging: use `self.event_logger.info(...)` with structured fields so you can trace actions across the CLI and backend logs.

With these guardrails, you can confidently extend InfraPilot’s CLI without breaking the current UX.

---

## 10. Versioning & Releases

- Use semantic versions and keep `cli/pyproject.toml` aligned with Git tags (e.g., `0.3.1` and `v0.3.1`).
- Tag releases before publishing to a registry.
- Never reuse a version number.

---

## 11. Install Verification Checklist

- Fresh install works (registry or Git tag).
- `infrapilot --help` runs without repo files present.
- Upgrade works (`pipx upgrade infrapilot` or `pip install --upgrade infrapilot`).
- No credentials are bundled; secrets load only at runtime.
