# Evidence Dossier — Live-Gates und Lark-Upstream-Warnungen

**Stand:** 2026-08-02
**Workflow:** `$tccode` (`thorough`, `critical`) innerhalb Agent-Workflow-v4
**Arbeitsstand:** `agent-workflow/20260802-live-gates-execution`
**Fork:** `manni07/OpenViking`
**Live-Status:** `H1 PASS`; OpenClaw-disposable-Service/MCP `PASS`; H2, OpenClaw-P0 und Provider-/Feishu-Live offen

## Ergebnis

Die offline behebbaren WebSocket-Kompatibilitätsfehler sind geschlossen:
`lark-oapi 1.7.1`, `uvicorn 0.52.1` und `websockets 15.0.1` sind gelockt,
und die OpenViking-/VikingBot-Serverpfade wählen den SansIO-Adapter explizit.
Ein frischer Importtest bestätigt daneben genau zwei bekannte Warnungen aus
dem unveränderten Drittanbieterpaket. Sie werden weder global gefiltert noch in
`site-packages` gepatcht.

PR #8 im Fork wurde am 2026-08-02 als Merge-Commit
`373aa383511a62a8178208511c60b655ea406dfa` in `manni07/OpenViking:main`
übernommen. H1 wurde am 2026-08-02 in einem privaten OAuth-Pilotlauf gegen den
exakt freigegebenen Codex-Origin ausgeführt. H2, OpenClaw-P0/Service und
Provider-/Feishu-Live bleiben davon unabhängig offen.

Die separate OpenClaw-/MCP-Prüfung wurde am selben Tag in einem privaten
temporären State abgeschlossen: Plugin-Build und -Typecheck, frischer
Loopback-Gateway-Start, Plugin-Initialisierung, Gateway-Health und ein echter
MCP-Handshake mit read-only `health` sind PASS. Der temporäre Prozess wurde
sauber beendet; der bestehende OpenViking-Dienst und fremde Testprozesse wurden
nicht neu gestartet oder beendet. Die zuvor beobachteten fünf Plugin-Legacy-
fehler sind behoben; im vollständigen Repository-Baum bestehen `44 Test Files,
729 Tests` sowie Build/Typecheck. Offen bleibt nur der mutierende P0-Harness-
Aufruf selbst.

Der lokale Runner `/Volumes/ExtremePro/projects/local-ci-gate` meldet alle
fünf Checks `PASS`: Root `6167 passed, 246 skipped, 1` bekannter
Lark-Upstream-Warnung und Bot `271 passed, 2` bekannte Lark-Upstream-Warnungen.
Die Warnungsanzahl ist damit klassifiziert, nicht versteckt.

## Gate-Ledger

| Gate | Status | Fehlender Nachweis / sichere nächste Aktion |
|---|---|---|
| H1 Codex Capability | `PASS` | OAuth-Origin `https://chatgpt.com/backend-api/codex`, Modell `gpt-5.3-codex-spark`, `store=false`, `reasoning.effort=low`, Threshold `1000`; Compaction-Emission, vollständige Stream-Items, Replay und stateful Canary wurden in einem privaten temporären Lauf bestätigt. |
| H2 Responses Benchmark | `HOLD / NOT RUN` | Erst nach H1-PASS und separater Freigabe; 20 reale plus 10 synthetische Szenarien, Wiederholungen und Kosten-/Datengrenzen sind noch nicht freigegeben. |
| OpenClaw P0/Service | `PARTIAL PASS / P0 HOLD` | Disposable OpenClaw `2026.5.27`, Plugin `2026.6.18`, `44/729` Plugin-Tests, Loopback-Gateway `:18999`, Plugin-Health und MCP read-only sind PASS. Nicht ausgeführt ist nur der mutierende Agent-/P0-Harness mit freigegebenem Modell-/Kostenrahmen. |
| Provider-/Feishu-Live | `HOLD / NOT RUN` | Token-Art, exakte HTTPS-Domain/Fixture, App-Berechtigungen, Retention-/Verschlüsselungsentscheidung, Timeout-, Kosten- und Rollback-Grenzen fehlen. |

H2, OpenClaw-P0/Service und Provider-/Feishu-Live werden durch H1 nicht
freigegeben. Der OpenViking-Health-Endpunkt ist weiterhin nur ein lokaler
Liveness-Nachweis. Es gab keinen Neustart eines Dienstes, Servers oder Rechners.

## H1-Live-Evidenz

- Authentisierung: lokaler Codex-CLI-OAuth-Bootstrap in einem separaten
  `0700`-Tempverzeichnis; kein API-Key und keine Tokenwerte in Reports.
- Requests: `store=false`, keine Conversations, kein
  `previous_response_id`, kein Retry/Fallback innerhalb der Chain.
