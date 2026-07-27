# Session Transfer Protocol: Security Hardening

**Erstellt:** 2026-07-27
**Arbeitszweig:** `agent-workflow/20260727-security-hardening`
**Basis-Commit:** `60ef45d4c3a7d07ceb1df4e9d7dde7a14449ac50` (`origin/main`)
**Arbeitsbaum:** `/Volumes/ExtremePro/projects/OpenViking-agent-worktrees/20260727-security-hardening`
**Ziel:** P0-P2-Härtung aus `docs/audit/2026-07-27-security-audit-main.md`; keine Produktion, kein Server- oder Rechnerneustart.

## Übergabestatus

Die Änderungssätze implementieren die geplanten P0/P1-Maßnahmen: Markdown-Link-Sanitizing im Web Studio und Graph-HTML, ein 16-MiB-WebDAV-Body-Limit, fail-closed Regeln für öffentliche CORS-/Basis-URL-Konfiguration, kompatible Abhängigkeitsaktualisierungen sowie eine neue CI für Dependency-Audits. Die wesentlichen Dossiers befinden sich hier:

| Artefakt | Zweck |
|---|---|
| `docs/audit/2026-07-27-security-audit-main.md` | Ausgangsbefunde auf synchronisierter Main-Basis |
| `docs/dossiers/ARD_security_hardening_2026-07-27.md` | Ziele, Grenzen, Risiken und Akzeptanzkriterien |
| `docs/dossiers/TRD_security_hardening_2026-07-27.md` | technische Verträge |
| `docs/plan/PD_security_hardening_2026-07-27.md` | QWF und Phasen |
| `docs/dossiers/ID_security_hardening_2026-07-27.md` | Dateiebene und Rollback |
| `docs/dossiers/SIM_security_hardening_2026-07-27.md` | theoretische Gate-Simulation |
| `docs/tests/TD_security_hardening_2026-07-27.md` | Testmatrix und Soll-Kommandos |
| `docs/openitem/Security_Hardening_Open_Items_2026-07-27.md` | Rest- und Blockerrisiken |

## Wiederaufnahme ohne Kontextverlust

```sh
cd /Volumes/ExtremePro/projects/OpenViking-agent-worktrees/20260727-security-hardening
git status --short
git diff --check
git diff -- docs/dossiers docs/plan docs/tests docs/openitem docs/sessions docs/diaries docs/manuals docs/vision
```

Prüfe zuerst, dass nur erwartete Änderungen auf diesem Zweig vorhanden sind. Nicht den Arbeitsbaum des Nutzers oder seine Recovery-Stashes zurücksetzen, anwenden oder löschen. Für den Rücksprung dieser Härtungsserie ist ein normaler Git-Revert des späteren einzelnen Härtungs-Commits vorgesehen; es gibt keine Schema- oder Datenmigration.

## Verifikationsfolge

Die folgenden Kommandos sind absichtlich explizit. Ein nicht ausgeführter, nicht vorhandener oder fehlschlagender Schritt bleibt offen.

```sh
uv run pytest tests/server/test_api_webdav.py tests/server/test_public_url.py tests/session/memory/test_graph_view.py
uv run pytest tests/test_security_audit_baseline.py
cd web-studio && npm run test -- file-preview.security.test.tsx && npm run lint && npm run build
cd .. && cargo test
uv export --locked --no-hashes --format requirements-txt -o .security-requirements.txt
uv tool run --from pip-audit==2.10.0 pip-audit -r .security-requirements.txt --format json -o .security-pip-audit.json
cargo audit --json > .security-cargo-audit.json
cd bot && npm audit --omit=dev --json > ../.security-bot-npm-audit.json
cd ../web-studio && npm audit --omit=dev --json > ../.security-web-studio-npm-audit.json
cd .. && python scripts/verify_security_audit_baseline.py \
  --baseline .github/security-audit-baseline.json \
  --pip-audit .security-pip-audit.json \
  --cargo-audit .security-cargo-audit.json \
  --npm-audit .security-bot-npm-audit.json bot/package-lock.json \
  --npm-audit .security-web-studio-npm-audit.json web-studio/package-lock.json \
  --scanner-version pip=2.10.0 --scanner-version cargo=0.22.1 --scanner-version npm=11.6.1
```

Vor einem Browser-E2E-Lauf muss eine nicht-sekrete, gültige `ov.conf` vorhanden sein. Vor einem öffentlichen Proxy-Test müssen konkrete HTTPS-Origin(s) und `public_base_url` gesetzt sein. Weder diese Dokumentation noch die Testfolge autorisieren einen Neustart eines Rechners oder Servers.

## Bekannte Grenzen und Stop-Regeln

- Der lokale `pip-audit`-Subprozess endete mit `SIGABRT`; somit ist kein lokaler vollständiger Python-Audit-Nachweis vorhanden.
- Ein kompletter lokaler Suite-Lauf war ohne `ov.conf` nicht möglich.
- Kein Browser-E2E, kein vollständiger Serverstart und kein CI-Lauf werden als erfolgt behauptet.
- `agy` konnte im Headless-Modus wegen Berechtigung nicht als externer Review-Nachweis laufen.
- Die Baseline umfasst 74 Exceptions mit Ablauf **2026-08-27**. Starlette-Major-, Rust-gix/PyO3/RSA/ältere-rustls-webpki- sowie Web-Studio-shadcn- und Bot-Inkompatibilitätswege bleiben in `docs/openitem/` erfasst.

Bei einem neuen Advisory, einer abgelaufenen Ausnahme oder einem Mismatch des Baseline-Verifiers: **anhalten**, Befund und Pfad speichern, keine breite Ignore-Regel einführen und die Kompatibilitätsentscheidung separat dokumentieren.

## Sicherer Git-Hand-off

```sh
git status --short
git diff --check
git diff --name-only
git log --oneline --decorate -5
```

Erst nach Prüfung dieser Ausgaben nur die Dateien dieses Security-Hardening-Zweigs stagen, committen und auf `origin` pushen. Einen Draft-PR erst nach dem tatsächlichen Push erstellen. Dieser STP enthält keine Behauptung, dass Push, PR, CI oder Deployment bereits stattgefunden haben.
