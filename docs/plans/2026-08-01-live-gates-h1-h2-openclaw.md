# Plan — OpenClaw-P0, Codex-H1 und Codex-H2 (Live-Phase)

Status: **H1 PASS; OpenClaw-disposable-Service und MCP PASS; H2 / OpenClaw-P0 / Provider-Live weiterhin offen**
Stand: 2026-08-02
Ziel-Repository: `manni07/OpenViking`

Der aktuelle Evidence-Ledger steht in
[`docs/dossiers/2026-08-02-live-gates-and-lark-warning-ledger.md`](../dossiers/2026-08-02-live-gates-and-lark-warning-ledger.md).
Die noch benötigten H2/P0/Feishu-Felder stehen ausführbar in
[`docs/plans/2026-08-02-live-gate-inputs.md`](2026-08-02-live-gate-inputs.md).
Die Offline-WebSocket-Kompatibilität ist abgeschlossen; die beiden
Lark-Upstream-Warnungen bleiben separat dokumentiert und sind kein Anlass für
einen lokalen Filter oder einen `site-packages`-Patch.

## Zweck und harte Grenzen

Dieses Dokument beschreibt die separat freizugebende Live-Phase. Es aktiviert
keinen Provider, startet keinen Dienst und verwendet weder API-Key noch OAuth-
Credential ohne eine neue, explizite Lauf-Freigabe. Die Offline-Suite und die
Native-/Lifecycle-Nachweise sind davon unabhängig.

Die Live-Phase darf nur mit einem exakt benannten, temporären Arbeitsverzeichnis,
einem einzelnen freigegebenen `CodexVLM`-Pilotobjekt und einem einzelnen
Credential beginnen. Kein Account-/Provider-Failover, keine Conversations,
keine `previous_response_id` und kein automatisches Überspringen eines
fehlenden Capability-Features.

## Freigabe-Eingang (vor jedem Netzwerkzugriff)

1. Auftraggeber bestätigt schriftlich: Live-Phase starten, erlaubter Endpunkt,
   Modell, Zeitfenster, Kostenlimit und maximale Request-/Turn-Zahl.
2. OAuth- oder API-Key-Modus wird festgelegt. Für OAuth ist ausschließlich der
   bereits freigegebene HTTPS-Codex-Origin zulässig; benutzerdefinierte Origins
   und Redirects sind verboten. Tokenwerte werden nie in Logs, Reports oder
   Artefakten ausgegeben.
3. Der exakte Prozess/Container für OpenClaw wird identifiziert. Ein Neustart
   ist nur für diesen Prozess und nur nach Bestätigung zulässig; Rechner- oder
   fremder Dienst-Neustart bleibt ausgeschlossen.
4. Es wird ein frischer, privater, löschbarer State-/Artefaktpfad mit
   Eigentümer- und Modusprüfung eingerichtet. Vorheriger Zustand wird nicht
   überschrieben.
5. `git status`, Branch, Commit und SHA-256-Manifeste werden eingefroren.

Ohne diese Felder gibt es keinen Probe-Request. Insbesondere reichen ein
vorhandenes OAuth-Token, ein lokaler Health-Endpunkt oder ein erfolgreicher
Offline-Test nicht als implizite Freigabe. Für den H1-Pilot muss die
Approval-Datei außerdem vor dem Credential-Resolver und vor jeder Client- oder
Netzwerk-Factory strikt schema-validiert werden; unbekannte oder fehlende
Felder schlagen fail-closed fehl.

## Ausführungsprotokoll — 2026-08-02

Die aktuelle Ausführung wurde durch den Auftraggeber ausdrücklich gestartet.
Sie verwendete ausschließlich einen privaten, temporären OAuth-Arbeitsbereich;
der bestehende OpenViking-Dienst auf `127.0.0.1:1933` wurde weder
neugestartet noch beendet. Tokenwerte und opaque Response-Inhalte wurden nicht
in Artefakte oder Logs übernommen.

Für H1 wurden die tatsächlich vom ChatGPT-Codex-Account unterstützten
Parameter verwendet: Origin `https://chatgpt.com/backend-api/codex`, Modell
`gpt-5.3-codex-spark`, `store=false`, `reasoning.effort=low` und
`context_management.compact_threshold=1000`. Der zuvor verwendete Modellname
`gpt-5.3-codex` wurde vom OAuth-Endpunkt abgewiesen; Werte unter 1000 wurden als
ungültig abgewiesen. Diese Antworten sind account-/endpoint-spezifische
Live-Evidenz und keine globale Default-Änderung.

**H1-Ergebnis: PASS.** Der Probe-Request erzeugte verschlüsselte
`response.output_item.done`-Items für Compaction und Reasoning, anschließend
ein Message-Item und `response.completed`. Ein zweiter Request replayte das
neueste Compaction-Fenster erfolgreich. Ein zusätzlicher stateful Canary-Turn
veröffentlichte einen neuen Zustand (`generation=0`, `turn_count=1`) ohne
Server-Conversation oder `previous_response_id`.

