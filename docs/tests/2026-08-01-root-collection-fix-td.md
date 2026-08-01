# Test Dossier: Root-Test-Collection

**Stand:** 2026-08-01
**Status:** Collection-Fix PASS; eigenstaendige Harnesses und Live-Phasen nicht ausgefuehrt

## 1. Ziel und Erfolgsvertrag

Dieser Fix schliesst exakt die 20 vorbestehenden Collection-Fehler:

| Fehlergruppe | Anzahl | Ursache | Verifizierter Fix |
|---|---:|---|---|
| Root-Abhaengigkeiten | 8 | Wiederverwendete, nicht kanonische venv ohne `mcp` und `scrapy` | Frische, lockfile-basierte Worktree-venv enthaelt `mcp 1.28.1` und `scrapy 2.16.0` |
| Eigenstaendige Harnesses | 11 | Root-Pytest sammelte `tests/api_test` und `tests/oc2ov_test` trotz eigener Umgebungen und Workflows | Root-Collection ignoriert exakt `api_test` und `oc2ov_test` |
| Optionaler Provider | 1 | Gemini-E2E importierte `google.genai` transitiv bereits bei der Collection | Providerimport erst bei Fixture-/Testausfuehrung |

Die Regressionstests kodieren den Grund der Grenzen: Der Root-Lauf darf keine
eigenstaendigen Live-Harnesses vereinnahmen; ein deaktivierter optionaler
Provider darf die Collection nicht verhindern; bei tatsaechlicher Nutzung muss
ein fehlendes Provider-Extra laut fehlschlagen.

## 2. TDD-Evidenz

### 2.1 RED

Der erste Vertragstestlauf verwendete nur den vorhandenen diagnostischen
Interpreter, nicht die spaeter hergestellte kanonische Umgebung:

```bash
PYTHONPATH=.:bot:/tmp/openviking-codex-responses-test-deps-20260731:/tmp/openviking-pytest-html-Dcw39z \
  /Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m pytest \
  tests/test_test_suite_boundaries.py \
  -q -o addopts= -p no:cacheprovider --no-cov
```

Ergebnis: **3 FAIL**. Die Tests fanden die fehlende exakte
`collect_ignore`-Grenze und den Top-Level-Import des Gemini-Embedders.

### 2.2 GREEN im diagnostischen Interpreter

Dasselbe Kommando nach der minimalen Implementierung ergab **3 PASS** und eine
vorbestehende unbekannte `qdrant`-Marker-Warnung. Dieser Lauf war nur ein
TDD-Zwischenbeleg; er ist kein Nachweis einer kanonischen Root-Umgebung.

## 3. Kanonische Testumgebung

Die isolierte Worktree-Umgebung wurde reproduzierbar aus `uv.lock` erstellt:

```bash
UV_PROJECT_ENVIRONMENT=.venv-root-collect \
  uv sync --frozen --python 3.12.11 --extra test
```

Verifiziert:

```text
uv       0.8.20
Python   3.12.11
mcp      1.28.1
scrapy   2.16.0
```

Der Build war erfolgreich. Es wurden keine Provider-Credentials verwendet,
keine Services gestartet oder neugestartet und keine Live-Endpunkte aufgerufen.

## 4. Finale Offline-Evidenz

### 4.1 Vertragsregressionen

```bash
env -u GOOGLE_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY \
  .venv-root-collect/bin/python -m pytest \
  tests/test_test_suite_boundaries.py \
  -q -o addopts= -p no:cacheprovider --no-cov
```

Ergebnis: **3 PASS**; eine vorbestehende unbekannte `qdrant`-Marker-Warnung.

### 4.2 Gemini-Collection ohne Credentials

```bash
env -u GOOGLE_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY \
  .venv-root-collect/bin/python -m pytest \
  tests/integration/test_gemini_e2e.py --collect-only \
  -q -o addopts= -p no:cacheprovider --no-cov
```

Ergebnis: **5 Tests gesammelt**, Exitcode 0. Die Collection importiert die
optionale Gemini-Implementierung nicht. Eine spaetere echte Ausfuehrung bleibt
credential- und providerabhaengig und wurde nicht vorgenommen.

### 4.3 Vollstaendige Root-Collection

```bash
env -u GOOGLE_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY \
  -u OPENAI_ACCESS_TOKEN \
  .venv-root-collect/bin/python -m pytest \
  tests --collect-only \
  -q -o addopts= -p no:cacheprovider --no-cov
```

Ergebnis:

```text
6382 tests collected in 18.07s
exit code 0
0 collection errors
```

Eine zusaetzliche pipe-basierte Re-Collection der Boundary-Datei bestand
ebenfalls. Sie ist ein Konsistenzbeleg, kein Ersatz fuer einen unabhaengigen
Testlauf.

