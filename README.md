# uv sync/tool install bug reproduction

This repository demonstrates a bug in `uv sync` and `uv tool install` where base
dependencies are not properly maintained when switching between extras.

## The Bug

When a package has:
- Base dependency: `typer>=0.20.0`
- Extra1 that adds: `typer-slim>=0.20.0`
- Extra2 that adds: `rich>=13.0.0` (already satisfied by typer)

Switching extras causes the base dependency to disappear.

## Reproduction with `uv sync`

This is the easiest way to test since it's isolated to the project directory:

```bash
git clone https://github.com/pimlock/uv-bug-repro
cd uv-bug-repro

# Step 1: Sync base - works
uv sync
uv run repro-cli  # ✓ Hello from repro-cli!

# Step 2: Sync with extra1 - works
uv sync --extra extra1
uv run repro-cli  # ✓ Hello from repro-cli!

# Step 3: Sync with extra2 - FAILS
uv sync --extra extra2
uv run repro-cli  # ✗ ModuleNotFoundError: No module named 'typer'
```

Output:
```
➜ uv sync
Using CPython 3.14.0
Creating virtual environment at: .venv
Resolved 11 packages in 843ms
      Built uv-bug-repro @ file:///.../2026-01-21-uv-repro
Prepared 1 package in 2.13s
Installed 9 packages in 87ms
 + click==8.3.1
 + markdown-it-py==4.0.0
 + mdurl==0.1.2
 + pygments==2.19.2
 + rich==14.2.0
 + shellingham==1.5.4
 + typer==0.21.1
 + typing-extensions==4.15.0
 + uv-bug-repro==0.1.0 (from file:///.../2026-01-21-uv-repro)

➜ uv run repro-cli
Hello from repro-cli!

➜ uv sync --extra extra1
Resolved 11 packages in 3ms
Prepared 1 package in 335ms
Installed 1 package in 39ms
 + typer-slim==0.21.1

➜ uv run repro-cli
Hello from repro-cli!

➜ uv sync --extra extra2
Resolved 11 packages in 2ms
Uninstalled 1 package in 18ms
 - typer-slim==0.21.1

❯ uv run repro-cli
Traceback (most recent call last):
  File ".../2026-01-21-uv-repro/.venv/bin/repro-cli", line 4, in <module>
    from uv_bug_repro import main
  File ".../2026-01-21-uv-repro/src/uv_bug_repro/__init__.py", line 1, in <module>
    import typer
ModuleNotFoundError: No module named 'typer'
```

## What happens

1. **Step 1**: `typer==0.21.1` installed (which depends on `typer-slim`)
2. **Step 2**: `typer-slim==0.21.1` added explicitly (was already a transitive dep)
3. **Step 3**: `typer-slim==0.21.1` removed, but `typer` is ALSO removed even though
   `typer>=0.20.0` is a base dependency that should always be present

## Expected Behavior

The base dependency `typer>=0.20.0` should be installed in ALL cases,
regardless of which extras are selected.

## Workaround

Using `--reinstall` forces a clean resolution and avoids the bug:

```bash
uv sync --extra extra2 --reinstall  # ✓ works
uv tool install ".[extra2]" --reinstall  # ✓ works
```

## Environment

- uv version: 0.9.26
- Python: tested on 3.11 and 3.14