- Stream: `response.output_item.done` enthielt Compaction-, Reasoning- und
  Message-Items; `response.completed` wurde eindeutig erkannt.
- Replay: Das neueste Compaction-Fenster wurde mit einem neuen Turn-Delta
  erneut akzeptiert. Provider-only `created_by` wird nur für den Request
  entfernt; der caller-owned Zustand bleibt vollständig.
- Stateful Canary: veröffentlichter Zustand `generation=0`, `turn_count=1`;
  der sichtbare Text wurde nicht als Qualitätsnachweis gewertet. Diese
  Qualitäts-/Tokenbewertung gehört in H2.
- Regression: `tests/unit/test_codex_responses_state.py` — `77 passed`.

## OpenClaw-/MCP-Live-Evidenz

- Temporärer Root: `/tmp/openviking-openclaw-pilot-6zQ66v` (`0700`), keine
  Übernahme von `HOME`, `/app` oder Host-Daemon-State.
- Plugin `typecheck`/`build`: PASS. Vollständige Plugin-Suite im
  Repository-Baum: `44 Test Files, 729 Tests` PASS. Behoben wurden die
  veralteten Recall-Exports, die doppelte URI-Klassifikation, direkte Setup-
  Netzwerklogik und die doppelte ZIP-/Upload-I/O-Schicht.
- SHA-256: `dist/index.js`
  `4e7a89cecb33a227335c6493a0031b6e41cdaae9cf0a99d85d2aa976efcf3c34`,
  `dist/commands/setup.js`
  `4465b2b0317c0ecd2faef5d8559d699f8b807260de40db803c4c138d888a6e38`,
  `openclaw.plugin.json`
  `0d94af38d72502963a86a9f15dcd2c645ea0d8ba34a4de9906b11835fed912a8`,
  `package.json`
  `cbb50444613105ccbd0705f3fd54c3a696490d6fae8d93ca51e8b315a7a08028`.
- Gateway: frischer Prozess auf Loopback `127.0.0.1:18999`, `ready`, HTTP
  `/health` 200, danach sauber beendet.
- MCP: `initialize` 200 mit Session, `notifications/initialized` 202,
  `tools/list` 200 mit 16 Werkzeugen, `tools/call health` 200 mit
  `isError=false`. Keine mutierenden Werkzeuge und kein Provider-Call.

## Lark-Warning-Ledger

Die folgende Tabelle ist ein absichtlicher Maintenance-Restbefund, kein
lokaler Abnahmefehler:

| Signatur | Provenienz | Bewertung | Behebung/Exit-Kriterium |
|---|---|---|---|
| `datetime.datetime.utcfromtimestamp() is deprecated ...` | Vendorter Protobuf-Code unter `lark_oapi/ws/pb/google/protobuf/internal/well_known_types.py` (Import in `lark-oapi 1.7.1`) | Veraltet, aber nicht aus OpenViking-Datenpfaden; ein Upgrade der separaten Projekt-Abhängigkeit `protobuf` erreicht diesen eingebetteten Code nicht. | Auf eine verifizierte Lark-Version warten, die den vendorten Ausdruck ersetzt. Danach Lock-Hash, Import- und Protobuf-Regressionslauf aktualisieren. |
| `There is no current event loop` | Modul-Import `lark_oapi/ws/client.py`; der SDK-Client hält anschließend einen globalen Loop und wird im Feishu-Kanal aus einem separaten Thread gestartet. | Lifecycle-/Verfügbarkeitsrisiko, nicht nur Kosmetik. Ein vorab erzeugter Loop oder ein Warning-Filter würde die Ownership-/Cleanup-Frage verdecken. | Upstream muss Loop-Eigentum, Thread-Bindung und Stop/Cleanup explizit machen. Danach Sync-/Async-, Multi-Thread- und Cleanup-Tests ergänzen. |

Der Regressionstest
`tests/test_lark_websockets_compat.py::test_lark_upstream_warning_ledger_is_explicit`
importiert das SDK in einem frischen Subprozess und prüft die beiden
Signaturen samt Dateipfad. Ein neuer oder verschwundener Befund stoppt den
Dependency-Review, statt stillschweigend unterdrückt zu werden. Der Test
verändert weder Warning-Filter außerhalb seines lokalen Capture-Blocks noch
installierte Dateien.

## Freigabe-/Stop-Regeln

Für die noch offenen Gates darf die Ausführung erst beginnen, wenn die in
[`docs/plans/2026-08-01-live-gates-h1-h2-openclaw.md`](../plans/2026-08-01-live-gates-h1-h2-openclaw.md)
genannten Freigabefelder vollständig und schriftlich vorliegen. Fehlende
Origin-, OAuth-, Preis-, Deadline-, Retention- oder Prozessdaten bleiben
`HOLD`; es gibt keinen automatischen Fallback, Retry, Failover oder Restart.
