# Architecture Requirement Dossier

## Codex-Compaction und OpenViking Responses State

Stand: 2026-07-31
Status: Implementierter, offline verifizierter Kandidat; Aktivierung und Live-Promotion auf HOLD
Basis: `60ef45d4c3a7d07ceb1df4e9d7dde7a14449ac50`

## 1. Ergebnis

Der Kandidat trennt zwei unabhängige Sicherheitsgrenzen:

1. Ein gehärteter, quellkontrollierter Codex-Compaction-Hook wurde unter
   `tools/codex_compaction_hooks/` implementiert. Er ist **nicht** in der globalen
   Codex-Konfiguration installiert.
2. `CodexVLM` besitzt einen additiven, opt-in Responses-State-Pfad. Bestehende
   `create()`- und `get_completion()`-Aufrufe bleiben zustandslos.

Die Architektur ist fail-closed: State-Bindings, Generation, Ablauf, Limits,
Tool-Call-Integrität und Capability werden vor oder während des Requests geprüft.
Ein State wird erst nach einem vollständigen `response.completed` veröffentlicht.

## 2. Architekturgrenzen

| Bereich | Implementierter Kandidat | Bewusst ausgeschlossen |
|---|---|---|
| Hook | Private Metadaten, feste Ausgabe, atomare Datei, Korrelation | Globale Installation oder Aktivierung |
| Responses | Aufruferverwalteter, unveränderlicher State | Conversations und `previous_response_id` |
| Speicherung | Jede zustandsbehaftete Anfrage erzwingt `store=false` | Zusage vollständiger Provider-Zero-Retention |
| Provider | Eine `CodexVLM`-Instanz und genau ein Credential | Account-/Provider-Failover innerhalb einer Chain |
| OAuth | Nur `https://chatgpt.com/backend-api/codex` | Benutzerdefinierte OAuth-Origins |
| Compaction | Opt-in Threshold nach erfolgreichem Capability-Probe | Stiller Fallback bei fehlender Capability |
| Kompatibilität | Additive Methoden; `VLMBase` unverändert | Änderung anderer Provider |

## 3. Komponenten

### 3.1 Gehärteter Hook

`tools/codex_compaction_hooks/codex_compaction_hook.py` implementiert:

- private Ablage unter dem Codex-Zustandsverzeichnis mit `0700` für das
  Verzeichnis und `0600` für Dateien;
- Eigentümer-, Zielverzeichnis- und Symlink-Prüfungen für jede Komponente von
  `CODEX_HOME` bis zum State-Verzeichnis;
- atomaren Austausch einer sicheren Temp-Datei;
- maximal 64 KiB Eingabe und fünf Sekunden interne Laufzeitgrenze;
- keine Repository-, Transcript-, Pfad- oder Dateinamen in der injizierten
  Ausgabe;
- feste kleine Hinweise für PreCompact und `SessionStart(source=compact)`;
- PostCompact-Korrelation und Invariantenprüfung statt behaupteter semantischer
  Vollständigkeit.

Der kritische Pfad liest weder ein vollständiges Transcript noch Git-Metadaten.

### 3.2 Responses-State

`openviking/models/vlm/backends/codex_responses_adapter.py` enthält:

- den eingefrorenen `CodexResponsesState`;
- den eingefrorenen Ergebniscontainer `CodexResponsesTurn[T]`;
- Sync-/Async-Adapter;
- kanonische, verlustfreie Übernahme sämtlicher `response.output`-Items;
- Beschneidung ausschließlich vor dem neuesten gültigen Compaction-Item;
- State-Integrität, TTL, Ressourcenlimits und Chain-Concurrency;
- Tool-Ausgabe genau einmal für eine offene Call-ID der aktuellen Generation;
- native Async-Iteration und commit-on-complete.

Der State bindet Chain-ID, Generation, Modell, Instructions-Digest, Origin,
Principal-/Credential-Fingerprint, Ablaufzeit, Items und offene Tool-Calls.
Opaque Felder sind nicht Bestandteil normaler Repräsentationen oder Logs.

### 3.3 `CodexVLM` und Konfiguration

`openviking/models/vlm/backends/codex_vlm.py` stellt additive
`get_completion_with_state()`-Pfade und den expliziten
`probe_responses_compaction_capability()` bereit.

`openviking_cli/utils/config/vlm_config.py` führt zwei opt-in Einstellungen ein:

- `responses_state_enabled: false`
- `responses_compact_threshold: null`

Ein Threshold ohne State-Modus ist ungültig. Der State-Modus verlangt exakt ein
`openai-codex`-Credential. Dadurch bleibt der Legacy-Pfad Default.

## 4. Sicherheitsinvarianten

1. Stateful Requests enthalten `store=false` und `stream=true`.
2. `conversation`, `previous_response_id`, `background` und Escape-Hatches über
   `extra_body` werden abgelehnt.
