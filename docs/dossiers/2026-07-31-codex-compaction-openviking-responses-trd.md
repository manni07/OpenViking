# Technical Requirement Dossier

## Codex Responses State und Compaction

Stand: 2026-07-31
Status: Implementierter Kandidat; offline verifiziert; Live-Gates auf HOLD

## 1. Technischer Vertrag

Die Änderung ist additiv. `VLMBase`, andere Provider sowie die bestehenden
zustandslosen `create()`- und `get_completion()`-Pfade bleiben unverändert.

### 1.1 State

`CodexResponsesState` ist unveränderlich und aufruferverwaltet. Er enthält:

- Chain-ID und Generation;
- Modell und Instructions-Digest;
- Origin sowie Principal-/Credential-Fingerprint;
- Ablaufzeit;
- kanonische Responses-Items;
- offene und bereits verwendete Tool-Call-IDs;
- Turn-, Bild- und Tool-Ausgabe-Zähler;
- Integritätstag.

Ein expliziter Fork ist nur ohne offene Tool-Calls erlaubt. Stale Generation,
Binding-Wechsel, Replay, Manipulation oder Ablauf schlagen vor dem
Netzwerkzugriff fehl, soweit die jeweilige Prüfung lokal entscheidbar ist.

### 1.2 Request

Für jeden zustandsbehafteten Request gelten:

```text
store = false
stream = true
conversation = verboten
previous_response_id = verboten
background = verboten
```

Die Regeln gelten auch für `extra_body`. Bei vorhandenem State akzeptiert die
API nur neue Turn-Deltas. Das vollständige, kanonische Ledger wird vom Adapter
zusammengesetzt.

### 1.3 Response und Commit

- Sämtliche `response.output`-Items werden strukturerhaltend übernommen.
- Reasoning-, Tool- und Compaction-Items werden nicht semantisch reduziert.
- Nur der Abschnitt vor dem neuesten gültigen Compaction-Item wird entfernt.
- Ein neuer State wird ausschließlich nach `response.completed` veröffentlicht.
- Fehler, Timeout, Cancellation und Teil-Stream geben keinen Kandidaten-State
  frei.
- Nach dem ersten Stream-Ereignis gibt es keinen automatischen Retry.
- Async verwendet natives, cancellation-sicheres `async for`.

### 1.4 Tool-Calls

Eine Tool-Ausgabe wird nur akzeptiert, wenn:

1. die Call-ID offen ist;
2. Chain und Generation aktuell sind;
3. die Call-ID noch nicht verbraucht wurde;
4. Einzel- und Gesamtgrößenlimits eingehalten werden.

Die Ausgabe schließt die offene ID genau einmal.

## 2. Capability und Credential

`responses_compact_threshold` ist optional und nur mit aktiviertem State-Modus
zulässig. Vor der Verwendung ist ein erfolgreicher Capability-Probe für den
tatsächlich verwendeten Codex-Endpunkt erforderlich. Unsupported Features führen
zu einem expliziten Fehler, nicht zu einem Legacy-Fallback.

Im Pilot gilt:

- exakt ein `openai-codex`-Credential;
- kein Credential-/Account-/Provider-Failover innerhalb der Chain;
- OAuth ausschließlich zu
  `https://chatgpt.com/backend-api/codex`;
- keine benutzerdefinierten OAuth-Origins.

Der Probe wurde nicht live ausgeführt. Er ist potenziell kostenpflichtig und darf
erst nach ausdrücklicher Genehmigung erfolgen.

## 3. Konfiguration

```yaml
vlm:
  provider: openai-codex
  responses_state_enabled: false
  responses_compact_threshold: null
```

Die Defaults ändern das bestehende Verhalten nicht. Für einen später genehmigten
Pilot wären `responses_state_enabled: true`, ein positiver Threshold und genau ein
Credential erforderlich. Diese Dokumentation aktiviert nichts.

## 4. Hook-Vertrag

Der quellkontrollierte Hook-Kandidat:

- liest höchstens 64 KiB Eingabe;
- besitzt eine interne Laufzeitgrenze von fünf Sekunden;
- schreibt ausschließlich in ein privates, eigentümergeprüftes Verzeichnis;
- erzwingt `0700`/`0600`;
- verweigert Symlinks in jeder Pfadkomponente von `CODEX_HOME` bis zum
  State-Verzeichnis sowie unsichere Ziele;
- aktualisiert atomar;
- injiziert nur konstante, kleine Hinweise;
- korreliert PreCompact, Compact-SessionStart und PostCompact über Metadaten.

Es werden keine Transcript-Inhalte, Repository-Namen, Pfade, Dateinamen oder
Git-Metadaten in den Prompt übernommen. Der Kandidat wurde nicht in
`~/.codex/config.toml`, `~/.codex/hooks.json` oder den globalen Hook-Pfad
installiert.

