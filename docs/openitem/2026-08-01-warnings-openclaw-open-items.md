# Open Items: Warnungsbereinigung und OpenClaw-Harness

**Stand:** 2026-08-01
**Workflow:** `agent-workflow-v4`, `thorough`, `critical`, Teamgröße 10
**Status:** Offline-Warnungsgate PASS; Live-Gates HOLD

## Zusammenfassung und Evidenz

Die Root-Collection sammelt im frischen, gefrorenen Worktree-Environment 6384
Tests unter `--strict-markers` und meldet keine `Pytest*Warning`. Die beiden
Regressionen in `tests/test_collection_warnings.py` bestehen 2/2. Die
eigenständige OpenClaw-Harness sammelt in ihrer eigenen venv 47 Tests ohne
Collection-Warning; der ausschließlich gemockte Diagnostik-Satz besteht 4/4.

Untersucht wurden `pyproject.toml`, die drei betroffenen Root-Testdateien,
`tests/oc2ov_test/pyproject.toml`, `utils/test_utils.py`, die Harness-Clients,
das Harness-`run.sh`/`run_tests.py` und der Self-hosted Workflow. Es wurden
keine Provider-Credentials, Services oder Neustarts verwendet.

## Gap-Analyse

- H1/H2 und Provider-Live-Tests sind nicht durch Offline-Collection freigegeben.
- Die OpenClaw-P0-Suite benötigt ein laufendes OpenClaw-/OpenViking-System;
  `run.sh` und `run_tests.py` enthalten zusätzlich veraltete Pfade und dürfen
  offline nicht als Ausführungserfolg gewertet werden.
- Die allgemeine Root-Test-Fixture erwartet eine beschreibbare lokale
  OpenViking-Konfiguration. Der isolierte Warnungslauf umgeht diese Fixture;
  eine vollständige Root-Testausführung ist deshalb ein separater Gate.

## Priorisierte Maßnahmen

### High

| Maßnahme | Begründung | Komponenten | Wirkung | Risiko | Owner | Nächster Schritt |
|---|---|---|---|---|---|---|
| H1-Live-Capability erst freigeben | Modell-, Origin-, Limit- und Credential-Policy fehlen | Responses-/Codex-Gate | Verhindert ungeprüften Egress | Hoch bei voreiligem Start | `mcp_coordinator_agent` + Security | Separate Freigabe und Preflight vor I/O |
| H2-Benchmark hinter H1 halten | Keine Corpus- oder Live-Evidenz | Benchmark/Canary | Verhindert falsche Promotion | Hoch | `simulation_agent` | Erst nach H1-PASS 20+10 Szenarien ausführen |
| OpenClaw-P0 separat qualifizieren | P0 ruft reale CLI/Services auf | `tests/oc2ov_test/tests/p0` | Liefert echte Integrationsaussage | Hoch | `test_e2e_agent` | Live-Phase autorisieren, Settings/Services prüfen |

### Medium

| Maßnahme | Begründung | Komponenten | Wirkung | Risiko | Owner | Nächster Schritt |
|---|---|---|---|---|---|---|
| Root-Testausführung mit Fixture isolieren | Vollsuite benötigt beschreibbare OV-Konfiguration | `tests/conftest.py`, `ov.conf` | Trennt Collection- von Laufzeitfehlern | Mittel | `test_unit_agent` | Dedicated temp config und gezielte Offline-Matrix |
| Harness-Einstiegspunkte modernisieren | `run.sh`/`run_tests.py` verweisen auf veraltete Pfade | `tests/oc2ov_test/run.sh`, `run_tests.py` | Reproduzierbarer Besitzer-Workflow | Mittel | `code_quality_api_agent` | Separater TDD-Auftrag, keine Live-Ausführung vorab |
| Harness-Dependency-Lock einführen | Eigenes Projekt besitzt keinen `uv.lock` | `tests/oc2ov_test/pyproject.toml` | Reproduzierbare venv | Mittel | `devops_agent` | Lockfile- und CI-Entscheidung separat genehmigen |

### Low

| Maßnahme | Begründung | Komponenten | Wirkung | Risiko | Owner | Nächster Schritt |
|---|---|---|---|---|---|---|
| Offline-Manual um Harness-Contract ergänzen | Temporäre Settings sind sicherheitsrelevant | Root-Manual/README | Verhindert Credential-Leaks | Niedrig | `documentation_agent` | Beispiele synchron halten |
| Warnungs-Gate in CI sichtbar machen | Strict-Marker-Vertrag soll nicht regressieren | Root-CI | Frühere Diagnose | Niedrig | `devops_agent` | Nur Collection-Job ergänzen, kein Live-Job |
| Stale-Harness-Pfade als Issue markieren | Kein stilles `PASS` für `run.sh` | OpenClaw-Dokumentation | Klare Erwartung | Niedrig | `open_item_agent` | Nach Live-Freigabe priorisieren |

## Dokumentationsübergabe

Die technische Änderung, Testbefehle und Holds sind im aktualisierten PD/ARD/
TRD/ID, Testdossier und Manual verlinkt. Der STP enthält Worktree, Branch,
Hashes, sichere Wiederaufnahme und Stop-Regeln. `agy` blieb wegen fehlender
Headless-`command`-Berechtigung UNAVAILABLE und wurde nicht durch eine
unsichere Freigabe umgangen.