3. Modell, Instructions, Origin, Principal, Credential und Generation können
   innerhalb einer Chain nicht unbemerkt wechseln.
4. Timeout, Fehler, Cancellation oder Teil-Stream mutieren den alten State nicht.
5. Nach dem ersten Stream-Ereignis erfolgt kein automatischer Retry.
6. Tool-Ausgaben werden nur für offene IDs, genau einmal und innerhalb der
   aktuellen Generation angenommen.
7. Der Capability-Probe hat keinen stillen Fallback.
8. OAuth wird im State-Modus ausschließlich an den freigegebenen HTTPS-Origin
   gesendet.
9. State-Inhalte erscheinen standardmäßig weder in Logs noch Telemetrie.

`store=false` verhindert die reguläre gespeicherte Response, ist aber keine
Garantie vollständiger Provider-Zero-Retention. Maßgeblich bleiben die offiziellen
Dokumente zu [Conversation State](https://developers.openai.com/api/docs/guides/conversation-state)
und [Compaction](https://developers.openai.com/api/docs/guides/compaction).

## 5. Harte Limits

| Limit | Default |
|---|---:|
| State | 32 MiB |
| Items | 4096 |
| Turns | 256 |
| Bilder | 8 |
| Bytes je Bild | 8 MiB |
| Bytes je Tool-Ausgabe | 1 MiB |
| Tool-Ausgaben gesamt | 4 MiB |
| Retained Tool-Call-IDs | 4096 |
| Bytes je Tool-Call-ID | 512 |
| TTL | 3600 s |
| Gleichzeitige Chains | 16 |

Überschreitungen schlagen explizit fehl. Bereits gesehene Call-IDs werden in die
kanonische State-Byte-Bilanz einbezogen.

## 6. Verifikation

| Evidenz | Ergebnis |
|---|---|
| Neue Hook- und State-Suiten | 92 bestanden, 0 fehlgeschlagen |
| Core-Kombination | 122 gesammelt, 121 bestanden, 1 bestätigter Baseline-Fehler |
| Erweiterte Kombination | 142 gesammelt, 130 bestanden, 12 bestätigte Baseline-Fehler |
| Ruff Check | PASS |
| Ruff Format Check | 6 Dateien formatiert |
| Compileall | PASS |
| `git diff --check` | PASS |
| Shared OpenViking MCP | Health und read-only `search_experience` PASS |
| Globale Codex-Dateien | Unverändert und identisch zu SHA-256-verifiziertem Backup |

Der eine Core-Fehler ist
`test_vlm_config_default_provider_resolves_codex`; er reproduziert auf der
unveränderten Basis mit 29/30 bestandenen Tests. Weitere elf Stream-Config-Fehler
reproduzieren ebenfalls auf der Basis mit 9/20 bestandenen Tests. Sie werden nicht
als Kandidatenregression ausgegeben.

## 7. Freigabestatus

Der Kandidat ist implementiert und offline verifiziert, aber nicht live
freigegeben. Folgende HOLDs sind zwingend:

- Es existiert noch keine kontrollierte A/B-Matrix mit mindestens 20
  sanitisierten realen Langsitzungen und 10 synthetischen Szenarien.
- Der Capability-Probe und Canary gegen den exakt verwendeten Codex-Endpunkt
  wurden nicht ausgeführt. Der Probe kann Requests erzeugen und potenziell Kosten
  verursachen; er erfordert vorherige ausdrückliche Freigabe.
- Die bestätigten Legacy-Baseline-Fehler sind nicht bereinigt.
- Es erfolgte keine Aktivierung, Default-Promotion oder globale Hook-Installation.

Die Default-Promotion bleibt ein separater Evidenzentscheid. Ein Restart von
Rechner, Server, Runtime oder Service ist weder erforderlich noch autorisiert.

Der Security-Re-Review Revision 2 hob das Offline-Kandidaten-Veto auf: keine
offenen Critical-/High-Befunde, 95,6 % aggregiert und mindestens 91 % je
Kriterium. Da das geforderte aktuelle Claude Opus nicht verfügbar war, ist die
Bewertung mit einem Codex-Ersatzmodell vorläufig. Die verbleibenden
Medium-Befunde stehen im Open-Item-Bericht.

## 8. Verknüpfte Artefakte

- [TRD](2026-07-31-codex-compaction-openviking-responses-trd.md)
- [Implementation Dossier](2026-07-31-codex-compaction-openviking-responses-id.md)
- [Planning Document](../plan/2026-07-31-codex-compaction-openviking-responses-pd.md)
- [Test Dossier](../tests/2026-07-31-codex-compaction-openviking-responses-td.md)
- [Open Items](../sessions/2026-07-31-codex-compaction-openviking-responses-open-items.md)
- [Manual](../manuals/2026-07-31-codex-compaction-openviking-responses-manual.html)
