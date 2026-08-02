# Session Transfer Protocol — Lark/WebSockets Compatibility

**Stand:** 2026-08-02
**Worktree:** `/Volumes/ExtremePro/projects/OpenViking-agent-worktrees/20260801-open-items-completion`
**Branch:** `agent-workflow/20260801-open-items-completion`
**Remote:** `https://github.com/manni07/OpenViking.git`
**Lokaler CI-Runner:** `/Volumes/ExtremePro/projects/local-ci-gate`

## Erledigt

- RED/GREEN-Tests für Lark-WebSockets und Uvicorn-SansIO ergänzt.
- `lark-oapi>=1.7.1,<2.0`, `uvicorn>=0.51.0` und
  `websockets>=13.0,<16` festgeschrieben.
- Lockfile auf `1.7.1`/`0.52.1`/`15.0.1` aktualisiert.
- OpenViking- und VikingBot-Server wählen `websockets-sansio`.
- Installationshinweise und lokales Gate angepasst.

## Noch ausstehend

- Commit/Push/PR-Nachweis im Fork;
- zwei upstream Lark-Warnungen bleiben sichtbar und ungefiltert.

Der lokale Voll-Lauf ist abgeschlossen: `git-diff-check`,
`lark-websockets-compatibility`, `collection-fixture-regressions`,
`root-offline-suite` und `bot-standalone-suite` sind PASS. Root: `6164 passed,
246 skipped, 1` upstream Lark-Warnung; Bot: `271 passed, 2` upstream
Lark-Warnungen. Der Word-Parser-Test-Helfer verwendet einen lokalen
`asyncio`-Proxy, damit keine fremden `to_thread`-Aufrufe in die Testzählung
gelangen.

## Stop-Regeln

Keine Live-Provider-/Feishu-Aufrufe, kein OpenClaw-P0, kein H1/H2 und kein
Restart von Rechner, Server, Runtime, Container oder Service.
