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

**Validierungsstand.** 13 fokussierte Python-Regressionen (Public-URL, exakte und überschreitende WebDAV-Streamgrenze, Baseline-Verifier), 16 Vitest-Fälle sowie Studio-Lint/Build sind grün. Die Dossiers definieren weitere pytest-, npm-, Cargo- und Scanner-Kommandos. Nicht als bestanden behauptet werden: ein lokaler vollständiger Python-Audit (Subprozess `SIGABRT`), eine vollständige Suite ohne gültige `ov.conf`, Browser-E2E/Serverstart, ein CI-Lauf oder ein Deployment. Der angeforderte `agy`-Review war im Headless-Modus nicht berechtigt; dies bleibt ein dokumentierter externer Review-Blocker.

**Restarbeit.** Vor Merge die im STP aufgeführten Kommandos in einer passenden Konfiguration ausführen; jede der 74 Baseline-Ausnahmen vor dem 2026-08-27 entfernen oder erneut explizit bewerten. Kein Rechner- oder Serverneustart wurde ausgeführt oder ist für diese Arbeit angeordnet.

**Betroffener Git-Kontext.** Basis `60ef45d4c3a7d07ceb1df4e9d7dde7a14449ac50`; Arbeitszweig `agent-workflow/20260727-security-hardening` im isolierten Worktree. Ein künftiger Push/PR wird erst nach Status-, Diff- und Testprüfung berichtet.
