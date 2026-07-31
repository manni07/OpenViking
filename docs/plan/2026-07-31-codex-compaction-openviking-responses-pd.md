# Planning Document

## Optimierung von Codex-Compaction und OpenViking Responses

Stand: 2026-07-31
Status: Implementierter Kandidat; Offline-Gates bestanden; Live- und
Promotions-Gates auf HOLD

## 1. Ziel und Erfolgskriterien

Das Vorhaben sollte lokale Codex-Compaction sicherer machen und OpenViking um
einen expliziten, aufruferverwalteten Responses-State erweitern. Erfolg bedeutet:

- additive Implementierung ohne Änderung des Legacy-Defaults;
- keine Cross-Chain-Leaks oder ungebundene Tool-Ausgaben;
- keine Veröffentlichung eines Teil-States;
- Hook-Sicherheit gegen Rechte-, Symlink-, Parallelitäts-, Timeout- und
  Prompt-Injection-Risiken;
- verifizierte Tests und dokumentierter Rollback;
- keine Aktivierung oder Promotion ohne gesonderte Evidenz.

Der Kandidat erfüllt die implementierbaren Offline-Kriterien. Die empirischen und
Live-Kriterien sind offen und bleiben fail-closed.

## 2. Quick-Win-First-Ausführung

| Reihenfolge | Arbeitspaket | Ergebnis |
|---:|---|---|
| 1 | Hook-Sicherheit und Backup | Kandidat implementiert; globale Dateien unverändert |
| 2 | Baseline und Capability-Grenze | Baseline-Fehler reproduziert; Live-Probe nicht autorisiert |
| 3 | Lokale A/B-Messung | **HOLD:** Corpus 20 real + 10 synthetisch fehlt |
| 4 | State-Vertrag | Implementiert und getestet |
| 5 | Tests | 92 neue Tests bestanden |
| 6 | Adapter und Config | Implementiert; Default bleibt aus |
| 7 | Canary | **HOLD:** potenziell kostenpflichtig, Genehmigung erforderlich |
| 8 | Promotion | **HOLD:** keine Freigabeevidenz |

Die Reihenfolge verhinderte, dass Live-Aufrufe oder globale Änderungen als
Voraussetzung für die sichere Offline-Implementierung behandelt wurden.

## 3. Phasenstatus

### Phase 0 — Isolation, Dossiers und Hook

Erledigt:

- isolierter Worktree auf Basis `60ef45d4`;
- globale Codex-Dateien vorab gesichert und SHA-256-verifiziert;
- quellkontrollierter Hook mit privaten Rechten, atomarem Schreiben,
  komponentenweiser Symlink-Prüfung, fester Ausgabe und Ressourcenlimits;
- 24 Hook-Tests bestanden.

Nicht durchgeführt:

- Installation oder Aktivierung des Hooks;
- Restart eines Rechners, Servers, Dienstes oder einer Runtime.

### Phase 1 — Baseline, A/B und Capability

Erledigt:

- aktuelle Baseline-Ausfälle auf dem unveränderten Checkout reproduziert;
- Vergleichskandidaten und Promotionsmetriken definiert;
- expliziter Capability-Probe implementiert.

HOLD:

- keine 20 sanitisierten realen Langsitzungen und 10 synthetischen Szenarien;
- kein Live-Probe am exakten Codex-Endpunkt;
- keine Kandidatenwahl für den globalen Compaction-Schwellwert.

Der vorhandene Wert 206720 bleibt unverändert. 175k wurde nicht übernommen.

### Phase 2 — Responses-State

Erledigt:

- immutable State- und Turn-Verträge;
- Sync-/Async-Streaming;
- `store=false`, Delta-only und verbotene Conversation-Felder;
- vollständige Item-Weitergabe und neueste-Compaction-Beschneidung;
- Commit-on-complete, Tool exactly once, Bindings, TTL und Limits;
- OAuth-Origin- und Single-Credential-Grenze;
- opt-in Konfiguration;
- 68 State-/Adaptertests bestanden.

### Phase 3 — Abschlussdokumentation

Erledigt:

- ARD, TRD, PD, TD und Implementation Dossier;
- Development Diary, Manual, Proposal Dossier und Open-Item-Bericht;
- Session-Transfer-Protokoll wird separat geführt.

Nicht durchgeführt:

- Commit, Push, PR, Merge, Aktivierung oder Promotion.