Die Behebung umfasste den gemeinsamen Sync-/Async-Stream-Reducer sowie die
Replay-Normalisierung von provider-only `created_by`-Feldern. Opaque Items
bleiben im caller-owned Zustand vollständig erhalten; nur nicht zulässige
Response-Metadaten werden für den nächsten Input entfernt. Die Offline-
Regressionen hierfür bestehen mit `77 passed`.

H1-PASS schließt keine Qualitäts- oder Kostenfreigabe für H2 ein. H2 bleibt bis
zum kontrollierten Benchmark mit dem im nächsten Abschnitt beschriebenen
Corpus und den harten Request-/TTL-/Kostenlimits offen.

## Ausführungsprotokoll — OpenClaw und MCP, 2026-08-02

Die OpenClaw-Prüfung lief ausschließlich in einem privaten, temporären
Arbeitsbereich unter `/tmp/openviking-openclaw-pilot-6zQ66v` (Verzeichnisse
`0700`, keine Host-Konfiguration). Verwendet wurde die mit Node `v24.11.0`
kompatible, gepinnte CLI `openclaw 2026.5.27`; ein Upgrade auf die aktuellere,
mit diesem Node nicht kompatible Version wurde nicht versucht.

- Plugin `openviking 2026.6.18`: `typecheck` und `build` PASS.
- Plugin-Linkinstallation, `setup --json` und `status --json` PASS; der
  lokale OpenViking-Health-/User-Key-Probe meldete kompatibel auf `v0.4.11`.
- Ein frischer Gateway-Prozess wurde nur temporär auf Loopback `127.0.0.1:18999`
  mit Ephemeral-Token gestartet. Er meldete `ready`, initialisierte das Plugin
  und `/health` antwortete HTTP 200. Der Prozess wurde anschließend sauber per
  SIGINT beendet; der bestehende Dienst auf `127.0.0.1:1933` blieb unangetastet.
- Die Legacy-Brüche wurden behoben: Recall-Kompatibilitätsfunktionen liegen
  nur noch in der Registry, URI-Klassifikation nur noch im Routing, Setup-
  Netzwerkzugriff nur noch im Probe-Service und ZIP-/Upload-I/O nur noch im
  Resource-Packager. Im vollständigen temporären Repository-Baum sind damit
  `44 Test Files, 729 Tests` PASS; `typecheck` und `build` sind ebenfalls PASS.
- Die Manifestprüfung wurde im vollständigen Baum mit dem Repository-Icon
  wiederholt. SHA-256 der gebauten Pilot-Artefakte: `dist/index.js`
  `4e7a89cecb33a227335c6493a0031b6e41cdaae9cf0a99d85d2aa976efcf3c34`,
  `dist/commands/setup.js`
  `4465b2b0317c0ecd2faef5d8559d699f8b807260de40db803c4c138d888a6e38`,
  `openclaw.plugin.json`
  `0d94af38d72502963a86a9f15dcd2c645ea0d8ba34a4de9906b11835fed912a8`,
  `package.json`
  `cbb50444613105ccbd0705f3fd54c3a696490d6fae8d93ca51e8b315a7a08028`.

Der echte MCP-Transportnachweis gegen `http://127.0.0.1:1933/mcp` ist
vollständig:

| Schritt | Ergebnis |
|---|---|
| `initialize` | HTTP 200, `text/event-stream`, Session-ID ausgestellt |
| `notifications/initialized` | HTTP 202 |
| `tools/list` | HTTP 200, 16 Werkzeuge, `health` vorhanden |
| `tools/call health` | HTTP 200, ein Content-Block, `isError=false` |

Es wurden keine mutierenden OpenClaw-/MCP-Werkzeuge, kein Provider-Agent-Call,
kein `reset`, `install`, `restart`, `--force` oder Host-Service-Aufruf
verwendet. Für den vollständigen OpenClaw-P0-Lauf fehlt weiterhin ausschließlich
der explizit mutierende Agent-/Harness-Lauf mit einem freigegebenen Modell- und
Kostenrahmen; die disposable Service-/Plugin-/MCP-Kette ist reproduzierbar PASS.

## H1 — Capability-Probe

### Vorbereitung

- Gegen den exakt verwendeten Codex-Endpunkt wird ein einzelner Probe-Request
  mit `store=false` und der vorgesehenen `responses_compact_threshold`
  ausgeführt.
- Geprüft werden ausschließlich die tatsächlich benötigten Fähigkeiten:
  `context_management`, Compaction-Items, vollständige `response.output`-
  Weitergabe (Reasoning/Tool/Compaction) und Replay des nächsten Turn-Deltas.
- Die Probe verwendet keine produktiven Conversations und keine
  `previous_response_id`.

### PASS-Kriterien

