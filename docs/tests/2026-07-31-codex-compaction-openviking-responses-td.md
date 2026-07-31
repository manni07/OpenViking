# Test Dossier

## Codex-Compaction und Responses State

Stand: 2026-07-31
Status: Neue Kandidatensuiten vollständig grün; Legacy-Baseline und Live-Gates
auf HOLD

## 1. Testabsicht

Die Tests kodieren die Sicherheits- und Kontinuitätsgründe der Änderung:

- untrusted Hook-Eingaben dürfen nicht in den nächsten Prompt gelangen;
- ein unsicherer Dateipfad darf keine private Kontinuitätsdatei ersetzen;
- State darf weder Chain-, Credential- noch Generationsgrenzen überschreiten;
- ein unvollständiger Stream darf keinen neuen State veröffentlichen;
- Tool-Ausgaben dürfen genau einmal und nur für offene IDs angenommen werden;
- Compaction darf keine Items nach dem neuesten Compaction-Item verlieren;
- der Legacy-Pfad muss Default bleiben.

## 2. Testinventar

| Datei | Fokus | Ergebnis |
|---|---|---:|
| `tests/unit/test_codex_compaction_hook.py` | Rechte, Symlinks, Timeout, Korrelation, Parallelität, Injection | 24 PASS |
| `tests/unit/test_codex_responses_state.py` | State, Streaming, Compaction, Tool-Calls, Limits, Config | 68 PASS |
| **Gesamt neu** |  | **92 PASS** |

## 3. Hook-Abdeckung

Die Hook-Suite prüft:

- ausschließlich konstante Ausgabe bei bösartigen Transcript-, Pfad- und
  Repository-Feldern;
- `0700`-Verzeichnis und `0600`-Datei;
- atomaren Austausch und Parallelzugriffe;
- Symlink-Ablehnung am Ziel und in jeder Pfadkomponente von `CODEX_HOME` bis
  `state/compaction-hooks`;
- Eigentümer- und Verzeichnisinvarianten;
- 64-KiB-Eingabelimit und interne Fünf-Sekunden-Grenze;
- PreCompact/SessionStart/PostCompact-Korrelation;
- keine behauptete semantische Transcript-Vollständigkeit.

## 4. Responses-Abdeckung

Die State-Suite prüft:

- immutable Branches und explizites Forking;
- Bindings für Modell, Instructions, Origin, Principal und Credential;
- stale Generation, Replay, manipulierten Integrity-Tag und TTL;
- vollständige Reasoning-, Tool-, Output- und Compaction-Items;
- Beschneidung ausschließlich vor dem neuesten Compaction-Item;
- parallele und verschachtelte Chains ohne Datenübertritt;
- Tool-Ausgabe genau einmal für offene IDs;
- Timeout, Cancellation, Fehler und Teil-Stream ohne State-Commit;
- keine automatische Wiederholung nach dem ersten Event;
- natives Async-Streaming und Sync-/Async-Parität;
- State-, Item-, Turn-, Bild-, Tool-Ausgabe- und Chain-Limits;
- Sentinel-Secrets in Log-Capture;
- keine sichtbaren oder opaken Tool-Inhalte in State-spezifischen Traces;
- threadsichere Singleton-Initialisierung der Adapter;
- Credential-I/O außerhalb des Async-Event-Loops;
- maximal 4096 retained Tool-Call-IDs, 512 Bytes je ID und Einrechnung in die
  State-Byte-Grenze;
- `store=false` und Ablehnung von Conversations,
  `previous_response_id`, `background` und `extra_body`-Umgehungen;
- OAuth-Origin und Single-Credential-Pilot;
- Capability-Fehler ohne stillen Fallback;
- unveränderte zustandslose Legacy-Aufrufe.

## 5. Frische Testevidenz

### 5.1 Neue Suiten

```text
92 passed, 4 warnings
```

Bewertung: Kandidaten-Gate PASS; keine Skips oder Xfails.

### 5.2 Core-Kombination

Enthalten:

- beide neuen Suiten;
- `tests/unit/test_codex_vlm.py`;
- `tests/models/vlm/test_timeout_config.py`.

```text
122 collected
121 passed
1 failed
4 warnings
```

Einziger Fehler:

```text
tests/unit/test_codex_vlm.py::test_vlm_config_default_provider_resolves_codex
```

