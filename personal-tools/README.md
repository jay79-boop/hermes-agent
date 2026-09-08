# personal-tools

Non-trading tools, docs, tests and static pages moved here from
`jay79-boop/pwb-toolbox` in the 2026-09-08 reorg (that repo now carries only
trading work). This mirrors pwb-toolbox's own `tools/`, `docs/`, `tests/`,
`static/` layout on purpose, so each tool's existing relative-path logic
(`Path(__file__).resolve().parents[N]`) keeps working unchanged.

**Run everything from inside this directory, not the hermes-agent repo
root** — hermes-agent's own top-level `tools/` is its auto-imported agent-tool
registry (`tools/registry.py` globs `tools/*.py` at startup), a different
thing with the same name. `python -m tools.karaoke_server` or
`python -m tools.grok_export` only resolve correctly with `personal-tools/` as
the working directory:

```bash
cd personal-tools
python -m tools.karaoke_server
python tools/ai_company.py gates
pytest tests/ -v
```

See each tool's own docstring or README under `tools/` for what it does.
