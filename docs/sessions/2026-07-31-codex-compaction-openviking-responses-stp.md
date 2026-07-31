# Session Transfer Protocol: Legacy-VLM-Reparatur

**Stand:** 2026-07-31
**Status:** FINALER WORKFLOW-HOLD / SECURITY-VETO / KEIN SOURCE-UNLOCK
**Workflow:** `$tccode`, `thorough`, `critical`; Agent Workflow v4
**Verknuepfte offene Punkte:**
[Open-Item-Bericht](2026-07-31-codex-compaction-openviking-responses-open-items.md)

Dieses Dokument ist der normative, restartbare Abschluss des aktuellen
Legacy-VLM-Laufs. Historische Aussagen in ARD, TRD, ID, TD, Diary oder einer
aelteren STP-Fassung, wonach Security Revision 2 einen Offline-Source-Unlock
erteilt habe, sind fuer diesen Follow-up **superseded**. Sie duerfen nicht als
aktuelle Clearance verwendet werden.

## 1. Autoritative Repository-Identitaet

| Feld | Exakter Wert |
|---|---|
| Repository | OpenViking |
| Worktree | `/Volumes/ExtremePro/projects/OpenViking-agent-worktrees/20260731-legacy-vlm-repair` |
| Branch | `agent-workflow/20260731-legacy-vlm-repair` |
| Base | `2b6dea0a73bf986f1e5f118a0e85893e3b614adf` |
| Arbeitsmodus | isolierter, nicht aktivierter Kandidat |

Vor einer spaeteren Fortsetzung sind Worktree, Branch und Base read-only zu
verifizieren. Bei Drift gilt HOLD; nicht rebasen, mergen, resetten oder fremde
Aenderungen bereinigen.

## 2. Finales Security-Gate

| Security Revision 3 | Ergebnis |
|---|---|
| Score | `89/100` |
| Critical | `0` |
| High | `1` |
| Medium | `1` |
| H1 | **NOT CLOSED** |
| H2 bis H5 | **CLOSED** auf Design-/Testvertragsebene |
| Urteil | **VETO / HOLD** |
| Source-Unlock | **NICHT ERTEILT** |

Die einzige offene Security-High-Luecke ist H1: Der markierte native
Stream-Test assertiert das Langfuse-Update nicht exakt. Es fehlen fuer diesen
Pfad die verbindlichen Assertions fuer:

- `output == "VLM response interrupted after partial output."`;
- `metadata.error == "partial_stream_non_retryable"`;
- keine weiteren Metadaten ausser der normativ optionalen `response_id`;
- eine eigene Variante, die genau diese `response_id`-only-Erweiterung prueft.

Damit koennte eine Implementierung ohne natives Stream-Langfuse-Update oder mit
zusaetzlichen nicht geheimen Metadaten den bisherigen Test bestehen. H2 bis H5
wurden im finalen Review nicht abgeschwaecht. Es gibt in diesem Lauf keine
Revision 4 und keinen weiteren Test-/Designzyklus.

### Sichere Wiederaufnahme des Sourcepfads

Der Sourcepfad darf nur wieder aufgenommen werden, wenn alle folgenden
Bedingungen gleichzeitig erfuellt sind:

1. neue ausdrueckliche User-Autorisierung zum Wiedereroeffnen des Sourcepfads;
2. korrigierter, exakter H1-Testvertrag fuer Chat und nativen Stream,
   einschliesslich Langfuse-`output`, `metadata.error` und der ausschliesslich
   erlaubten optionalen `response_id`;
3. neues Security-Urteil mit mindestens `90/100`, `0 Critical` und `0 High`.

Bis dahin: kein Sourcecode, keine weitere Testrevision und kein Source-Writer.

## 3. Finale Testevidenz dieses Laufs

Exakt sechs bekannte Testdateien wurden im RED-Vertrag bearbeitet:

1. `tests/unit/test_codex_vlm.py`;
2. `tests/unit/test_kimi_glm_vlm.py`;
3. `tests/unit/test_model_retry.py`;
4. `tests/unit/test_stream_config_vlm.py`;
5. `tests/unit/test_vikingbot_vlm_adapter_retry.py`;
6. `tests/unit/test_vlm_failover.py`.

Final beobachtet:

```text
266 collected
129 PASS
137 fachliche RED/FAIL
0 ERROR
0 SKIP
0 XFAIL
4 bestehende Pydantic-Warnungen
py_compile: PASS
git diff --check: PASS
alle sechs Testdateien: jeweils <1000 Zeilen
```

