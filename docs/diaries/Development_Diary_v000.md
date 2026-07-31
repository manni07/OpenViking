# Development Diary v000

## 2026-07-27 — Synchronisierte Main-Fassung: Security Hardening

**Auslöser.** Nach sicherer Synchronisation der Main-Basis wurde ein Sicherheitsaudit erstellt. Die Umsetzung folgt dem durch `$tccode` geführten Phasenmodell mit `agent-workflow-v4` in thorough/critical-Ausprägung und gestaffelten Rollen.

**Entscheidungen.**

- Lokale WebDAV-Uploads erhalten einen sicheren Default von 16 MiB; Überschreitungen müssen vor einem Schreibpfad mit HTTP 413 enden.
- Öffentliche Bindungen sind fail-closed: keine CORS-Wildcard, konkrete Origin-Allowlist und explizite HTTPS-`public_base_url`; lokale Defaults bleiben ohne CORS-Wildcard gültig.
- Markdown-Links werden im Web Studio und der Graph-HTML-Ausgabe anhand enger Schema-Allowlisten behandelt; gesperrte Links erhalten keinen klickbaren Zielwert.
- Abhängigkeitsupdates bleiben auf kompatible Versionen begrenzt. Nicht kompatible Starlette-, Rust-, shadcn- und Bot-Pfade werden nicht stillschweigend durch Major-Upgrades ersetzt.
- Der neue CI-Entwurf führt Python-, Cargo- und npm-Audits aus und erlaubt nur paketpfadgenaue, ablaufende Baseline-Befunde.

**Arbeitsartefakte.** ARD, TRD, PD, ID, Simulation und Testdossier liegen in `docs/dossiers/`, `docs/plan/` und `docs/tests/`. Der Ausgangsbefund liegt in `docs/audit/2026-07-27-security-audit-main.md`; der Reststatus in `docs/openitem/Security_Hardening_Open_Items_2026-07-27.md`.

**Validierungsstand.** 13 fokussierte Python-Regressionen (Public-URL, exakte und überschreitende WebDAV-Streamgrenze, Baseline-Verifier), 16 Vitest-Fälle sowie Studio-Lint/Build sind grün. Der nachgelagerte Konfigurationsabgleich bestand zusätzlich mit 37 Konfigurations-/Public-URL-Tests. Die CI des ersten Härtungs-Commits bestand vollständig, einschließlich API/CLI-Integration, Plattform-Builds, Dokumentationsbuild und Dependency-Audit. Anschließend wurden noch Helm- und Beispielkonfigurationen auf sichere öffentliche Defaults ausgerichtet; deren PR-Check bleibt vor dem Merge erneut abzuwarten. Nicht als bestanden behauptet werden: ein lokaler vollständiger Python-Audit (Subprozess `SIGABRT`), eine vollständige Suite ohne gültige `ov.conf`, Browser-E2E/Serverstart oder ein Deployment. Der angeforderte `agy`-Review war im Headless-Modus nicht berechtigt; dies bleibt ein dokumentierter externer Review-Blocker.

**Restarbeit.** Vor Merge die PR-Checks des sicheren Konfigurationsnachtrags abwarten; jede der 74 Baseline-Ausnahmen vor dem 2026-08-27 entfernen oder erneut explizit bewerten. Eine reale Bereitstellung verlangt einen konkret benannten Ziel-Host/-Cluster und dessen nicht-sekrete Konfigurationsreferenzen; lokal ist kein Docker-Daemon und kein Kubernetes-Kontext verfügbar. Kein Rechner- oder Serverneustart wurde ausgeführt oder ist für diese Arbeit angeordnet.

**Betroffener Git-Kontext.** Basis `60ef45d4c3a7d07ceb1df4e9d7dde7a14449ac50`; Arbeitszweig `agent-workflow/20260727-security-hardening` im isolierten Worktree. Draft-PR #1 ist im Fork `manni07/OpenViking` eröffnet; Push/Merge erfolgen nur nach Status-, Diff- und Checkprüfung.
## Codex-Compaction und OpenViking Responses State

Datum: 2026-07-31
Status: Offline-Kandidat vorhanden; Legacy-VLM-H3, Security und Live auf HOLD

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

Der separate Legacy-VLM-H3-Sicherheitsreview durchlief die maximal drei
Revisionen: 78/100 (`0C/5H/1M`), 84/100 (`0C/3H/1M`) und final 89/100
(`0C/1H/1M`). H2–H5 wurden geschlossen; H1, der exakte Konstantenvertrag für
markierte VikingBot-Fehler, blieb offen. Damit wurden `0H` und 90/100 verfehlt.
Source-Unlock wurde verweigert; es erfolgte keine Produktionscodeänderung und
keine vierte H1-Schließungsrevision. Die sechs ergänzten Vertrags-Testdateien
wurden final mit `266 collected = 129 PASS + 137 fachliche RED` ausgeführt.

OpenViking MCP Health und ein echter read-only `search_experience`-Aufruf waren
PASS, ohne Restart. Diese Evidenz beweist MCP-Zugriff, nicht die Responses-/
Compaction-Fähigkeit des Providers. Der User vertagte den Live-Provider-Test.

## Entscheidungen

- 206720 bleibt unveränderte Baseline; 175k wurde nicht übernommen.
- Capability wird nicht vermutet, sondern muss am exakten Endpoint geprüft
  werden.
- Der Probe wurde nicht ausgeführt, weil er potenziell kostenpflichtig ist und
  ausdrückliche Genehmigung benötigt.
- Ohne 20 reale und 10 synthetische Szenarien gibt es keine A/B-Siegerwahl.
- Vorbestehende Legacy-Fehler werden sichtbar als HOLD geführt.
- Der finale H3-Security-HOLD bleibt bestehen; H1 wird in diesem Lauf nicht
  weiter revidiert oder implementiert.
- Der bestandene MCP-Read ist kein Ersatz für einen Provider-Capability-Probe.
- Der Live-Test wurde auf Wunsch des Users vertagt.
- Keine Installation, Aktivierung, Promotion, kein Restart und kein Git-Publish.

## Ergebnis

Der Worktree enthält einen offline verifizierten, opt-in Kandidaten und die
zugehörige Übergabedokumentation. Der Legacy-VLM-H3-Follow-up bleibt wegen H1
bei verweigertem Source-Unlock auf HOLD. Live-Capability, A/B-Effekt und
Default-Promotion sind ausdrücklich nicht bewiesen.

## Verweise

- [Implementation Dossier](../dossiers/2026-07-31-codex-compaction-openviking-responses-id.md)
- [Test Dossier](../tests/2026-07-31-codex-compaction-openviking-responses-td.md)
- [Lessons Learned](../lessons/2026-07-31-codex-compaction-openviking-responses-lessons-learned.md)
- [Open Items](../sessions/2026-07-31-codex-compaction-openviking-responses-open-items.md)