## 5. Fehler- und Limitmodell

Eigene Fehlertypen unterscheiden Validierung, Ablauf, Generation, Binding,
Tool-Integrität, Limits, Capability, Concurrency und Transport. Default-Limits:

| Ressource | Grenze |
|---|---:|
| State | 32 MiB |
| Items | 4096 |
| Turns | 256 |
| Bilder | 8 |
| Bild | 8 MiB |
| Tool-Ausgabe einzeln / gesamt | 1 MiB / 4 MiB |
| Retained Tool-Call-IDs | 4096 |
| Tool-Call-ID | 512 Bytes |
| TTL | 3600 s |
| Chains | 16 |

Opaque State-Daten dürfen nicht in Logs, Traces, Dossiers oder Telemetrie
ausgegeben werden. Tests verwenden Sentinel-Secrets zur Prüfung. Gesehene
Tool-Call-IDs zählen zur kanonischen State-Byte-Grenze.

## 6. Erfüllungsmatrix

| Anforderung | Implementierung | Evidenz |
|---|---|---|
| Additive API | Adapter und `CodexVLM` | Neue Tests PASS |
| Immutabler State | Frozen Dataclasses plus Integrität | Neue Tests PASS |
| Delta-only | Request-Validierung | Contract-Tests PASS |
| `store=false` | Zwang und Escape-Hatch-Prüfung | Contract-Tests PASS |
| Lossless Items | Kanonischer Reducer | Reasoning/Tool/Compaction PASS |
| Commit-on-complete | Stream-State-Maschine | Timeout/Partial/Cancel PASS |
| Native Async | Async-Adapter | Sync/Async-Parität PASS |
| Tool exactly once | Open-/Seen-ID-Vertrag | Replay-Tests PASS |
| Limits/TTL/Chains | Lokale Guards | Boundary-Tests PASS |
| Hook-Härtung | Quellkontrolliertes Tool | 30 Hook-Tests PASS |
| Legacy default | Opt-in Config | Core bis auf Baseline-Fehler |
| Live Capability | Expliziter Probe | **HOLD: nicht genehmigt/ausgeführt** |

## 7. Verification Baseline

```text
Neue Suiten:       102 passed
Core kombiniert:  131 passed, 1 failed (132 collected)
Erweitert:         140 passed, 12 failed (152 collected)
Ruff check:        PASS
Ruff format:       PASS
compileall:        PASS
git diff --check:  PASS
```

Der Core-Fehler und elf zusätzliche Stream-Config-Fehler reproduzieren auf dem
unveränderten Basis-Checkout. Deshalb sind sie keine neu eingeführten
Regressionen, verhindern aber eine Aussage „Legacy vollständig grün“.

## 8. Freigaberegel

Live-Promotion bleibt HOLD, bis:

1. 20 reale sanitierte und 10 synthetische Long-Horizon-Szenarien ausgewertet
   sind;
2. Capability-Probe und Canary nach Genehmigung am exakten Endpoint bestehen;
3. Qualität nicht sinkt, mediane Output-Tokens mindestens 20 % fallen,
   p95-Latenz höchstens 10 % steigt, Fehlerrate nicht steigt und Cross-Chain-Leaks
   null bleiben;
4. alle kritischen Security-, Kontinuitäts- und Legacy-Gates bestehen.

Kein Restart und keine Aktivierung sind Bestandteil dieses Kandidaten.

Der Security-Re-Review Revision 2 meldet keine offenen Critical-/High-Befunde
und hebt das Offline-Kandidaten-Veto auf. Er bewertete den Kandidaten mit 95,6 %
aggregiert und mindestens 91 % je Kriterium. Die Bewertung ist vorläufig, weil
das geforderte aktuelle Claude Opus nicht verfügbar war und Codex als
Ersatzmodell eingesetzt wurde.

Die drei Medium-Restbefunde aus diesem Review wurden anschließend offline
geschlossen: eine stabile Credential-Slot-Bindung funktioniert auch ohne
`client_id`, Async-Ressourcen werden trotz wiederholter Cancellation vollständig
geschlossen, und der Hook verwendet Directory-FD-Verankerung, eine erzwungene
Deadline sowie begrenzte Retention. Evidenz: Follow-up-Commit
`325e5cff3895036a2fc0e8a0a93131e77f7c9d0d`, ergänzende
Cancellation-Fehlerpriorität in `0556a9aac049d2563893e1abe4068c0260024542`
und 102/102 Kandidatentests.

## 9. Artefakte

- [ARD](2026-07-31-codex-compaction-openviking-responses-ard.md)
- [Implementation Dossier](2026-07-31-codex-compaction-openviking-responses-id.md)
- [Test Dossier](../tests/2026-07-31-codex-compaction-openviking-responses-td.md)
- [Manual](../manuals/2026-07-31-codex-compaction-openviking-responses-manual.html)
