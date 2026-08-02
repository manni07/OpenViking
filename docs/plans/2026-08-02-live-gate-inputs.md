# Live-Gate-Eingaben und ausführbare Restschritte

**Stand:** 2026-08-02
**Worktree:** `/Volumes/ExtremePro/projects/OpenViking-agent-worktrees/20260801-open-items-completion`
**Fork:** `manni07/OpenViking`

Dieses Blatt trennt erledigte Nachweise von den wenigen Eingaben, die für
kosten- oder datenträchtige Läufe nicht sicher aus dem Repository ableitbar
sind. Es ersetzt keinen Nachweis durch ein pauschales `HOLD`.

## Bereits festgelegt und verifiziert

| Feld | Wert / Nachweis |
|---|---|
| Codex-Origin | `https://chatgpt.com/backend-api/codex` (OAuth, exakt verwendet) |
| Codex-Modell | `gpt-5.3-codex-spark`; `gpt-5.3-codex` wurde vom Endpunkt abgewiesen |
| Responses-Semantik | `store=false`, kein `conversation`, kein `previous_response_id`, kein Retry/Fallback nach Streambeginn |
| Compaction | `context_management.compact_threshold=1000`; kleinere Werte wurden vom Endpunkt abgewiesen |
| H1-Laufgrenze | 2 Capability-/Replay-Requests plus 1 stateful Canary, pro Request 20 s Client-Deadline |
| State-Grenzen (Default) | 32 MiB, 4096 Items, 256 Turns, 8 Bilder, 8 MiB Bilddaten, 1 MiB pro/4 MiB gesamt Tool-Output, TTL 3600 s, 16 parallele Chains |
| OAuth-Schutz | Token nur aus lokalem Codex-Bootstrap in private `0600`-Datei kopiert; keine Tokenwerte in Logs/Artefakten |
| OpenClaw | temporär `2026.5.27` auf Node `24.11.0`, Plugin `2026.6.18`, Loopback-Gateway `:18999`, Plugin `44/729` Tests PASS, MCP read-only PASS |
| Service-Schutz | Bestehender OpenViking-Dienst `127.0.0.1:1933` und fremde Testprozesse wurden nicht neu gestartet oder beendet |

## Noch auszufüllende H2-Freigabe

Der H2-Benchmark darf erst laufen, wenn diese sechs Werte in einer
sanitisierten Approval-Datei stehen und mit dem Corpus-Hash übereinstimmen:

1. `cost_cap`: Betrag und Währung oder ausdrücklich `0` (kein Kostenrisiko).
2. `max_requests`: harte Obergrenze für alle 20 realen plus 10 synthetischen
   Szenarien einschließlich Wiederholungen.
3. `per_request_timeout_seconds` und `wall_deadline_seconds`.
4. `state_ttl_seconds` für den Benchmark (nicht länger als nötig; der
   Implementierungsdefault ist 3600 s).
5. `corpus_path` und SHA-256 des **sanitisierten** Korpus; produktive
   Transcripts, Credentials und Identifikatoren sind nicht zulässig.
6. `model`/`origin` nochmals explizit bestätigen (abweichende Werte stoppen
   vor dem Netzwerkzugriff).

Praktische, konservative Startwerte wären `max_requests=120`,
`per_request_timeout_seconds=20`, `wall_deadline_seconds=1800` und
`state_ttl_seconds=3600`; sie sind Vorschläge, keine stillschweigende
Freigabe. Ohne Betrag und Corpus-Hash wird kein H2-Netzwerkbenchmark gestartet.

## Noch auszufüllende OpenClaw-P0-Freigabe

Der disposable Service-/Plugin-/MCP-Nachweis ist abgeschlossen. Für den
mutierenden P0-Agentlauf genügt eine einzige zusätzliche Zeile:

```text
P0 freigegeben: Modell=<exakt>, max_agent_calls=1, wall_deadline_seconds=<...>, cost_cap=<...>, read/write scope=<...>
```

Ohne diese Zeile bleibt der Agent-Call aus; der OpenClaw-Gateway-Smoke und der
read-only MCP-Handschlag sind davon nicht abhängig.

## Noch auszufüllende Provider-/Feishu-Freigabe

Für Feishu ist keine Credential-Quelle im Host gefunden worden. Bereitzustellen
sind ausschließlich über einen privaten, temporären Pfad:

- erlaubter HTTPS-Origin (z. B. `https://open.feishu.cn`, falls das die
  tatsächlich freigegebene Tenant-Domain ist);
- Credential-Art: App-/Tenant-Token oder User-OAuth, App-ID/Secret niemals in
  Git/Logs;
- exakte read-only Scopes;
- ein nichtproduktives Fixture (URL/Resource-ID plus SHA-256), maximal ein
  read-only Request;
- `per_request_timeout`, `wall_deadline`, `request_cap=1`, TTL und
  Rollback-/Retention-Entscheidung.

Die ausführbare Freigabezeile lautet:

```text
Feishu freigegeben: origin=<https>, credential=<tenant|user-oauth>, scopes=<read-only>, fixture=<url/id>, sha256=<...>, timeout=<...>, ttl=<...>, retention=<...>
```

Bis dahin werden weder Feishu noch andere Provider-Live-Endpunkte angerufen.

## Hash-/Artefakt-Ledger

Gebauter disposable OpenClaw-Pilot:

| Artefakt | SHA-256 |
|---|---|
| `dist/index.js` | `4e7a89cecb33a227335c6493a0031b6e41cdaae9cf0a99d85d2aa976efcf3c34` |
| `dist/commands/setup.js` | `4465b2b0317c0ecd2faef5d8559d699f8b807260de40db803c4c138d888a6e38` |
| `openclaw.plugin.json` | `0d94af38d72502963a86a9f15dcd2c645ea0d8ba34a4de9906b11835fed912a8` |
| `package.json` | `cbb50444613105ccbd0705f3fd54c3a696490d6fae8d93ca51e8b315a7a08028` |

Nach dem Commit wird der Worktree-Commit zusätzlich in das Evidence-Dossier
eingetragen; bis dahin bleibt der aktuelle Arbeitsstand bewusst `git status`
dirty und wird nicht als unveränderlicher H2-Benchmarkstand ausgegeben.
