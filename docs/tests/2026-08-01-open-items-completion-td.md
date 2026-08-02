# Test Dossier — Open Items Completion (2026-08-01)

## Testvertrag

Der Test muss zeigen, dass Root und eigenständige Harnesses ihre
Konfigurationen, Pythonpfade und Collection-Grenzen nicht vermischen. Ein
Test, der nur durch Markerfilter oder eine zufällige Host-Konfiguration grün
wird, gilt nicht als PASS.

## Ausgeführte Nachweise

| Suite | Ergebnis |
|---|---:|
| Root strict collection | 6359 gesammelt, 0 Collection-Fehler |
| Root Vollsuite | 6129 passed, 232 skipped, 4 warnings |
| VikingBot standalone | 271 passed, 4 warnings |
| Legacy-/Config-/Boundary-Fokus | 268 passed, 3 skipped |
| Integration/storage/rerank-Fokus | 420 passed, 2 skipped |
| Storage vollständig | 395 passed, 2 skipped |
| AGFS-Smoke/Lifecycle | 5 passed / 2 passed |

## Warning-Analyse

Die vier Warnungen je Lauf kommen aus `lark_oapi` (`utcfromtimestamp`,
Event-Loop-Erkennung, `websockets.InvalidStatusCode`) und dem
`websockets.legacy`-Kompatibilitätsmodul. Keine davon ist eine lokale
Collection-Warning. Eine Behebung erfolgt nur über eine separat getestete
Dependency-Aktualisierung, nicht durch Unterdrückung im Projekt.

## Nicht ausgeführt

OpenClaw-P0/Service, Codex-H1/H2 und Provider-Live wurden nicht ausgeführt.
Ihnen fehlt die separat genehmigte Live-Phase; sie sind HOLD/NOT RUN und nicht
Teil des Offline-PASS.
