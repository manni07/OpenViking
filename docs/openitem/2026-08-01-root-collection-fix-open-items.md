# Open Items: Root-Test-Collection-Fix

**Stand:** 2026-08-01
**Status:** Root-Collection PASS; weitere Ausfuehrungs- und Live-Gates HOLD

Die folgenden neun Massnahmen sind bewusst nach Prioritaet getrennt. Keine
Massnahme erweitert die aktuelle Autorisierung fuer Provideraufrufe, Services
oder Restarts.

## High

| ID | Massnahme | Abschlusskriterium |
|---|---|---|
| H1 | Capability-Probe weiterhin fail-closed vorbereiten | Erst nach neuer ausdruecklicher Live-, Credential- und Kostenfreigabe; exakter Endpoint, Modell und Limits vor Netzwerkzugriff festgelegt; keine stillen Fallbacks |
| H2 | Live-Benchmark und Canary erst nach H1-PASS ausfuehren | Separat freigegebener Datenkorpus und Promotionkriterien vollstaendig; keine Aktivierung allein aufgrund der Offline-Collection |
| H3 | API- und OpenClaw-/OC2OV-Harnesses in ihren jeweils eigenen Projektkontexten qualifizieren | Beide Dependency-/Settings-Vertraege separat hergestellt und die Suiten aus ihren Besitzerverzeichnissen ausgefuehrt; Ergebnisse inklusive Skips, Xfails und Live-Voraussetzungen getrennt berichtet |

## Medium

| ID | Massnahme | Abschlusskriterium |
|---|---|---|
| M1 | Die 11 unbekannten `cli_remote`-Marker kanonisch registrieren oder ihrem Besitzer-Workflow zuordnen | Root-Collection meldet keine unbekannten `cli_remote`-Marker; Semantik und Besitzer sind dokumentiert |
| M2 | Den unbekannten `qdrant`-Marker kanonisch registrieren | Marker ist in der aktiven Pytest-Konfiguration definiert und bleibt gezielt selektierbar |
| M3 | Die drei Helper-Class-Collection-Warnungen ohne Produktivrefactor beseitigen | Hilfsklassen werden eindeutig nicht als Tests gesammelt; vorhandene Testsemantik bleibt unveraendert |

## Low

| ID | Massnahme | Abschlusskriterium |
|---|---|---|
| L1 | Root-Collection als expliziten CI-Gate mit frischer lockfile-basierter venv abbilden | CI nutzt einen gepinnten Interpreter und `uv sync --frozen --extra test`; Collection-Fehler brechen den Job ab |
| L2 | Abhaengigkeits- und Collection-Inventardrift sichtbar machen | Python-, uv-, `mcp`- und `scrapy`-Version sowie Testzahl werden als Diagnoseartefakt publiziert, ohne Secrets oder Umgebungsinhalte zu loggen |
| L3 | Weitere optionale Provider-E2E-Module auf Top-Level-Imports pruefen | Statischer oder gezielter Collection-Vertrag dokumentiert alle optionalen Provider; keine speculative Produktivabstraktion |

## Verbindliche Aussagegrenze

Die 20 Collection-Fehler sind geschlossen. Die eigenstaendigen Harnesses sind
nur korrekt aus dem Root-Scope entfernt, nicht ausgefuehrt. Die vollstaendige
Root-Testausfuehrung und alle Live-Provider-Phasen bleiben ohne neue
Autorisierung offen. Kein Rechner-, Server-, Runtime-, Container-, Service-
oder Prozess-Restart ist durch diesen Bericht erlaubt.

## Nachlauf: Offline-Warnungen und OpenClaw-Harness — 2026-08-01

Die Massnahmen M1, M2 und M3 sind mit dem Nachlauf abgeschlossen:

- `cli_remote` und `qdrant` sind in der Root-Pytest-Konfiguration registriert.
- Die drei Supportklassen sind nicht mehr als Testklassen benannt.
- Die neue Regression `tests/test_collection_warnings.py` besteht mit 2/2 Tests.
- Die frische Root-Umgebung sammelt 6384 Tests mit `--strict-markers` und ohne
  Collection-Warnungen.

H3 ist offline teilweise abgeschlossen: Der eigenständige OpenClaw-/OC2OV-
Harness sammelt aus seinem eigenen Verzeichnis 47 Tests ohne
`PytestCollectionWarning`; `tests/test_cli_diagnostics.py` besteht mit 4/4.
Die temporär aus der Beispielkonfiguration erzeugten Settings wurden nach dem
Lauf entfernt und nie versioniert. P0-/Live-Tests, der veraltete Harness-
Runner sowie H1/H2 und Provider-Live-Tests bleiben bewusst HOLD.

Der aktuelle, exakt dreistufige Folgebericht (3 High, 3 Medium, 3 Low) ist
[`2026-08-01-warnings-openclaw-open-items.md`](2026-08-01-warnings-openclaw-open-items.md).
