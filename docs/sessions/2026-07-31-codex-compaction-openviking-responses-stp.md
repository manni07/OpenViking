# Session Transfer Protocol: Offline-HOLD-Lift

**Stand:** 2026-07-31
**Status:** OFFLINE LEGACY-VLM HOLD AUFGEHOBEN / LIVE M1 HOLD
**Workflow:** `$tccode`, `thorough`, `critical`; Agent Workflow v4, Team 10
**Open Items:**
[Open-Item-Bericht](2026-07-31-codex-compaction-openviking-responses-open-items.md)

Dieses Dokument ist der normative, restartbare Abschluss des neuen,
user-autorisierten Offline-Zyklus. Aeltere Abschnitte in Dossiers dokumentieren
das fruehere VETO historisch; sie sind keine aktuelle Clearance.

## 1. Repository- und Autoritaetsstatus

| Feld | Exakter Wert |
|---|---|
| Repository | `volcengine/OpenViking` ueber Fork-Remote `manni07/OpenViking` |
| Worktree | `/Volumes/ExtremePro/projects/OpenViking-agent-worktrees/20260731-legacy-vlm-repair` |
| Branch | `agent-workflow/20260731-legacy-vlm-repair` |
| Veroeffentlichter Vorgaenger-HEAD | `a4b8f91c64803983f356c20cd848bd877a097d00` |
| Draft-PR | `https://github.com/volcengine/OpenViking/pull/3667` |
| PR Base / Head | `main` / `agent-workflow/20260731-legacy-vlm-repair` |
| Aktivierung | nicht erfolgt |

Vor Fortsetzung `git status`, Branch, `git rev-parse HEAD` und PR-Head
read-only pruefen. Keine fremden Aenderungen verwerfen, kein Rebase, Merge oder
Reset als implizite Reparatur.

## 2. Gate-Entscheidung

Der User autorisierte nach dem alten finalen HOLD einen neuen Offline-Zyklus.
Architektur 97/96/100, Pre-Source Security 93/100 bei 0C/0H und
Implementierungssimulation 96,6 Prozent (Minimum 95) oeffneten den engen
Source-Scope. Der erste Source-Stand bestand 267/267, wurde aber durch Security
Rev1 erneut gesperrt:

| Gate | Ergebnis |
|---|---|
| Security Rev1 | `86/100`, `0C/1H/2M`, VETO |
| H6 | Markerzuweisung kann Primärfehler ersetzen und Cleanup verhindern |
| M2 | Aggregate-Grenze vertraut einem taeuschenden `len()` |
| neue direkte Tests | 5 RED aus exakt H6/M2, keine Harnessfehler |
| Security Rev2 | `96/100`, `0C/0H/1M`, PASS |
| Offline-Urteil | `offline_hold_lifted=true` |

H6 ist durch einen opaken, klassenmarkierten Wrapper geschlossen. Das Original
bleibt identisch als `__cause__`; alle aktuellen Aufrufer behalten den
Rueckgabewert des Markerhelpers. M2 prueft die Kindgrenze je Iteration: Kind 257
loest fail-closed aus, Kind 258 wird nicht gelesen. Sync-/Async-Cleanup erfolgt
auch bei verweigerter Markerzuweisung exakt einmal.

## 3. Exakter Aenderungsscope

Produktionsdateien:

1. `openviking/utils/model_retry.py`;
2. `openviking/models/vlm/backends/openai_vlm.py`;
3. `openviking/models/vlm/base.py`;
4. `bot/vikingbot/providers/vlm_adapter.py`.

Testdateien:

1. `tests/unit/test_model_retry.py`;
2. `tests/unit/test_stream_config_vlm.py`;
3. `tests/unit/test_vikingbot_vlm_adapter_retry.py`.

Keine Aenderung an `VLMConfig`, Dependencies, Lockfiles, VolcEngine-
Konstruktoren oder globaler Codex-Konfiguration. Oeffentliche VLM-Signaturen und
Rueckgabetypen bleiben unveraendert.

## 4. Reproduzierte Offline-Evidenz

Supervisor und Worker reproduzierten:

