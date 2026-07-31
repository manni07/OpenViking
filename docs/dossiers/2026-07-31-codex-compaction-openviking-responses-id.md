# Implementation Dossier

## Codex-Compaction und OpenViking Responses State

Stand: 2026-07-31
Status: Implementierter, offline verifizierter Kandidat; Live-Freigabe HOLD
Basis-Commit: `60ef45d4c3a7d07ceb1df4e9d7dde7a14449ac50`

## 1. Lieferergebnis

Der Worktree enthält einen minimal additiven Kandidaten:

- einen gehärteten Compaction-Hook unter
  `tools/codex_compaction_hooks/codex_compaction_hook.py`;
- einen aufruferverwalteten Responses-State-Adapter unter
  `openviking/models/vlm/backends/codex_responses_adapter.py`;
- additive State-Methoden und einen expliziten Capability-Probe in
  `openviking/models/vlm/backends/codex_vlm.py`;
- zwei opt-in Konfigurationsfelder in
  `openviking_cli/utils/config/vlm_config.py`;
- 102 neue Offline-Tests.

Es wurden keine globalen Codex-Dateien verändert, keine Funktion aktiviert und
kein Provider-Call, Restart, Push oder Merge ausgeführt. Die isolierte Branch
enthält die gezielten Implementierungs-Commits `a84a3730`, `325e5cff` und
`0556a9aa`.

## 2. Implementierungsentscheidungen

### 2.1 Hook

Der Hook schreibt nur private Korrelationsmetadaten. Jede Pfadkomponente von
`CODEX_HOME` bis zum Hook-State-Verzeichnis wird auf Symlinks geprüft.
Eigentümer, Typ und Rechte werden validiert; Dateien werden atomar mit `0600` in
einem `0700`-Verzeichnis veröffentlicht. Eingabe und Laufzeit sind begrenzt.
Prompts enthalten ausschließlich feste, kleine Hinweise.

Das Offline-Follow-up verankert alle Operationen an geöffneten Directory-FDs,
erzwingt die Fünf-Sekunden-Deadline über den gesamten Hook und begrenzt alte
Korrelationsmetadaten durch TTL-, Anzahl- und Scan-Limits.

### 2.2 Responses-State

Der State ist frozen, integritätsgeschützt und an Modell, Instructions, Origin,
Principal und Credential gebunden. Der Adapter übernimmt alle Output-Items
kanonisch, beschneidet nur vor dem neuesten Compaction-Item und veröffentlicht
einen Nachfolgestate ausschließlich nach `response.completed`.

Stateful Requests erzwingen `store=false` und `stream=true`. Conversations,
`previous_response_id`, Background und entsprechende `extra_body`-Umgehungen
werden abgelehnt. Sync und Async teilen denselben Zustandsvertrag.

### 2.3 Tool- und Ressourcenintegrität

Offene Tool-Call-IDs gehören zu genau einer Chain-Generation. Tool-Ausgaben
werden genau einmal angenommen. State-, Item-, Turn-, Bild-, Tool-Ausgabe-, TTL-
und Chain-Grenzen schlagen laut fehl. Opaque Daten sind von normaler
Repräsentation und Logging ausgeschlossen.

Revision 2 verhindert zusätzlich State-spezifische sichtbare/opaque Inhalte in
Traces, serialisiert die erstmalige Adapter-Initialisierung, hält
Credential-Datei-/Refresh-I/O vom Async-Event-Loop fern und begrenzt retained
Tool-Call-IDs auf 4096 beziehungsweise 512 Bytes je ID. Die IDs zählen zur
kanonischen State-Byte-Bilanz.

### 2.4 Capability und Pilot

Compaction ist nur opt-in und erfordert einen erfolgreichen Probe am tatsächlich
verwendeten Endpoint. Im Pilot gilt exakt ein `openai-codex`-Credential und für
OAuth ausschließlich `https://chatgpt.com/backend-api/codex`. Es gibt keinen
stillen Fallback und kein Failover innerhalb einer Chain.

## 3. Änderungsumfang

| Datei | Änderung |
|---|---|
| `codex_compaction_hook.py` | Gehärteter Hook-Kandidat |
| `codex_responses_adapter.py` | State, Reducer, Limits, Sync/Async Adapter |
| `codex_vlm.py` | Additive öffentliche Methoden und Probe |
| `vlm_config.py` | Opt-in State-/Threshold-Konfiguration |
| `test_codex_compaction_hook.py` | 30 Hook-Sicherheitsfälle |
| `test_codex_responses_state.py` | 72 State-/Adapterfälle |

`VLMBase` und andere Provider wurden nicht geändert.

## 4. Verifikation