## 5. Verbleibende Warnungen

Die erfolgreiche Root-Collection meldet ausserhalb des exakten 20-Fehler-Scopes:

- 11 unbekannte `cli_remote`-Marker-Warnungen;
- 1 unbekannte `qdrant`-Marker-Warnung;
- 3 `PytestCollectionWarning`-Meldungen fuer Hilfsklassen.

Diese Warnungen wurden weder verdeckt noch als PASS klassifiziert. Sie sind im
Open-Item-Bericht separat erfasst.

## 6. Aussagegrenze

PASS bedeutet ausschliesslich: Die Root-Testsammlung laeuft in der frischen,
lockfile-basierten Umgebung ohne Collection-Fehler durch und die drei neuen
Grenzvertraege bestehen.

Nicht ausgefuehrt und daher **nicht PASS**:

- die eigentlichen Tests von `tests/api_test` und `tests/oc2ov_test`;
- die vollstaendige Root-Testausfuehrung ohne `--collect-only`;
- Gemini-, OpenAI- oder andere Provider-Live-Tests;
- H1 Capability-Probe, H2 Live-Benchmark oder Canary;
- Service-, Runtime-, Container-, Server- oder Rechner-Restarts.

## 7. Geaenderte Dateien

- `tests/conftest.py`
- `tests/integration/test_gemini_e2e.py`
- `tests/test_test_suite_boundaries.py`

## 8. Warnungsbereinigung und Standalone-Harness — 2026-08-01

Dieser Nachlauf behandelt die zuvor bewusst offenen 15 Root-Warnungen und
trennt die OpenClaw-Harness weiterhin vom Root-Collector.

### 8.1 RED vor der Änderung

In der frisch erzeugten Worktree-Umgebung schlug der Strict-Marker-Lauf mit
Exit 2 fehl: elf `cli_remote`- und ein `qdrant`-Marker waren nicht registriert
(12 Collection-Fehler). Der gezielte Lauf mit
`-W error::pytest.PytestCollectionWarning` schlug zusätzlich an den drei
Hilfsklassen `TestModel`, `TestModel` und `TestAccessor` fehl.

### 8.2 Root-GREEN

- `pyproject.toml` registriert jetzt ausschließlich die beiden fehlenden
  Marker mit ihrer externen Service-Bedeutung.
- Die drei Supportklassen tragen neutrale Namen
  `JsonStabilityModel`, `JsonUtilsModel` und `RegistryAccessor`; ihre
  Testmethoden und Laufzeitsemantik bleiben unverändert.
- `tests/test_collection_warnings.py` hält Strict-Marker- und
  `PytestCollectionWarning`-Verträge test-first fest; beide Tests bestehen mit
  2/2.
- Mit uv 0.8.20, Python 3.12.11 und der frischen gefrorenen Umgebung sammelt
  die Root-Suite unter `--strict-markers` 6384 Tests, Exit 0. Die normale
  Collection sammelt ebenfalls 6384 Tests und meldet keine
  `Pytest*Warning`-Zeile.
- Die beiden Supportdateien bestehen isoliert ohne Root-Service-Fixture mit
  43/43 Tests (`--noconftest`). Ein breiterer Aufruf ohne diese Isolation
  bleibt wegen der vorhandenen `/Users/turgay/.openviking/ov.conf`-/
  `/app`-Pfadannahme der allgemeinen Root-Fixture blockiert; das ist kein
  Fehler der Warnungsänderung.

### 8.3 OpenClaw-Harness, separat und offline

Die Harness-Konfiguration nutzt jetzt ausschließlich `tests` als Testpfad und
trägt `.` sowie `utils` in `pythonpath`. Die importierten Datenklassen heißen
`ScenarioData` und `ScenarioDataManager`, sodass `utils/test_utils.py` nicht
mehr als Testklasse gewarnt wird. `config/settings.py` bleibt absichtlich
ignoriert und wird nur für einen Lauf aus `settings.example.py` erzeugt.

Der sichere Lauf im eigenen `tests/oc2ov_test/.venv-oc2ov` sammelte mit
`-W error::pytest.PytestCollectionWarning` 47 Tests, Exit 0. Der ausschließlich
gemockte Diagnostik-Satz bestand mit 4/4. Die temporäre Beispielkonfiguration
wurde danach entfernt; es wurden keine Credentials verwendet.

Nicht ausgeführt und daher weiterhin **HOLD**: P0-/OpenClaw-Agent-Aufrufe,
OpenViking-/OpenClaw-Servicezugriffe, `run.sh`/`run_tests.py`, der Upgrade-
Workflow sowie H1, H2 und Provider-Live-Tests. Kein Service-, Server-,
Runtime- oder Rechnerneustart erfolgte.
