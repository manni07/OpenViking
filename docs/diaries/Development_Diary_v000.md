# Development Diary v000

## Codex-Compaction und OpenViking Responses State

Datum: 2026-07-31
Status: Kandidat implementiert; keine Live-Aktivierung

## Ausgangslage

Die Umsetzung startete in einem isolierten OpenViking-Worktree auf Commit
`60ef45d4`. Ungetrackte Dateien des Haupt-Checkouts blieben unangetastet. Vor
potenziellen globalen Codex-Änderungen wurden `config.toml`, `hooks.json` und das
bestehende Hook-Skript auf einem Backup-Volume gesichert, gehasht und mit
restriktiven Rechten versehen.

## Arbeitschronik

### 1. Architektur und Stop-Regeln

ARD, TRD und PD definierten einen additiven State-Pfad, einen nicht installierten
Hook-Kandidaten und fail-closed Live-Gates. `VLMBase`, andere Provider, globale
Codex-Dateien und laufende Dienste wurden aus dem Änderungsumfang ausgeschlossen.

### 2. Testvertrag

Die neuen Tests wurden auf Kontinuitäts- und Sicherheitsgründe ausgerichtet:
keine Prompt-Injection aus Hook-Eingaben, keine unsicheren Symlinkpfade, kein
State-Commit nach Teil-Streams, keine Cross-Chain- oder Tool-Replays und kein
stiller Capability-Fallback.

### 3. Hook-Implementierung

Der Hook-Kandidat erhielt private Rechte, sichere atomare Dateien,
komponentenweise Symlink- und Eigentümerprüfungen, Eingabe-/Zeitlimits und feste
Prompts. Eine abschließende Pfadprüfung führte zu einem zusätzlichen
Parent-Symlink-Test. Im Offline-Sicherheits-Follow-up wurden alle Dateioperationen
an Directory-FDs verankert, die Deadline erzwungen und TTL-/Anzahl-/Scan-Limits
für die Retention ergänzt. Ergebnis: 30 Hook-Tests bestanden.

### 4. Responses-Implementierung

Der Adapter erhielt einen frozen State, kanonische vollständige Output-Items,
Compaction-Reduktion, commit-on-complete, native Async-Streams, Tool exactly once,
Bindings, Integrität und harte Limits. `CodexVLM` exponiert additive
State-Methoden und einen expliziten Probe. Nach einem Security-Veto wurden
Trace-Redaction, Adapter-Initialisierungsrace, Credential-I/O im Event-Loop und
unbegrenzte retained Call-ID-Metadaten TDD-geführt gehärtet. Das Follow-up band
Credentials stabil an ihren persistenten Slot, auch ohne `client_id`, und
schirmte Stream-/Client-Cleanup gegen wiederholte Cancellation und Close-Fehler
ab. Ein ergänzender Test stellt sicher, dass ein Close-Fehler die ursprüngliche
Cancellation nicht verdeckt. Ergebnis: 72 State-/Adaptertests bestanden.

### 5. Konfiguration

`responses_state_enabled` und `responses_compact_threshold` wurden opt-in
ergänzt. Threshold ohne State und State ohne genau ein `openai-codex`-Credential
werden abgelehnt. Der Default bleibt aus.

### 6. Verifikation

Frische Kandidatensuiten: 102/102 PASS. Die Core-Kombination lieferte 131 PASS und
einen Fehler; die erweiterte Kombination 140 PASS und zwölf Fehler. Der einzelne
Codex-Config-Fehler sowie elf Stream-Config-Fehler wurden auf der unveränderten
Basis reproduziert. Ruff, Format, Compileall und `git diff --check` bestanden.

Der gemeinsame OpenViking-MCP bestand Health und eine read-only Suche ohne
Restart. Globale Codex-Dateien blieben identisch zu den SHA-256-verifizierten
Backups.

Der Security-Re-Review Revision 2 meldete keine offenen Critical-/High-Befunde
und hob das Offline-Kandidaten-Veto auf. Score: 95,6 % aggregiert, mindestens
91 % je Kriterium. Der Review ist wegen eines Codex-Ersatzmodells vorläufig; das
geforderte aktuelle Claude Opus war nicht verfügbar. Die drei Medium-Befunde
wurden anschließend TDD-geführt im Commit
`325e5cff3895036a2fc0e8a0a93131e77f7c9d0d` geschlossen und mit Commit
`0556a9aac049d2563893e1abe4068c0260024542` um den kombinierten
Cancellation-/Close-Fehlerfall ergänzt. Eine unabhängige
Revalidierung bleibt vor Aktivierung erforderlich.

## Entscheidungen

- 206720 bleibt unveränderte Baseline; 175k wurde nicht übernommen.
- Capability wird nicht vermutet, sondern muss am exakten Endpoint geprüft
  werden.
- Der Probe wurde nicht ausgeführt, weil er potenziell kostenpflichtig ist und
  ausdrückliche Genehmigung benötigt.
- Ohne 20 reale und 10 synthetische Szenarien gibt es keine A/B-Siegerwahl.
- Vorbestehende Legacy-Fehler werden sichtbar als HOLD geführt.
- Keine Installation, Aktivierung, Promotion, kein Restart und kein Git-Publish.

## Ergebnis

Der Worktree enthält einen offline verifizierten, opt-in Kandidaten und die
zugehörige Übergabedokumentation. Live-Capability, A/B-Effekt und Default-Promotion
sind ausdrücklich nicht bewiesen.

## Verweise

- [Implementation Dossier](../dossiers/2026-07-31-codex-compaction-openviking-responses-id.md)
- [Test Dossier](../tests/2026-07-31-codex-compaction-openviking-responses-td.md)
- [Open Items](../sessions/2026-07-31-codex-compaction-openviking-responses-open-items.md)