## 4. Verifikation

| Gate | Ist | Status |
|---|---:|---|
| Neue Tests | 92/92 | PASS |
| Core kombiniert | 121/122; 1 Baseline-Fehler | CANDIDATE PASS / LEGACY HOLD |
| Erweitert | 130/142; 12 Baseline-Fehler | CANDIDATE PASS / LEGACY HOLD |
| Ruff | Check und Format PASS | PASS |
| Compileall | PASS | PASS |
| Diff-Whitespace | PASS | PASS |
| MCP read-only | Health und Suche PASS | PASS |
| Endpoint Capability | nicht ausgeführt | HOLD |
| A/B-Corpus | nicht ausgeführt | HOLD |

Die bestehenden Fehler sind ein Codex-Config-Test und elf Stream-Config-Tests.
Alle reproduzieren auf dem unveränderten Basis-Checkout.

## 5. Promotionsgate

Eine spätere Default-Promotion erfordert kumulativ:

- keine Qualitätsverschlechterung und keinen kritischen Szenarioverlust;
- mindestens 20 % weniger mediane Output-Tokens;
- höchstens 10 % schlechtere p95-Latenz;
- keine höhere Fehlerrate;
- null Cross-Chain-Leaks;
- 100 % kritische Kontinuitäts-, Security- und Legacy-Tests.

Bei einem verfehlten Kriterium bleibt der Modus opt-in. Der Capability-Probe und
Canary können Requests gegen einen potenziell kostenpflichtigen Endpoint erzeugen
und dürfen nur nach ausdrücklicher Genehmigung ausgeführt werden.

## 6. Stop- und Rollback-Regeln

- Keine globale Änderung ohne Vergleich mit den SHA-256-verifizierten Backups.
- Kein Restart ohne ausdrückliche Bestätigung.
- Kein stiller Capability-Fallback.
- Kein Failover innerhalb einer State-Chain.
- Kein State-Commit nach Teil-Stream, Fehler oder Cancellation.
- Bei einem Live- oder A/B-Gate-Fehler bleibt die Funktion aus; es erfolgt keine
  Promotion.

## 7. Simulation

Die Test-Simulation erreichte 97,2 % aggregiert bei mindestens 96 % je
Einzelkriterium. Die Implementierungs-Selbstsimulation im
[Implementation Dossier](../dossiers/2026-07-31-codex-compaction-openviking-responses-id.md)
erreicht 96,0 % aggregiert und mindestens 92 % je Kriterium. Beide überschreiten
95 % aggregiert und 90 % je Kriterium. Diese Simulation ist keine unabhängige
Live-Evidenz und hebt die HOLDs nicht auf.

Der Security-Re-Review Revision 2 erreichte 95,6 % aggregiert und mindestens
91 % je Kriterium. Er meldet keine offenen Critical-/High-Befunde und hebt das
Offline-Kandidaten-Veto auf. Wegen Nichtverfügbarkeit des geforderten aktuellen
Claude Opus wurde Codex vorläufig als Ersatzmodell eingesetzt. Die drei
verbleibenden Medium-Befunde bleiben offen.

## 8. Nächste autorisierte Entscheidung

Ohne neue Genehmigung ist nur Offline-Arbeit zulässig. Die nächste materielle
Entscheidung ist entweder:

1. A/B-Corpus bereitstellen und Messung freigeben; oder
2. den potenziell kostenpflichtigen Capability-Probe plus Canary explizit
   genehmigen.

Bis dahin bleibt der Kandidat nicht aktiviert.

## 9. Artefakte

- [ARD](../dossiers/2026-07-31-codex-compaction-openviking-responses-ard.md)
- [TRD](../dossiers/2026-07-31-codex-compaction-openviking-responses-trd.md)
- [Implementation Dossier](../dossiers/2026-07-31-codex-compaction-openviking-responses-id.md)
- [Test Dossier](../tests/2026-07-31-codex-compaction-openviking-responses-td.md)
- [Development Diary](../diaries/Development_Diary_v000.md)
- [Manual](../manuals/2026-07-31-codex-compaction-openviking-responses-manual.html)
- [Proposal Dossier](../vision/2026-07-31-codex-compaction-openviking-responses-ppd.md)
- [Open Items](../sessions/2026-07-31-codex-compaction-openviking-responses-open-items.md)
