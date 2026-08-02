# Session Transfer Protocol — Lark/WebSockets Compatibility

**Stand:** 2026-08-02
**Worktree:** `/Volumes/ExtremePro/projects/OpenViking-agent-worktrees/20260801-open-items-completion`
**Branch:** `agent-workflow/20260802-live-gates-execution`
**Remote:** `https://github.com/manni07/OpenViking.git`
**Lokaler CI-Runner:** `/Volumes/ExtremePro/projects/local-ci-gate`

Der Fork-PR #8 ist verifiziert geschlossen: Merge-Commit
`373aa383511a62a8178208511c60b655ea406dfa` auf `manni07/OpenViking:main`.

## Erledigt

- RED/GREEN-Tests für Lark-WebSockets und Uvicorn-SansIO ergänzt.
- `lark-oapi>=1.7.1,<2.0`, `uvicorn>=0.51.0` und
  `websockets>=13.0,<16` festgeschrieben.
- Lockfile auf `1.7.1`/`0.52.1`/`15.0.1` aktualisiert.
- OpenViking- und VikingBot-Server wählen `websockets-sansio`.
- Installationshinweise und lokales Gate angepasst.
- Frischer Subprozess-Regressionstest für die zwei bekannten Lark-Upstream-
  Warnungen ergänzt; Warnungsfilter und `site-packages`-Änderungen bleiben
  ausgeschlossen.

## Noch ausstehend

- H1 ist PASS. Der disposable OpenClaw-Service und der echte read-only MCP-
  Handshake sind PASS; der mutierende/stale OpenClaw-P0-Harness bleibt HOLD.
- H2 und Provider-/Feishu-Live benötigen weiterhin den jeweils konkreten
  Corpus bzw. Ziel-/Credential-/Kostenrahmen. Die fehlenden Felder sind im
  Live-Gate-Plan als ausführbare nächste Schritte benannt.
- Zwei Upstream-Lark-Warnungen bleiben sichtbar und ungefiltert; sie sind im
  Evidence-Ledger mit Provenienz und Exit-Kriterium erfasst.

Der lokale Voll-Lauf ist abgeschlossen: `git-diff-check`,
`lark-websockets-compatibility`, `collection-fixture-regressions`,
`root-offline-suite` und `bot-standalone-suite` sind PASS. Root: `6167 passed,
246 skipped, 1` upstream Lark-Warnung; Bot: `271 passed, 2` upstream
Lark-Warnungen. Der Word-Parser-Test-Helfer verwendet einen lokalen
`asyncio`-Proxy, damit keine fremden `to_thread`-Aufrufe in die Testzählung
gelangen.

## Stop-Regeln

Kein Provider-/Feishu-Aufruf, kein mutierender OpenClaw-P0-Lauf und kein
Restart von Rechner, Server, Runtime, Container oder bestehendem Service.