| Prüfung | Ergebnis |
|---|---|
| Neue Suiten | 102/102 PASS |
| Core-Kombination | 131 PASS, 1 bestätigter Baseline-Fehler |
| Erweiterte Kombination | 140 PASS, 12 bestätigte Baseline-Fehler |
| Ruff Check / Format | PASS / PASS |
| Compileall | PASS |
| Diff-Check | PASS |
| MCP Health + read-only Suche | PASS |
| Globale Codex-Hashes | unverändert gegenüber Backup |

Der eine Core- und elf zusätzliche Stream-Config-Fehler reproduzieren auf dem
Basis-Checkout. Sie sind nicht durch diesen Kandidaten verursacht, bleiben aber
ein Legacy-Freigabe-HOLD.

## 5. Implementierungs-Selbstsimulation

Dies ist eine dossierbasierte Selbstprüfung, keine unabhängige Live-Evidenz.

| Kriterium | Wert | Begründung |
|---|---:|---|
| Korrektheit | 97 % | Verträge und Failure Paths durch Tests abgedeckt |
| Integration | 96 % | Additive Pfade, bestehender Default erhalten |
| Sicherheit | 97 % | Bindings, Limits, Hook-Pfad und Log-Sentinels |
| Testbarkeit | 98 % | 102 deterministische neue Tests |
| Performance | 92 % | Harte Limits; kein realer Long-Horizon-Benchmark |
| Wartbarkeit | 95 % | Provider-spezifisch, keine `VLMBase`-Ausweitung |
| Beobachtbarkeit | 94 % | Typisierte Fehler, absichtlich keine State-Logs |
| Rollback | 99 % | Opt-in und globale Dateien unverändert |
| **Aggregiert** | **96,0 %** | Mindestwert je Kriterium: 92 % |

Damit sind die geforderten 95 % aggregiert und 90 % je Einzelkriterium erreicht.
Der fehlende Live- und A/B-Nachweis bleibt dennoch HOLD.

### Security-Re-Review Revision 2

Keine offenen Critical-/High-Befunde; das Offline-Kandidaten-Veto ist aufgehoben.
Bewertung: 95,6 % aggregiert, mindestens 91 % je Kriterium. Das geforderte
aktuelle Claude Opus war nicht verfügbar, deshalb ist der Review mit Codex als
Ersatzmodell vorläufig. Die drei Medium-Restbefunde sind im Offline-Follow-up
`325e5cff3895036a2fc0e8a0a93131e77f7c9d0d` geschlossen und mit
`0556a9aac049d2563893e1abe4068c0260024542` um die Cancellation-Fehlerpriorität
ergänzt:

- stabile Credential-Slot-Bindung auch ohne `client_id`;
- abgeschirmtes Async-Cleanup trotz wiederholter Cancellation und Close-Fehlern;
- Directory-FD-verankerter Hook mit erzwungener Deadline und begrenzter
  Retention.

Die neuen Regressionstests sind Bestandteil der 102/102 bestandenen
Kandidatentests. Eine unabhängige Revalidierung vor Aktivierung bleibt offen.

## 6. Harte HOLDs

1. **A/B-Evidenz fehlt:** keine 20 sanitisierten realen Langsitzungen und 10
   synthetischen Multi-Turn-/Tool-Szenarien.
2. **Live-Capability fehlt:** Probe und Canary am exakten Codex-Endpunkt wurden
   nicht ausgeführt. Der Probe ist potenziell kostenpflichtig und erfordert
   ausdrückliche Genehmigung.
3. **Legacy nicht vollständig grün:** ein Codex-Config- und elf
   Stream-Config-Fehler sind vorbestehend, aber offen.
4. **Keine Aktivierung:** weder Hook noch State-Modus oder Threshold wurden
   global aktiviert; keine Default-Promotion.

## 7. Freigabeurteil

Der Code ist als **offline verifizierter Opt-in-Kandidat** übergabefähig. Er ist
nicht als live-capability-verifiziert, A/B-optimiert oder promotionsfähig zu
bezeichnen. Eine spätere Aktivierung benötigt einen gesonderten Evidenzreview und
ausdrückliche Autorisierung.

## 8. Artefakte

- [ARD](2026-07-31-codex-compaction-openviking-responses-ard.md)
- [TRD](2026-07-31-codex-compaction-openviking-responses-trd.md)
- [PD](../plan/2026-07-31-codex-compaction-openviking-responses-pd.md)
- [TD](../tests/2026-07-31-codex-compaction-openviking-responses-td.md)
- [Development Diary](../diaries/Development_Diary_v000.md)
- [Manual](../manuals/2026-07-31-codex-compaction-openviking-responses-manual.html)
- [Proposal Dossier](../vision/2026-07-31-codex-compaction-openviking-responses-ppd.md)
- [Open Items](../sessions/2026-07-31-codex-compaction-openviking-responses-open-items.md)