- Endpunkt akzeptiert alle benötigten Felder ohne stillen Fallback.
- `response.completed` ist eindeutig korrelierbar; Teilstream, Timeout,
  Cancellation und HTTP-Fehler veröffentlichen keinen neuen Zustand.
- Neuester Compaction-Item beschneidet ausschließlich den davor liegenden
  Kontext; spätere Items bleiben byte-/item-getreu erhalten.
- State-Grenzen (Bytes, Items, Turns, Bilder, Tool-Ausgaben, TTL) und
  Credential-/Generation-Bindung werden vor dem Netzwerkzugriff geprüft.

### HOLD-Kriterien

Unsupported-Feature, abweichender Origin, Redirect, fehlendes `store=false`,
unklare Replay-Semantik, Leak in Log/Trace oder irgendein stiller Fallback.

## H2 — kontrollierter Benchmark

H2 startet erst nach H1-PASS und einer erneuten Freigabe. Die Matrix bleibt
identisch und reproduzierbar:

- mindestens 20 sanitierte reale Langsitzungen;
- mindestens 10 synthetische Multi-Turn-/Tool-Szenarien;
- nichtdeterministische Szenarien dreimal;
- Baseline `206720`, `scope=total` gegen die gehärteten Hooks und die Kandidaten
  `206720/total`, `200000/total`, `200000/body_after_prefix`;
- keine 175k-Variante ohne belegten Bedarf.

Erfasst werden Kontinuität, Output-Tokens, p95-Latenz, Fehlerrate,
Compaction-Häufigkeit, Hook-Laufzeit, State-Größe und Cross-Chain-Leaks.

### Promotion-Gate

Der Zustand bleibt opt-in, sofern nicht alle Kriterien erfüllt sind: keine
Qualitäts- oder kritische Szenarioeinbuße, mindestens 20 Prozent weniger
mediane Output-Tokens, p95 höchstens 10 Prozent schlechter, keine höhere
Fehlerrate, null Cross-Chain-Leaks und 100 Prozent der kritischen Security-,
Kontinuitäts- und Legacy-Tests. Bei einem einzigen Fehlkriterium erfolgt kein
Default-Rollout.

## OpenClaw-P0-/Service-Lauf

1. Vorab aktuellen Status, Port/Origin, PID/Container und Health read-only
   erfassen; kein altes Upgrade-/Reset-/Pkill-Skript verwenden.
2. Vor dem Handshake eine disposable OpenClaw-Home-/Config- und
   OpenViking-Workspace-Bindung belegen. Host-Home, feste `/app`-/1933-/18789-
   Annahmen und der nicht versionierte Harness-`settings.py`-Pfad dürfen nicht
   verwendet werden.
3. Mit temporären Settings einen echten MCP-Handshake und genau einen
   read-only Tool-Aufruf ausführen. Ein Health-Endpunkt allein ist kein
   Handshake-Nachweis.
4. P0-Harness im eigenen Environment ausführen; Nachrichten, Responses,
   Secrets und Prompt-Inhalte bleiben aus Logs/Artefakten redigiert und
   begrenzt. Der aktuelle Harness ist mutierend, solange diese Isolation nicht
   bewiesen ist.
5. Bei 503 der Embedding-Abhängigkeit, fehlendem Handshake, stale Harness,
   rohen Sentinel-Secrets oder ungeklärter Prozessidentität sofort HOLD. Kein
   automatischer Restart.

## Beweispaket und Stop-Regeln

Das Live-Beweispaket enthält nur sanitierte JSON-/Markdown-Berichte:

- Start-/Endzeit, Commit, Endpunktkennung ohne Token, Modell und Modus;
- H1-Probeantworten/Capability-Matrix;
- H2-Rohmetriken, Median/p95 und Vergleichsmatrix;
- OpenClaw-Handshake-/P0-Ergebnis;
- SHA-256-Manifeste, Testkommandos und PASS/FAIL/HOLD/NOT_RUN-Ledger.

STOP bei Credential- oder Prompt-Leak, unerwarteter Speicherung, fremdem
Prozess, fehlender Deadline, unbounded Retention, Cross-Chain-Datenübertritt,
unklarem Generation-Stand oder Kostenüberschreitung. Danach vorherigen
Zustand unverändert lassen und den Gate-Status als HOLD dokumentieren.

## Abschluss

Nach dem Live-Lauf werden STP, Development Diary, Manual, Proposal Dossier und
Open-Item-Bericht aktualisiert. Ein daraus entstehender Änderungs-PR bleibt
Draft, bis Review und alle Gates belegt sind; Aktivierung erfolgt nicht
automatisch.

Nach der Ausführung sind H1 sowie der disposable OpenClaw-Service/MCP-
Nachweis abgeschlossen. Der mutierende OpenClaw-P0-Harness, H2 und
Provider-/Feishu-Live bleiben separat offen, bis ihre jeweiligen Artefakte und
Stop-Kriterien erfüllt sind; sie werden nicht durch H1 oder den lokalen
Health-Check automatisch freigegeben.
