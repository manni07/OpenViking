# Open-Item-Bericht: finaler Legacy-VLM-HOLD

**Stand:** 2026-07-31
**Status:** Security Revision 3 VETO; kein Source-Unlock
**Session Transfer:**
[STP](2026-07-31-codex-compaction-openviking-responses-stp.md)

Dieser Bericht enthaelt exakt drei High-, drei Medium- und drei Low-Massnahmen.
Nur H1 ist ein aktueller Security-High-Befund. H2 und H3 sind operative
High-Prioritaets-Gates und keine zusaetzlichen Security-High-Befunde.

## High — 3 Massnahmen

| ID | Massnahme | Owner | Gate / Abschlusskriterium | Next command |
|---|---|---|---|---|
| H1 | Exakten nativen Stream-Langfuse-Testvertrag ergaenzen | `test_unit_agent`, danach `security_agent` | Erst nach neuer User-Autorisierung: fixes `output`, fixes `metadata.error`, keine weiteren Keys ausser optionaler `response_id`, eigene response-id-only-Variante; neues Security-Urteil `>=90`, `0C/0H` | Zunaechst kein Command; User-Autorisierung einholen, danach gezielten Testknoten aus `tests/unit/test_vikingbot_vlm_adapter_retry.py` ausfuehren |
| H2 | Sourcepfad weiter gesperrt halten und nur durch neues Security-Gate oeffnen | `master_orchestrator` und `security_agent` | Security Revision 3 bleibt autoritativ `89/100`, `0C/1H/1M`; kein Source-Writer vor geschlossenem H1 und neuem `>=90`, `0C/0H` | `git status --short --branch` und `git diff --name-only` read-only pruefen |
| H3 | Live-Provider-/Capability-/Canary-Gate getrennt wiederaufnehmen | `mcp_coordinator_agent` und `devops_agent` | Nur nach expliziter User-Wiederaufnahme: exakter HTTPS-Origin, ein Credential-Slot-Fingerprint, fixes Modell/Vision/Capabilities, numerische Request-/Token-/Bild-/Kostenlimits, Retry/Failover `0` | Kein Live-Command vor positivem lokalen Evidence Record |

## Medium — 3 Massnahmen

| ID | Massnahme | Owner | Gate / Abschlusskriterium | Next command |
|---|---|---|---|---|
| M1 | Finale sechs-Datei-Evidenz nach einer autorisierten H1-Korrektur reproduzieren | `test_unit_agent` | Collection bleibt erklaert; keine Errors/Skips/Xfails; RED wird nur nach Source-Unlock zu GREEN gefuehrt | Sechs-Datei-Collect-/RED-Befehle aus STP Abschnitt 7.3 |
| M2 | MCP-Freshness nur bei Bedarf read-only erneuern | `mcp_coordinator_agent` | Health exakt erfolgreich und `search_experience(..., limit=1)` liefert einen kontrollierten read-only Pfad; null Write/Restart | Erst bei Wiederaufnahme denselben read-only Health-/Search-Pfad verwenden |
| M3 | Autorisierten HOLD-Draft-PR beobachten und fail-closed halten | `devops_agent` | Scope geprueft; HOLD-Evidenz committed und gepusht; Draft-PR bleibt ohne Merge/Activation; CI-Ergebnis wird nicht als Source-Unlock umgedeutet | Nach PR-Erstellung nur Status/Checks read-only pruefen; kein Merge |

## Low — 3 Massnahmen

| ID | Massnahme | Owner | Gate / Abschlusskriterium | Next command |
|---|---|---|---|---|
| L1 | Vier bestehende Pydantic-Warnungen separat klassifizieren | `test_unit_agent` | Warnungen ohne Scope-Mischung dokumentiert oder beseitigt; Security-/RED-Ergebnis nicht umetikettiert | Spaeter gezielten Lauf mit unveraendertem Warning-Capture verwenden |
| L2 | Historische Rev2-PASS-/Unlock-Aussagen in weiteren Artefakten erst nach neuem Gate bereinigen | `documentation_agent` | Alle oeffentlichen Statusangaben nennen Rev3-VETO und verweisen auf das aktuelle STP; keine falsche Clearance | `rg -n "Revision 2|Source-Unlock|VETO" docs` read-only |
| L3 | Inhaltsfreie Diagnostik fuer kuenftige Gatefehler pruefen | `code_quality_api_agent` | Keine Prompt-, Credential-, Tool-, State- oder Exceptioninhalte in Logs/Traces; nur feste Kategorien | Kein Source-Command vor Source-Unlock |

## Verbindliche Stopregel

Keine weitere Test-/Designrevision und keine Sourceaenderung in diesem Lauf.
Keine Live-Calls, kein Merge, keine Aktivierung oder Promotion. Kein Restart
ohne ausdrueckliche Bestaetigung. Eine Wiederaufnahme des Sourcepfads braucht
neue User-Autorisierung, den korrigierten H1-Testvertrag und ein neues
Security-Urteil von mindestens `90/100` bei `0 Critical` und `0 High`.

Der aktuelle MCP-Nachweis ist nur ein enger dokumentierter read-only PASS:
`OpenViking is healthy (service initialized, storage: VikingFS)` und genau ein
Ergebnis aus `search_experience(..., limit=1)`, ohne Write oder Restart. Er ist
kein Codex-Capability- oder Canary-Nachweis.