Der unveränderte Basis-Checkout liefert für die betroffene Suite 29 PASS und
denselben einen Fehler. Das ist keine Kandidatenregression, aber ein Legacy-HOLD.

### 5.3 Erweiterte Kombination

Zusätzlich enthalten: `tests/unit/test_stream_config_vlm.py`.

```text
142 collected
130 passed
12 failed
4 warnings
```

Elf Stream-Config-Fehler reproduzieren auf der Basis mit 9 PASS und 11 FAIL.
Zusammen mit dem bekannten Codex-Config-Fehler sind alle zwölf Fehler als
vorbestehend bestätigt. Die Legacy-Suite ist trotzdem nicht vollständig grün.

### 5.4 Statische Prüfungen

```text
ruff check:        PASS
ruff format --check: 6 files already formatted
python -m compileall -q: PASS
git diff --check:  PASS
```

## 6. MCP- und Live-Grenze

Der gemeinsam genutzte OpenViking-Dienst auf `127.0.0.1:1933` bestand einen
Health-Check und einen read-only `search_experience`-Aufruf. Es erfolgte kein
Restart. Das beweist den MCP-Zugriff, nicht die Codex-Responses-Capability.

Nicht ausgeführt:

- Capability-Probe für `context_management` am exakten Codex-Endpunkt;
- Live-Nachweis von Compaction-Items und Replay;
- Canary mit echter Chain;
- A/B-Matrix mit 20 realen und 10 synthetischen Szenarien.

Der Capability-Probe kann einen Provider-Request und damit Kosten auslösen. Er
bedarf ausdrücklicher Genehmigung.

## 7. Test-Simulation

Vor Implementierung wurde die Teststrategie anhand der Kriterien
Vollständigkeit, Determinismus, Isolation, Security, Mutation-Sensitivität,
Async/Sync-Parität, Legacy-Schutz und Diagnosefähigkeit bewertet.

| Kriterium | Wert |
|---|---:|
| Vertragsvollständigkeit | 98 % |
| Determinismus | 98 % |
| Isolation | 97 % |
| Security | 98 % |
| Mutation-Sensitivität | 96 % |
| Async/Sync-Parität | 97 % |
| Legacy-Schutz | 96 % |
| Diagnosefähigkeit | 98 % |
| **Aggregiert** | **97,2 %** |

Damit sind mindestens 95 % aggregiert und mindestens 90 % je Kriterium erreicht.
Die Simulation ersetzt keine Live- oder unabhängige Security-Evidenz.

## 8. Freigabebewertung

| Gate | Status |
|---|---|
| Neue kritische Tests 100 % | PASS |
| Null Cross-Chain-Leaks in Offline-Tests | PASS |
| Kandidatenregression in geprüften Suites | Keine nachgewiesen |
| Legacy vollständig grün | HOLD |
| 20+10 A/B-Corpus | HOLD |
| Exakter Endpoint-Probe und Canary | HOLD |
| Qualitäts-/Token-/Latenz-/Fehler-Promotion | HOLD |

Gesamturteil: **Implementierter Offline-Kandidat, nicht aktiviert und nicht zur
Default-Promotion freigegeben.**

Der Security-Re-Review Revision 2 meldet keine offenen Critical-/High-Befunde
und hebt das Offline-Kandidaten-Veto auf. Score: 95,6 % aggregiert, mindestens
91 % je Kriterium. Die Bewertung ist vorläufig, weil das geforderte aktuelle
Claude Opus nicht verfügbar war und Codex als Ersatzmodell diente. Die drei
Medium-Restbefunde sind im Open-Item-Bericht erfasst.

## 9. Reproduktion

Die verwendete Testumgebung nutzt den OpenViking-Python-Interpreter und einen
isolierten Offline-Dependency-Pfad:

```bash
PYTHONPATH=/tmp/openviking-codex-responses-test-deps-20260731 \
  /Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m pytest \
  -q -o addopts= \
  tests/unit/test_codex_compaction_hook.py \
  tests/unit/test_codex_responses_state.py
```

Der temporäre Dependency-Pfad enthält keine produktive Aktivierung.

## 10. Verknüpfte Artefakte

- [Implementation Dossier](../dossiers/2026-07-31-codex-compaction-openviking-responses-id.md)
- [TRD](../dossiers/2026-07-31-codex-compaction-openviking-responses-trd.md)
- [Open Items](../sessions/2026-07-31-codex-compaction-openviking-responses-open-items.md)