Die 137 Fehler sind fachliche RED-Evidenz fuer noch fehlende Produktion, keine
Import-, Syntax-, Fixture- oder Harnessfehler. Die bereits ohne neue Produktion
gueltigen deep-all-safe/cyclic-safe H3-Faelle waren 16/16 GREEN. Die saubere
RED-Evidenz hebt das Security-VETO nicht auf.

Es wurde **keine Source-Datei geaendert**. Ein Source-Writer wurde nie
gestartet. Die vorhandenen Dossier-, Diary- und Testaenderungen sind fremde
beziehungsweise vorbestehende Workflow-Aenderungen und duerfen bei einer
Fortsetzung nicht still verworfen werden.

## 4. MCP-Evidenz, eng begrenzt

Die aktuelle, akzeptierte read-only Evidenz lautet exakt:

```text
health: OpenViking is healthy (service initialized, storage: VikingFS)
search_experience(query legacy..., limit=1): genau 1 Ergebnis
write operations: 0
restarts: 0
```

Zulaessige Aussage: Am dokumentierten Pruefpunkt funktionierten der gemeinsame
OpenViking-MCP-Health-Pfad und ein echter read-only `search_experience`-Aufruf
ohne Write oder Restart.

Nicht zulaessig sind aktuelle Behauptungen ueber 18 Tools oder drei Ergebnisse.
Der MCP-PASS beweist ausserdem weder Codex-Responses-Capabilities noch
`context_management`, Compaction-Items, Replay, Provider-Egress, Canary,
Source-Unlock, Aktivierung oder Promotion. Fuer eine spaetere
Freshness-Behauptung muessen Health und derselbe read-only Aufruf erneut ohne
Write oder Restart verifiziert werden.

## 5. Live-Provider-Gate

Der User hat den Live-Provider-Test vertagt. Provider-, Capability- und
Canary-Nachweise bleiben **HOLD**. In diesem Lauf gab es keinen Live-Request.

Eine spaetere Wiederaufnahme erfordert vor dem ersten Request:

- ausdrueckliche User-Wiederaufnahme;
- exakter HTTPS-Allowlist-Origin
  `https://chatgpt.com/backend-api/codex`;
- genau ein Credential-Slot-Fingerprint;
- fixes Modell, fixer Visionmodus und fixe Capabilitymenge;
- numerische Limits fuer Gesamtrequests, Output-Tokens, Bildbytes und
  Gesamtkosten;
- Provider-Retry `0` und Failover `0`.

Erst nach positivem lokalem Gate duerfen ein begrenzter Capability-Probe und
Canary erfolgen. MCP-Evidenz darf diesen Provider-Nachweis nicht ersetzen.

## 6. Autoritaet und harte Verbote

Der User hat Commit, Push und Draft-PR fuer eine spaetere, separate
`tccode.git`-Phase autorisiert. Diese Autoritaet gilt nicht fuer diesen
Session-Transfer und hebt keine fachlichen Gates auf.

Verbindlich:

- Commit, Push und Draft-PR: spaeter in `tccode.git` zulaessig, erst nach
  sauberer Scope-/Gate-Pruefung;
- Merge: strikt verboten;
- Aktivierung und Default-Promotion: verboten;
- Rechner-, Server-, Runtime-, Container-, Service- oder Prozess-Restart:
  ohne ausdrueckliche Bestaetigung verboten;
- Sourceaenderung und Live-Calls: unter dem aktuellen VETO verboten.

## 7. Exakte sichere Reproduktionsbefehle

Diese Befehle enthalten keine geheimen Werte. Sie sind fuer eine spaeter
autorisierte Wiederaufnahme dokumentiert und wurden in dieser
Session-Transfer-Rolle nicht erneut ausgefuehrt.

### 7.1 Identitaet, Status und Diff

```bash
cd /Volumes/ExtremePro/projects/OpenViking-agent-worktrees/20260731-legacy-vlm-repair
git status --short --branch
git branch --show-current
git merge-base HEAD 2b6dea0a73bf986f1e5f118a0e85893e3b614adf
git diff --stat
git diff --name-only
```

Erwartung: Branch exakt `agent-workflow/20260731-legacy-vlm-repair`; die
vorhandenen fremden Aenderungen bleiben sichtbar und unberuehrt.

### 7.2 Zwei semantische Provider-GREEN-Faelle

```bash
PYTHONPATH=.:bot:/tmp/openviking-codex-responses-test-deps-20260731 \
  /Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m pytest \
  -q -o addopts= \
  tests/unit/test_codex_vlm.py::test_vlm_config_default_provider_resolves_codex \
  tests/unit/test_kimi_glm_vlm.py::test_vlm_config_uses_canonical_provider_names
```

