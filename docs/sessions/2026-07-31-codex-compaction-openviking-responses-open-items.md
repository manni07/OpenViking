# Open-Item-Bericht nach Offline-HOLD-Lift

**Stand:** 2026-07-31
**Status:** Offline Legacy-VLM HOLD aufgehoben; Live M1 und Promotion auf HOLD
**Session Transfer:**
[STP](2026-07-31-codex-compaction-openviking-responses-stp.md)

Dieser Bericht enthaelt exakt drei High-, drei Medium- und drei Low-Massnahmen.
Nach Security Rev2 bestehen **keine Critical- oder High-Security-Befunde**. Die
High-Punkte unten sind operative Freigabe- oder getrennte Legacy-Gates.

## High — 3 Massnahmen

| ID | Massnahme | Owner | Gate / Abschlusskriterium | Next command |
|---|---|---|---|---|
| H1 | Live-Provider-/Capability-Probe kontrolliert nachholen | `mcp_coordinator_agent`, `security_agent` | Nur nach ausdruecklicher User-Wiederaufnahme: exakter HTTPS-Origin, ein Credential-Slot, fixes Modell und harte Request-/Token-/Bild-/Kostenlimits; Retry und Failover `0` | Kein Live-Command; User hat den Live-Test vertagt |
| H2 | Canary, A/B-Corpus und Promotionsevidenz erheben | `simulation_agent`, `test_unit_agent` | 20 reale + 10 synthetische Szenarien; keine Qualitaetsverschlechterung, mindestens 20% weniger mediane Output-Tokens, p95 hoechstens 10% schlechter, keine hoehere Fehlerrate | Erst nach positivem H1-Live-Gate und separater Datenfreigabe |
| H3 | Acht VolcEngine-Konstruktor-Baselinefehler separat reparieren | `architecture_agent`, `test_unit_agent` | Eigenes Scope-Gate; `VolcEngineVLM`-Konstruktorvertrag eindeutig entscheiden; alle acht Tests gruen ohne Responses-/Legacy-VLM-Regression | Separaten Auftrag und eigenen Branch/Worktree verwenden |

## Medium — 3 Massnahmen

| ID | Massnahme | Owner | Gate / Abschlusskriterium | Next command |
|---|---|---|---|---|
| M1 | Draft-PR und CI fail-loud beobachten | `devops_agent` | Commit und Push vorhanden; Checks transparent; Draft bleibt ohne Merge/Aktivierung | `gh pr checks 3667` read-only |
| M2 | Vier bestehende Pydantic-Warnungen separat klassifizieren | `test_unit_agent` | Warnungen dokumentiert oder in eigenem Scope behoben; kein Umdeuten der gruene/roten Testevidenz | Spaeter denselben 272-Fall-Lauf mit Warning-Capture verwenden |
| M3 | Nahe Dateigroessengrenze des Streamtests abbauen | `code_quality_api_agent` | `test_stream_config_vlm.py` liegt deutlich unter 1000 Zeilen, ohne Testverlust oder Produktionsrefactor | Separater Test-only Refactor; aktuell 998 Zeilen |

## Low — 3 Massnahmen

| ID | Massnahme | Owner | Gate / Abschlusskriterium | Next command |
|---|---|---|---|---|
| L1 | Lower-Level-Traceback-Risiko des erhaltenen `__cause__` dokumentieren | `security_agent` | Feste Sinks bleiben redigiert; direkte Aufrufer loggen keine Providerexception ungefiltert | Read-only Sink-Audit bei naechster Security-Runde |
| L2 | Rueckgabevertrag des Markerhelpers gegen kuenftige Aufrufer absichern | `code_quality_api_agent` | Jeder Aufrufer behaelt das von `mark_vlm_error_non_retryable()` gelieferte Objekt | `rg -n "mark_vlm_error_non_retryable" openviking bot` plus Review |
| L3 | Exotische nicht markierbare Cancellation-Exception bewerten | `test_unit_agent` | Built-in Cancellation bleibt korrekt; Sonderfall erhaelt nur bei realem Providerbedarf einen Contract-Test | Kein Source-Change ohne reproduzierbaren Fall |

## Geschlossene Befunde

- H1: exakter Langfuse-Vertrag und optionale `response_id` — **CLOSED**.
- H6: Exception verweigert Markerzuweisung — **CLOSED** durch opaken,
  klassenmarkierten Wrapper mit Original als `__cause__`.
- M2: taeuschendes Aggregate-`len()` — **CLOSED**; Kind 257 loest
  fail-closed aus, Kind 258 wird nicht gelesen.
- Final Security Rev2: `96/100`, `0 Critical`, `0 High`, `1 Medium`, PASS.

## Verbindliche Stopregel

Der Offline-HOLD ist aufgehoben. Live-Aufrufe, Canary, Aktivierung,
Default-Promotion und Merge bleiben verboten, bis ihre eigenen Gates erfuellt
sind. Kein Rechner-, Server-, Runtime-, Container-, Service- oder
Prozess-Restart ohne ausdrueckliche User-Bestaetigung.
