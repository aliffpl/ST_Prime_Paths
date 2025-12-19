# PrimePaths

Complete prime-path testing framework.

# PrimePaths — Prime Path generation from source code CFGs

This tool:
- clones one or more repos (or reads local paths),
- extracts Control Flow Graphs (CFGs) directly from Python source code via `staticfg`,
- generates Prime Paths (for Prime Path Coverage / graph-based testing),
- exports results as JSON / text / DOT.

Prime paths are **simple paths that are not a proper subpath of any other simple path**.  
See docs for details.

## Install
# PrimePaths

PrimePaths is a small toolkit that extracts Control Flow Graphs (CFGs) from
Python source and computes Prime Paths for graph-based testing.

Key features:
- Clone or read local repositories and extract CFGs
- Compute prime paths (simple paths that are not a proper subpath of any other simple path)
- Export results as JSON, plain text, or DOT

Note: when available the project prefers `staticfg` for richer CFG extraction.
If `staticfg` is not installed, a conservative AST-based fallback is used.

## Install

Create and activate a virtual environment, then install in editable mode:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# or CMD
.\.venv\Scripts\activate.bat
pip install -e .
```

## CLI Usage

The package installs a `primepaths` console script (entry point: `primepaths.cli:main`).

Analyze a local path and write JSON results to `out`:

```bash
primepaths analyze /path/to/repo --out out --format json
```

Analyze a Git repository URL (shallow clone):

```bash
primepaths analyze https://github.com/owner/repo.git --out out --format txt
```

Output formats:
- `json`: writes `out/primepaths.json` with analysis records
- `txt`: writes `out/primepaths.txt` human-readable summary
- `dot`: writes DOT files into `out/dot/` and an index JSON

## Programmatic API

Minimal example using the fallback AST CFG extractor and prime-path generator:

```python
from pathlib import Path
from primepaths.cfg_extract import extract_cfgs_from_file
from primepaths.prime_paths import prime_paths

arts = extract_cfgs_from_file(Path('path/to/module.py'))
for art in arts:
	g = art.graph
	primes = prime_paths(g)
	print(art.file, art.function, len(primes))
```

## Testing

Run the unit tests with `pytest`:

```bash
pytest -q
```

## Contributing

If you want richer CFG extraction, install `staticfg` in the environment. See
`pyproject.toml` for declared (optional) dependencies.
