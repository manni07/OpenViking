# Session Transfer Protocol: Root-Warnungen und OpenClaw-Harness

**Stand:** 2026-08-01
**Repository:** `manni07/OpenViking`
**Basis:** `origin/main` / Merge #5, `22919c337f2837ab65cbc4d778496090f9d77fad`
**Worktree:** `/Volumes/ExtremePro/projects/OpenViking-agent-worktrees/20260801-warnings-openclaw-fix`
**Branch:** `agent-workflow/20260801-warnings-openclaw-fix`
**Workflow:** `$tccode` + `agent-workflow-v4`, `thorough`, `critical`, Team 10

## Ziel und aktueller Stand

Die 15 zuvor offenen Root-Pytest-Warnungen sind geschlossen. Die Root-Suite
sammelt in einer frischen gefrorenen venv 6384 Tests mit
`--strict-markers`, Exit 0 und ohne `Pytest*Warning`. Die separate
OpenClaw-Harness sammelt 47 Tests ohne Collection-Warning; die gemockte
Diagnostik besteht 4/4.

Die tatsächlichen OpenClaw-/OpenViking-P0-Aufrufe, H1/H2 und Provider-Live-
Tests bleiben HOLD. Der Full-Root-Testlauf ist wegen der allgemeinen
`/app`-/`ov.conf`-Fixtureannahme nicht Teil dieses Collection-Gates. Kein
Service, Server, Container, Runtime oder Rechner wurde neu gestartet.

## Geänderte Dateien

- `pyproject.toml`: `cli_remote` und `qdrant` registriert.
- `tests/session/memory/test_json_stability.py`: zwei Supportmodelle neutral
  benannt.
- `tests/unit/test_accessors_registry.py`: Support-Accessor neutral benannt.
- `tests/test_collection_warnings.py`: test-first Collection-Verträge.
- `tests/oc2ov_test/pyproject.toml`: `tests` als einziger Testpfad sowie
  `pythonpath` für lokale Harness-Imports.
- `tests/oc2ov_test/utils/test_utils.py` und Harness-Aufrufer:
  `ScenarioData`/`ScenarioDataManager`.
- aktualisierte Dossiers, Testdossier, PD, Manual, Diary und Open-Item-Bericht.

## Reproduzierbare Offline-Befehle

```bash
cd /Volumes/ExtremePro/projects/OpenViking-agent-worktrees/20260801-warnings-openclaw-fix
UV_PROJECT_ENVIRONMENT=.venv-root-collect uv sync --frozen --python 3.12.11 --extra test
env -u GOOGLE_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENAI_ACCESS_TOKEN \
  .venv-root-collect/bin/python -m pytest tests --collect-only -q \
  -o addopts= -p no:cacheprovider --no-cov --strict-markers
.venv-root-collect/bin/python -m pytest tests/test_collection_warnings.py -q \
  -o addopts= -p no:cacheprovider --no-cov

cd tests/oc2ov_test
uv venv --python 3.12.11 .venv-oc2ov
uv pip install --python .venv-oc2ov/bin/python \
  'pytest>=7.0.0' 'pytest-html>=4.0.0' 'requests>=2.28.0'
cp config/settings.example.py config/settings.py  # temporär, ignoriert
.venv-oc2ov/bin/python -m pytest --collect-only -q -o addopts= \
  -p no:cacheprovider -W error::pytest.PytestCollectionWarning
.venv-oc2ov/bin/python -m pytest tests/test_cli_diagnostics.py -q \
  -o addopts= -p no:cacheprovider
unlink config/settings.py
```

## Wiederaufnahme- und Stop-Regeln

1. Vor jeder Fortsetzung `git status --short --branch`, `git diff --check`
   und `git log -1 --oneline` ausführen.
2. Keine Root-Collection-Grenze über `api_test`/`oc2ov_test` hinaus erweitern.
3. Keine echte `config/settings.py`, Credentials, `openclaw agent`,
   `run.sh`, `run_tests.py`, Workflow- oder Upgrade-Skripte ausführen.
4. Bei Lockdrift, neuen Collection-Kategorien, Netzwerk-/Credential-I/O,
   Servicezustand oder Restart sofort HOLD und nicht automatisch reparieren.
5. H1/H2 erst nach separater Autorisierung, vollständigen Limits und
   Capability-/Corpus-Gates beginnen.

## Reviews und offene Evidenz

Der Agent-Workflow-Orchestrator gab den Offline-Diff mit 96,2 % Aggregat frei
(C1 98, C2 97, C3 95, C4 96, C5 95). Der `agy`-Aufruf nach `agy --help`
blieb wegen fehlender Headless-`command`-Berechtigung UNAVAILABLE; es wurde
kein `--dangerously-skip-permissions` verwendet. Die Open-Item-Übergabe liegt
unter `docs/openitem/2026-08-01-warnings-openclaw-open-items.md`.