Erwartung der finalen Evidenz: beide Providerfaelle GREEN; keine
Produktionsaenderung an `vlm_config.py`.

### 7.3 Sechs-Datei-Inventar und fachlicher RED-Lauf

```bash
PYTHONPATH=.:bot:/tmp/openviking-codex-responses-test-deps-20260731 \
  /Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m pytest \
  --collect-only -q -o addopts= \
  tests/unit/test_codex_vlm.py \
  tests/unit/test_kimi_glm_vlm.py \
  tests/unit/test_model_retry.py \
  tests/unit/test_stream_config_vlm.py \
  tests/unit/test_vikingbot_vlm_adapter_retry.py \
  tests/unit/test_vlm_failover.py

PYTHONPATH=.:bot:/tmp/openviking-codex-responses-test-deps-20260731 \
  /Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m pytest \
  -q -o addopts= \
  tests/unit/test_codex_vlm.py \
  tests/unit/test_kimi_glm_vlm.py \
  tests/unit/test_model_retry.py \
  tests/unit/test_stream_config_vlm.py \
  tests/unit/test_vikingbot_vlm_adapter_retry.py \
  tests/unit/test_vlm_failover.py
```

Erwartung vor Source-Unlock: `266 collected = 129 PASS + 137 fachliche FAIL`,
`0 ERROR`, `0 SKIP`, `0 XFAIL`, vier bestehende Pydantic-Warnungen. Eine
abweichende Collection-Zahl ist zuerst als Inventardrift zu klaeren.

### 7.4 Syntax, Whitespace und Dateigroessen

```bash
/Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m py_compile \
  tests/unit/test_codex_vlm.py \
  tests/unit/test_kimi_glm_vlm.py \
  tests/unit/test_model_retry.py \
  tests/unit/test_stream_config_vlm.py \
  tests/unit/test_vikingbot_vlm_adapter_retry.py \
  tests/unit/test_vlm_failover.py

git diff --check

wc -l \
  tests/unit/test_codex_vlm.py \
  tests/unit/test_kimi_glm_vlm.py \
  tests/unit/test_model_retry.py \
  tests/unit/test_stream_config_vlm.py \
  tests/unit/test_vikingbot_vlm_adapter_retry.py \
  tests/unit/test_vlm_failover.py
```

Erwartung: `py_compile` PASS, `git diff --check` PASS und jede Testdatei unter
1000 Zeilen.

## 8. Stopregeln

Sofort STOP/HOLD bei einem der folgenden Punkte:

1. Source-, Config-, Dependency-, Lock- oder Git-Index-Aenderung waere noetig;
2. ein Live-, Capability- oder Canary-Request waere noetig;
3. Merge, Aktivierung oder Promotion waere noetig;
4. ein Rechner, Server, Runtime, Container, Service oder Prozess muesste neu
   gestartet werden;
5. Worktree, Branch oder Base stimmen nicht exakt mit Abschnitt 1 ueberein;
6. fremde Aenderungen koennten nicht erhalten werden;
7. die Security-Luecke H1 ist nicht exakt geschlossen oder das neue Urteil
   erreicht nicht mindestens `90/100` bei `0C/0H`.

## 9. Restartbare naechste Reihenfolge

1. Identitaet und fremde Aenderungen mit Abschnitt 7.1 read-only pruefen.
2. Dieses STP und den
   [Open-Item-Bericht](2026-07-31-codex-compaction-openviking-responses-open-items.md)
   als aktuelle Gate-Quelle lesen.
3. Keine Sourcearbeit beginnen. Fuer eine Wiedereroeffnung zuerst ausdrueckliche
   User-Autorisierung einholen.
4. Danach ausschliesslich den fehlenden H1-Testvertrag korrigieren und erneut
   durch Security bewerten lassen; Source-Unlock nur bei `>=90`, `0C/0H`.
5. Live bleibt unabhaengig HOLD, bis alle Bedingungen aus Abschnitt 5 vorliegen.
6. Erst nach allen fachlichen Gates darf `tccode.git` Commit, Push und Draft-PR
   vorbereiten. Merge, Aktivierung, Promotion und Restart bleiben verboten.

## 10. Aktueller Abschluss

Der enge MCP-read-only-Nachweis ist PASS. Der Live-Provider-Nachweis ist HOLD.
Security Revision 3 ist VETO/HOLD. Es gibt keinen Source-Unlock, keinen
Source-Diff, keinen Live-Call und keinen Restart. Dieser Lauf endet fail-closed.
