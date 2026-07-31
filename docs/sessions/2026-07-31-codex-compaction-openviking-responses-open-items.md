# Open-Item-Bericht

## Codex-Compaction und OpenViking Responses State

Stand: 2026-07-31
Status: Kandidat bleibt opt-in und nicht aktiviert

Dieser Bericht enthält exakt drei High-, drei Medium- und drei Low-Maßnahmen.

## High — 3 Maßnahmen

| ID | Maßnahme | Abschlusskriterium |
|---|---|---|
| H1 | A/B-Matrix mit mindestens 20 sanitisierten realen Langsitzungen und 10 synthetischen Multi-Turn-/Tool-Szenarien ausführen | Qualität unverändert; mediane Output-Tokens mindestens 20 % niedriger; p95-Latenz höchstens 10 % schlechter; Fehlerrate nicht höher |
| H2 | Capability-Probe und Canary am exakt verwendeten Codex-Endpunkt nach ausdrücklicher Kosten-/Live-Genehmigung ausführen | `context_management`, Compaction-Items und Replay belegt; kein stiller Fallback; null Cross-Chain-Leaks |
| H3 | Vorbestehenden Codex-Config-Fehler und elf Stream-Config-Fehler klären und Legacy-Suites erneut ausführen | Ursache dokumentiert und vollständiges relevantes Legacy-Gate grün oder separat ausdrücklich akzeptiert |

## Medium — 3 Maßnahmen

| ID | Maßnahme | Abschlusskriterium |
|---|---|---|
| M1 | Fehlende Garantie für `client_id` im Credential-Resolver schließen | State-Binding besitzt eine stabile, getestete Credential-Slot-Identität auch ohne optionales Resolverfeld |
| M2 | Async-Cleanup gegen wiederholte Cancellation abschirmen | `_leave_request` und Stream-Close laufen deterministisch; kein geleakter Chain-Slot |
| M3 | Hook-Aktivierung gegen TOCTOU, externe Deadline und unbegrenzte Retention härten | Aktivierungsreview belegt atomare Pfadentscheidung, Aufrufer-Deadline und begrenzte Altmetadaten |

## Low — 3 Maßnahmen

| ID | Maßnahme | Abschlusskriterium |
|---|---|---|
| L1 | Vorbestehende Pydantic-Warnungen separat bereinigen | Warnungsfreier gezielter Lauf ohne Scope-Mischung |
| L2 | Nutzerorientierte Übersetzungen und öffentliche API-Dokumentation erst nach Promotionsentscheid ergänzen | Dokumentation entspricht dem tatsächlich freigegebenen Modus |
| L3 | Inhaltsfreie Entwicklerdiagnostik für Limits und Capability-Fehler verbessern | Keine State-, Credential-, Prompt- oder Tool-Inhalte in Logs/Traces |

## Stop-Regel

H1 bis H3 verhindern die Default-Promotion. H2 kann Providerkosten erzeugen und
darf ohne ausdrückliche Genehmigung nicht gestartet werden. Kein offener Punkt
autorisiert Aktivierung, Restart, Commit, Push oder Merge.

## Verweise

- [Implementation Dossier](../dossiers/2026-07-31-codex-compaction-openviking-responses-id.md)
- [Test Dossier](../tests/2026-07-31-codex-compaction-openviking-responses-td.md)
- [Proposal Dossier](../vision/2026-07-31-codex-compaction-openviking-responses-ppd.md)
