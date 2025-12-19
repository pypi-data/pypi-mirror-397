# VibeMem (`vibemem`)

VibeMem is a pip-installable CLI tool to manage reusable “memories” (findings / recipes / gotchas / preferences) for vibe-coding agents.

- Canonical storage: Weaviate (single collection: `VibeMemMemory`)
- Optional local cache: Chroma persisted under `~/.vibemem/chroma/` (per-repo subdirectory)
- Works from **any directory**: derives repo root + scope from your current working directory (override via flags)
- Default output: JSON (agent-friendly). Use `--human` for pretty output.

## Install

From PyPI:

```bash
python -m pip install -U vibemem
```

Editable install from this repo:

```bash
python -m pip install -e .
```

Optional cache support (Chroma):

```bash
python -m pip install -e ".[cache]"
```

Dev tools/tests:

```bash
python -m pip install -e ".[dev]"
pytest
```

### Install troubleshooting

If `pip install -U vibemem` fails with an `OSError: [Errno 2] No such file or directory`, it usually means `pip` fell back to building a dependency from source and a build tool is missing on your machine.

Try:

```bash
python -m pip install -U pip setuptools wheel
python -m pip install -U vibemem -v
```

If it still fails, paste the full `-v` output (it should include the missing executable/file), and try a clean reinstall:

```bash
python -m pip uninstall -y vibemem
python -m pip install -U --no-cache-dir vibemem
```

## Configuration

VibeMem reads connection settings from environment variables first, then falls back to a JSON config file at `~/.vibemem/config`.

### Env vars

- `VIBEMEM_WEAVIATE_URL` (required for Weaviate operations)
  - Examples: `http://localhost:8080` or `https://YOUR_CLUSTER.weaviate.cloud`
- `VIBEMEM_WEAVIATE_API_KEY` (optional; required for Weaviate Cloud URLs)
- `VIBEMEM_WEAVIATE_GRPC_URL` (optional)
  - Example: `http://localhost:50051`
- `VIBEMEM_WEAVIATE_COLLECTION` (default: `VibeMemMemory`)
- `VIBEMEM_CACHE_MODE` (default: `auto`) — `auto|on|off`

### Show effective config

```bash
vibemem config show
```

## Scope model

VibeMem derives scope from your current directory:

- Repo root is detected by searching upwards for `.git/` first; fallback markers: `pyproject.toml`, `package.json`, `go.mod`
- `repo_slug = basename(repo_root)`
- `rel_path = path from repo_root to cwd` (empty at repo root)

Scope ID derivation is controlled by `--granularity`:

- `repo` (default): `scope_id = repo_slug`
- `cwd`: `scope_id = repo_slug::<rel_path>`
- `path:N`: `scope_id = repo_slug::<first N path parts>`

Show current derived scope:

```bash
vibemem scope
```

## Commands

### Search

Search returns ranked memories with scope-aware bubbling (current scope → parent scopes → repo-level; and optionally global).

```bash
vibemem search "TypeError: ..." --top 8
```

Options:

- `--include-global/--no-include-global`
- `--include-parents/--no-include-parents`
- `--cache auto|on|off`

When Weaviate is unreachable and cache is ON (and built), `search` will fall back to Chroma.

### Add a memory

```bash
vibemem add --type recipe --text "Use X to fix Y" --tags "python,typing" --confidence high --verification "ran pytest"
```

Add structured metadata:

```bash
vibemem add --type gotcha --text "Chroma where filters differ by version" --error "ModuleNotFoundError: chromadb" --file "vibemem/store/chroma_cache.py" --cmd "pip install -e '.[cache]'"
```

### Edit / remove

```bash
vibemem edit <uuid> --text "updated text" --tags "a,b"
vibemem rm <uuid>
```

### List

```bash
vibemem list --scope project --limit 20
vibemem list --scope global --type gotcha
vibemem list --scope all --tag python
```

### Sync (pull)

Rebuild local cache from Weaviate:

```bash
vibemem sync --pull --limit 200
```

Notes:
- “Push/offline queue” is a TODO stub (not implemented).

## Output modes

Default output is JSON:

```bash
vibemem scope
```

Pretty output:

```bash
vibemem --human scope
```

## Example agent prompt

Use something like this with your AI vibe coder to propose memories for your review before writing anything:

```text
You have access to this repository’s files. I want you to propose a list of “memories” for me to authorize before creating them.

1) Scan the repo for important environment information and setup details that would help in other projects (env vars, required services, ports, build tools, OS-specific steps, CI quirks, etc.).
2) Scan the repo for anything unusual, surprising, or easy to forget (non-obvious defaults, tricky edge cases, sharp corners, gotchas).
3) Output a list of candidate memories for approval. For each item, include:
   - type (recipe|gotcha|preference|note)
   - text (1–3 sentences)
   - suggested tags
   - scope suggestion (global vs project) and why
4) Do not create or write anything until I approve each memory.
```

## Notes

- The Weaviate collection will be auto-created on first use if it doesn’t exist.
- If the Weaviate instance doesn’t have a text vectorizer module configured, VibeMem will fall back to a non-vectorized collection; search will still work via keyword matching (hybrid query behavior depends on server capabilities).