```text
H6/M2 direct:              5 PASS
relevanter Drei-Datei-Satz: 189 PASS
finaler Sechs-Datei-Satz: 272 PASS
Responses + Hook:          122 PASS
breite 13-Datei-Matrix:    364 PASS + 8 FAIL
Skip/Xfail:                0
bekannte Warnungen:        4 Pydantic-Warnungen
Ruff / Format / py_compile / diff-check: PASS
Security Rev2:             96/100, 0C/0H/1M
Code Quality / API:        96/100
```

Die acht roten Breittests sind exakt die vorbestehenden
`tests/models/vlm/test_volcengine_cache.py`-Faelle. Alle scheitern an
`VolcEngineVLM.__init__() got an unexpected keyword argument 'model'`. Sie
wurden weder verschleiert noch in diesen Scope aufgenommen.

## 5. Reproduktionsbefehle

```bash
cd /Volumes/ExtremePro/projects/OpenViking-agent-worktrees/20260731-legacy-vlm-repair
git status --short --branch
git branch --show-current
git rev-parse HEAD
git diff --check

PYTHONPATH=.:bot:/tmp/openviking-codex-responses-test-deps-20260731 \
  /Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m pytest \
  -q -o addopts= \
  tests/unit/test_codex_vlm.py \
  tests/unit/test_kimi_glm_vlm.py \
  tests/unit/test_model_retry.py \
  tests/unit/test_stream_config_vlm.py \
  tests/unit/test_vikingbot_vlm_adapter_retry.py \
  tests/unit/test_vlm_failover.py

PYTHONPATH=.:bot:/tmp/openviking-codex-responses-test-deps-20260731 \
  /Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m pytest \
  -q -o addopts= \
  tests/unit/test_codex_compaction_hook.py \
  tests/unit/test_codex_responses_state.py \
  tests/unit/test_codex_vlm.py
```

Erwartung: `272 passed` beziehungsweise `122 passed`, jeweils vier bekannte
Warnungen und keine Skips/Xfails.

## 6. Live- und MCP-Grenze

Der User hat den Live-Provider-Test vertagt. Es gab keinen Provider-,
Capability- oder Canary-Request. Der spaetere Live-Pfad erfordert vor dem ersten
Request:

- ausdrueckliche User-Wiederaufnahme;
- exakten Allowlist-Origin `https://chatgpt.com/backend-api/codex`;
- genau einen Credential-Slot-Fingerprint;
- fixes Modell und fixe Capabilitymenge;
- numerische Request-, Output-Token-, Bildbyte- und Kostengrenzen;
- Provider-Retry `0` und Failover `0`.

Ein read-only OpenViking-MCP-Health-/Search-PASS ist nur Betriebszugriff. Er
beweist keine Codex-Responses-, Compaction- oder Replay-Capability.

## 7. Autorisierte und verbotene Aktionen

Autorisiert: gezielter Commit, Push und Aktualisierung des bestehenden
Draft-PRs nach finaler Scope-/Testpruefung.

Nicht autorisiert:

- Merge;
- Aktivierung oder Default-Promotion;
- Live-Provider-, Capability- oder Canary-Aufruf;
- Rechner-, Server-, Runtime-, Container-, Service- oder Prozess-Restart ohne
  ausdrueckliche User-Bestaetigung.

## 8. Sichere Fortsetzung

1. Identitaet und Dirty-State mit Abschnitt 5 read-only pruefen.
2. Den finalen Commit/PR-Head mit `git rev-parse HEAD` und `gh pr view 3667`
   vergleichen.
3. Bei der spaeteren Live-Wiederaufnahme zuerst H1 aus dem Open-Item-Bericht
   als neues, separates Gate behandeln.
4. Die acht VolcEngine-Fehler nur in einem eigenen Auftrag und isolierten Scope
   bearbeiten.
5. Bei unerwartetem Test-, Hash-, Scope- oder Security-Drift fail-loud HOLD.

## 9. Abschluss

Der **Offline Legacy-VLM HOLD ist aufgehoben**. Live M1, Canary, Aktivierung,
Promotion und Merge bleiben HOLD. Kein Restart wurde ausgefuehrt.
