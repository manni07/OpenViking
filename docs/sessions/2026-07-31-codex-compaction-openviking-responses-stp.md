# Session Transfer Protocol: Codex Compaction and OpenViking Responses

**Status:** OFFLINE IMPLEMENTATION VERIFIED / WORKFLOW HOLD / NOT ACTIVATED
**Date:** 2026-07-31
**Workflow:** `$tccode`, thorough, critical; Agent Workflow v4
**Current gate:** Offline implementation, Security-Medium-Follow-up and local
contract tests complete; provider capability, A/B, canary, independent
revalidation and promotion gates remain HOLD

This restartable handoff records the final evidence available in this worktree.
The source-controlled hook candidate and opt-in Responses state adapter are
implemented and pass their deterministic offline suites. They are not installed,
activated, deployed, pushed, merged, canary-tested, or promoted. The isolated
branch contains targeted local commits; no global state was changed. The
private Codex endpoint capability probe and local compaction comparison matrix
were deliberately not run.

## 1. Objective and current scope

The approved work has two independent but ordered lanes:

1. Harden and evaluate local Codex compaction without assuming that the
   ARC-AGI-3 report's 175k threshold applies locally. The verified baseline
   remains `206720` tokens.
2. Add an explicit opt-in OpenViking Responses state path using `store=false`,
   lossless response-item replay, capability-gated compaction, strict chain
   isolation, bounded resources, and unchanged legacy APIs.

The Quick-Win-First order is:

1. hook safety;
2. baseline and endpoint capability probe;
3. local controlled comparison;
4. state contract;
5. tests;
6. adapter;
7. canary;
8. evidence review before any possible promotion.

## 2. Immutable repository identity

| Field | Verified value |
|---|---|
| Repository | OpenViking |
| Isolated worktree | `/Volumes/ExtremePro/projects/OpenViking-agent-worktrees/20260731-codex-compaction-responses` |
| Branch | `agent-workflow/20260731-codex-compaction-responses` |
| Base commit | `60ef45d4c3a7d07ceb1df4e9d7dde7a14449ac50` |
| Initial worktree `HEAD` | `60ef45d4c3a7d07ceb1df4e9d7dde7a14449ac50` |
| Offline-security code `HEAD` | `0556a9aac049d2563893e1abe4068c0260024542` |
| Main checkout | `/Volumes/ExtremePro/projects/OpenViking` |

Do not silently rebase, merge, switch the base, or move implementation into the
main checkout. Any base drift changes the evidence boundary and requires an
explicit review before continuing.

## 3. Dirty-main preservation boundary

At the initial checkpoint the main checkout was on `main...origin/main` and had
the following untracked user-owned material:

- `.serena/`
- `AGENT_MEMORY.md`
- `docs/audit/`
- `docs/sessions/`
- `scripts/start-openviking-ollama.sh`

These paths are outside this implementation worktree's write scope. Do not
delete, move, stage, stash, copy over, reset, or otherwise mutate them. The
isolated worktree exists specifically to preserve this boundary. If an action
would overlap any of these paths in the main checkout, stop and obtain explicit
direction.

At the final evidence checkpoint the main checkout still had exactly this
untracked set and no tracked diff. No main-checkout file was changed by this
implementation.

## 4. Global Codex rollback package

The pre-change rollback package is:

`/Volumes/ExtremeSSD/backups/codex-compaction-20260731-implementation`

Verified metadata:

- owner: `turgay`;
- directory mode: `0700`;
- each backup file mode: `0600`;
- each source hash matched its corresponding backup hash at both the initial and
  final evidence checkpoints.

| File | SHA-256 |
|---|---|
| `config.toml` | `953cd1d789fea9a55a537b7fbb4e47866493e6ad45f87181b9f7ed9f94c5010c` |
| `hooks.json` | `4fe5db6cbad3525c04a2245979acafa98017773067fd62ece5ca3b970f59796d` |
| `session_transfer_precompact.py` | `419cf0eb2f749b93fcb3532daabad9512916c10aa74b4cd626c291e07ff207c3` |

Backup/source mapping:

- backup `config.toml` ↔ `/Users/turgay/.codex/config.toml`;
- backup `hooks.json` ↔ `/Users/turgay/.codex/hooks.json`;
- backup `session_transfer_precompact.py` ↔
  `/Users/turgay/.codex/hooks/session_transfer_precompact.py`.

Do not inspect or record credential values. A hash mismatch, missing file,
ownership change, or permission widening is an immediate HOLD. Rollback must
restore only these exact three files from the verified package; it must not be
implemented with a broad directory copy or destructive Git command.

The final source hashes remained identical to the table. Therefore the active
global Codex baseline stayed at `206720`, scope `total`; neither the global hook
nor the global compaction configuration was changed. The hardened hook exists
only as the worktree candidate
`tools/codex_compaction_hooks/codex_compaction_hook.py`.

## 5. Baseline test evidence

The initial targeted baseline command was:

```bash
PYTHONPATH=/tmp/openviking-codex-responses-test-deps-20260731 \
  /Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m pytest -q \
  tests/unit/test_codex_vlm.py \
  tests/models/vlm/test_timeout_config.py
```

Observed result:

- 30 tests collected;
- 29 passed;
- 1 failed;
- 4 warnings.

The failing test was:

```text
tests/unit/test_codex_vlm.py::test_vlm_config_default_provider_resolves_codex
```

It expected `provider_config == {}`, but the actual mapping contained seven
provider-resolution keys, including `api_base`, `api_key`, `api_version`,
`extra_headers`, and `extra_request_body`. This failure exists at the clean base
and is baseline/pre-existing evidence. It is not evidence that new
implementation passes, and it must not be silently skipped, rewritten, or
reported as green. Any later comparison must distinguish this known baseline
failure from new regressions.

## 6. Final implementation and verification evidence

Completed and verified:

- isolated worktree, branch, base commit, and main-checkout boundary identified;
- global Codex rollback package created before modification;
- backup ownership, modes, and source-to-backup SHA-256 equality verified;
- targeted legacy baseline executed and its single failure retained as evidence;
- source-controlled fail-closed compaction hook candidate implemented;
- hook path validation rejects symlinks at every component from `CODEX_HOME`
  through the private state root, including a symlinked parent component;
- immutable caller-managed Responses state, sync/native-async state methods,
  endpoint binding, integrity tagging, tool-call consumption, resource limits,
  complete-output ledger replay, newest-compaction pruning, and completion-only
  publication implemented additively;
- supported `VLMConfig` propagation added for `responses_state_enabled` and
  `responses_compact_threshold`, with fail-closed enforcement of exactly one
  `openai-codex` credential for the pilot;
- legacy stateless APIs and `VLMBase` were not changed;
- restart and activation prohibitions recorded and observed.

Implementation files in the isolated worktree:

- `tools/codex_compaction_hooks/codex_compaction_hook.py`;
- `openviking/models/vlm/backends/codex_responses_adapter.py`;
- `openviking/models/vlm/backends/codex_auth.py`;
- `openviking/models/vlm/backends/codex_vlm.py`;
- `openviking_cli/utils/config/vlm_config.py`;
- `tests/unit/test_codex_compaction_hook.py`;
- `tests/unit/test_codex_responses_state.py`;
- `tests/unit/test_codex_vlm.py`.

### 6.1 New offline critical suites

Command:

```bash
PYTHONPATH=/tmp/openviking-codex-responses-test-deps-20260731 \
  /Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m pytest -q \
  tests/unit/test_codex_compaction_hook.py \
  tests/unit/test_codex_responses_state.py \
  --no-cov
```

Result: `102 collected`, `102 passed`, `4` pre-existing Pydantic warnings,
`0 skipped`, `0 xfailed`. The parameterized result comprises 30 hook cases and
72 Responses-state/config/security cases.

### 6.2 Combined new and targeted legacy suites

Command:

```bash
PYTHONPATH=/tmp/openviking-codex-responses-test-deps-20260731 \
  /Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m pytest -q \
  tests/unit/test_codex_compaction_hook.py \
  tests/unit/test_codex_responses_state.py \
  tests/unit/test_codex_vlm.py \
  tests/models/vlm/test_timeout_config.py \
  --no-cov
```

Result: `132 collected`, `131 passed`, `1 failed`, `4 warnings`. The only
failure was the clean-base baseline failure at
`tests/unit/test_codex_vlm.py:207`,
`test_vlm_config_default_provider_resolves_codex`, already recorded in section
5. There was no new regression and no silent skip or xfail, but the combined
suite is correctly reported as not fully green.

### 6.3 Expanded configuration regression comparison

Worktree command:

```bash
PYTHONPATH=/tmp/openviking-codex-responses-test-deps-20260731 \
  /Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m pytest -q \
  tests/unit/test_codex_compaction_hook.py \
  tests/unit/test_codex_responses_state.py \
  tests/unit/test_codex_vlm.py \
  tests/models/vlm/test_timeout_config.py \
  tests/unit/test_stream_config_vlm.py \
  --no-cov
```

Result: `152 collected`, `140 passed`, `12 failed`, `4 warnings`.

Clean-main comparison command, run from
`/Volumes/ExtremePro/projects/OpenViking`:

```bash
PYTHONPATH=/tmp/openviking-codex-responses-test-deps-20260731 \
  /Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m pytest -q \
  tests/unit/test_stream_config_vlm.py \
  --no-cov
```

Clean-main result: `20 collected`, `9 passed`, `11 failed`, `4 warnings`.
Those same 11 stream-configuration failures occur in the worktree expanded
suite. Together with the one separately proven Codex provider-config baseline
failure, all 12 expanded-suite failures are pre-existing in the compared set.
The expanded suite therefore shows no new regression, but remains red and HOLD.

### 6.4 Static verification

Commands:

```bash
/Volumes/ExtremePro/pyenv/shims/ruff check \
  tools/codex_compaction_hooks/codex_compaction_hook.py \
  openviking/models/vlm/backends/codex_responses_adapter.py \
  openviking/models/vlm/backends/codex_auth.py \
  openviking/models/vlm/backends/codex_vlm.py \
  openviking_cli/utils/config/vlm_config.py \
  tests/unit/test_codex_compaction_hook.py \
  tests/unit/test_codex_responses_state.py \
  tests/unit/test_codex_vlm.py

/Volumes/ExtremePro/pyenv/shims/ruff format --check \
  tools/codex_compaction_hooks/codex_compaction_hook.py \
  openviking/models/vlm/backends/codex_responses_adapter.py \
  openviking/models/vlm/backends/codex_auth.py \
  openviking/models/vlm/backends/codex_vlm.py \
  openviking_cli/utils/config/vlm_config.py \
  tests/unit/test_codex_compaction_hook.py \
  tests/unit/test_codex_responses_state.py \
  tests/unit/test_codex_vlm.py

/Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m compileall -q \
  tools/codex_compaction_hooks/codex_compaction_hook.py \
  openviking/models/vlm/backends/codex_responses_adapter.py \
  openviking/models/vlm/backends/codex_auth.py \
  openviking/models/vlm/backends/codex_vlm.py \
  openviking_cli/utils/config/vlm_config.py \
  tests/unit/test_codex_compaction_hook.py \
  tests/unit/test_codex_responses_state.py \
  tests/unit/test_codex_vlm.py

git diff --check
```

Results:

- Ruff check: `All checks passed!`;
- Ruff format check: `8 files already formatted`;
- `compileall -q`: PASS;
- `git diff --check`: PASS.

### 6.5 Read-only MCP evidence

The already running shared OpenViking MCP at `127.0.0.1:1933` was checked
without a restart:

- health: healthy, `0.0612s`;
- MCP inventory: 18 tools;
- read-only `search_experience`: 3 results, `0.2280s`;
- embedding HTTP 503 was not observed.

This proves the shared MCP handshake and one read-only tool path. It does not
prove the private Codex Responses endpoint's compaction capability and is not a
state-mode canary.

### 6.6 Security review revision 2

Security revision 2 found no Critical or High issue. The review scored `95.6%`
aggregate with every individual criterion at least `91%`, so the security veto
against an offline-only commit was lifted. The outcome remains provisional
because the requested Claude Opus reviewer was not available.

All three Medium residuals were then closed offline in commits
`325e5cff3895036a2fc0e8a0a93131e77f7c9d0d` and
`0556a9aac049d2563893e1abe4068c0260024542`:

1. **Credential binding without `client_id`:** chains bind to the stable
   credential slot (`credential_slot` or persistent path), while an available
   `client_id` remains an additional binding component.
2. **Cancellation-safe async cleanup:** one shielded cleanup task attempts both
   stream and client close despite repeated cancellation or an earlier close
   failure; the original cancellation retains priority and the chain slot is
   released in the outer `finally`.
3. **Hook TOCTOU/deadline/retention:** I/O stays anchored to validated directory
   FDs; a signal timer enforces the outer five-second deadline; TTL, record and
   scan limits bound retention under process and thread locking.

The corresponding candidate suites now pass 102/102. Activation, independent
security revalidation, provider canary, deployment and promotion remain HOLD.

Still HOLD or pending separate authorization:

- explicit resolution of the pre-existing legacy provider-config test conflict;
- local Codex comparison matrix;
- exact private Codex endpoint capability probe;
- billable/live state canary;
- independent security revalidation before activation.

The Test Dossier and Development Diary contain the final 102/102 candidate
counts, 131/132 core result, and 140/152 expanded result. Sections 6.1 through 6.4 of
this STP retain the exact commands and clean-base comparison boundary.

## 7. Hard stop and HOLD rules

Stop immediately and retain evidence if any of the following occurs:

1. A computer, server, container runtime, process, or service would need a
   restart. No restart is authorized without the user's explicit confirmation.
2. A change would activate global Codex behavior, enable the new OpenViking
   mode by default, deploy, merge, push, or promote a candidate. None of these
   actions is authorized by this handoff.
3. Worktree `HEAD`, branch, or base identity drifts before the planned change is
   reviewed.
4. Main-checkout user material would be modified or a dirty-path overlap cannot
   be isolated.
5. Any rollback file is missing, differs from its recorded hash, has unexpected
   ownership, or has broader permissions.
6. Hook smoke, permission, timeout, symlink, concurrency, event-correlation, or
   prompt-injection tests fail.
7. Implementation simulation is below 95% aggregate or below 90% on any
   individual criterion after at most three revisions.
8. Test simulation is below 95% aggregate or below 90% on any individual
   criterion after at most three revisions.
9. The exact Codex endpoint has not yet proved support for `context_management`,
   compaction items, and replay. The probe may be billable and was not authorized
   in this run. State compaction and canary remain HOLD; unsupported capability
   must fail loudly with no silent fallback.
10. Any state-mode request could use `store=true`, Conversations,
    `previous_response_id`, an unapproved OAuth origin, provider/account
    failover, or a different credential inside a chain.
11. A timeout, cancellation, partial stream, replay, stale generation, duplicate
    tool output, limit breach, or error could mutate or publish the prior state.
12. Any sentinel secret appears in logs, traces, dossiers, telemetry, or test
    output.
13. Cross-chain leakage is detected or legacy behavior regresses beyond the
    recorded baseline.
14. A future OpenViking MCP handshake or read-only tool call regresses from the
    recorded healthy result.
15. The embedding dependency returns HTTP 503. It was not observed in this run,
    but remains HOLD if encountered; do not restart
    any dependency or service without confirmation.
16. The security agent exercises its veto.

Failure of a promotion criterion leaves the mode opt-in. Default promotion
requires a separate evidence review and explicit authorization.

## 8. No-restart and no-activation boundary

The following actions are explicitly prohibited in this session unless the user
confirms them after seeing the exact target and reason:

- rebooting or restarting a computer or server;
- stopping or starting a container runtime;
- restarting OpenViking, its embedding dependency, or any shared container;
- killing or restarting a process;
- enabling modified hooks or changing global Codex thresholds;
- deploying or enabling the stateful Responses mode;
- making the opt-in path a default;
- merging, pushing, or opening a PR automatically.

Static edits in the isolated worktree and non-mutating checks remain permissible.
The global Codex files remain unchanged. Installing the candidate hook or
changing the threshold would be a new, separately authorized activation step.

## 9. Safe restart procedure

Run these read-only commands first:

```bash
cd /Volumes/ExtremePro/projects/OpenViking-agent-worktrees/20260731-codex-compaction-responses
git status --short --branch
git rev-parse HEAD
git branch --show-current
git worktree list --porcelain
```

Expected immutable identity before continuation:

```text
HEAD:   0556a9aac049d2563893e1abe4068c0260024542 or a later documentation-only commit
branch: agent-workflow/20260731-codex-compaction-responses
```

Reverify both active global files and the rollback package without reading file
contents:

```bash
shasum -a 256 \
  /Users/turgay/.codex/config.toml \
  /Users/turgay/.codex/hooks.json \
  /Users/turgay/.codex/hooks/session_transfer_precompact.py

shasum -a 256 \
  /Volumes/ExtremeSSD/backups/codex-compaction-20260731-implementation/config.toml \
  /Volumes/ExtremeSSD/backups/codex-compaction-20260731-implementation/hooks.json \
  /Volumes/ExtremeSSD/backups/codex-compaction-20260731-implementation/session_transfer_precompact.py

stat -f '%Sp %Su:%Sg %N' \
  /Volumes/ExtremeSSD/backups/codex-compaction-20260731-implementation \
  /Volumes/ExtremeSSD/backups/codex-compaction-20260731-implementation/config.toml \
  /Volumes/ExtremeSSD/backups/codex-compaction-20260731-implementation/hooks.json \
  /Volumes/ExtremeSSD/backups/codex-compaction-20260731-implementation/session_transfer_precompact.py
```

Then:

1. Confirm the active hashes equal the three backup hashes in section 4.
2. Read the current ARD, TRD, PD, TD, this STP, ID, Diary, Manual, Proposal and
   open-item report before relying on their status.
3. Reconcile every artifact status against `git status`, `git log --oneline`,
   and exact file hashes. Preserve any user-owned worktree change.
4. Rerun the two offline commands in sections 6.1 and 6.2 before changing code.
   The expected results are 102/102 for the new suites and 131/132 combined with
   only the recorded baseline failure. Rerun section 6.3 when changing config;
   compare all 12 failures against the two recorded clean-base baselines.
5. Confirm the current Agent Workflow gate and obtain the missing independent
   security/simulation records.
6. Resolve the legacy test-contract conflict. Do not jump to provider
   capability, canary, activation, or promotion.
7. The private Codex capability probe, A/B corpus, canary, hook installation,
   threshold change, push, PR, merge, and promotion each remain separate gated
   actions. Do not infer authorization from this STP.
8. After a significant step, record the exact command, outcome, changed files,
   blockers, and next gate in this STP and the Development Diary.
9. Before any completion claim, run the full updated Test Dossier, the unchanged
   legacy suite, `git diff --check`, and targeted secret/log-capture checks.
   Report every skipped or infeasible test.

To reproduce the known baseline when the referenced environment is still
available:

```bash
cd /Volumes/ExtremePro/projects/OpenViking-agent-worktrees/20260731-codex-compaction-responses
PYTHONPATH=/tmp/openviking-codex-responses-test-deps-20260731 \
  /Volumes/ExtremePro/projects/OpenViking/.venv/bin/python -m pytest -q \
  tests/unit/test_codex_vlm.py \
  tests/models/vlm/test_timeout_config.py
```

If the temporary dependency path or referenced virtual environment is absent,
record that as an environment blocker; do not install, restart, or change global
dependencies implicitly.

## 10. Artifact checklist

The paths below reflect the final observed worktree state, not planned claims.

| Artifact | Required path or category | Final observed status |
|---|---|---|
| Architecture Requirement Dossier | `docs/dossiers/2026-07-31-codex-compaction-openviking-responses-ard.md` | CURRENT; offline security closure recorded |
| Technical Requirement Dossier | `docs/dossiers/2026-07-31-codex-compaction-openviking-responses-trd.md` | CURRENT; offline security closure recorded |
| Planning Document with QWF | `docs/plan/2026-07-31-codex-compaction-openviking-responses-pd.md` | CURRENT; live gates remain HOLD |
| Implementation Dossier | `docs/dossiers/2026-07-31-codex-compaction-openviking-responses-id.md` | PRESENT; offline candidate, live HOLD |
| Implementation simulation and scoring | ID | PASS: 96.0% aggregate, minimum criterion 92% |
| Test Dossier | `docs/tests/2026-07-31-codex-compaction-openviking-responses-td.md` | CURRENT; 102/102 candidate evidence and baseline HOLD recorded |
| Test simulation and scoring | TD | PASS prerequisite: 97.2% aggregate, each criterion at least 96% |
| Hook-hardening implementation | `tools/codex_compaction_hooks/codex_compaction_hook.py` | IMPLEMENTED; 30/30 cases including Directory-FD, deadline and retention; NOT INSTALLED |
| Codex comparison matrix | sanitized evidence artifact | NOT RUN / HOLD |
| Responses state, adapter, and config propagation | isolated worktree source files | IMPLEMENTED; 72/72 cases; OPT-IN only |
| Unit/contract/legacy results | section 6 | 102/102 new; core 131/132; expanded 140/152, baseline-only failures |
| Security review revision 2 | section 6.6 | Provisional PASS; 95.6%, minimum 91%; 3 Mediums subsequently closed offline |
| Capability-probe evidence | exact approved Codex endpoint | NOT RUN; approval/billing HOLD |
| MCP handshake and read-only call | section 6.5 | PASS; no restart; not a provider canary |
| Open-item report | exactly 3 High, 3 Medium, 3 Low | PRESENT; M1-M3 DONE offline, H1-H3 HOLD |
| Session Transfer Protocol | `docs/sessions/2026-07-31-codex-compaction-openviking-responses-stp.md` | UPDATED / WORKFLOW HOLD |
| Development Diary | `docs/diaries/Development_Diary_v000.md` | CURRENT; final test evidence and no-activation status recorded |
| Project Manual | `docs/manuals/2026-07-31-codex-compaction-openviking-responses-manual.html` | PRESENT; activation remains HOLD |
| Proposal Dossier | `docs/vision/2026-07-31-codex-compaction-openviking-responses-ppd.md` | PRESENT; proposals only |
| Targeted Git commit | isolated branch only | PRESENT; implementation `a84a3730`, security follow-ups `325e5cff` and `0556a9aa` |
| PR | optional and separately authorized | NOT CREATED |
| Merge/default promotion | separate review and authorization | NOT AUTHORIZED |

## 11. Completion criteria not yet met

The requested offline security residual closure is verified. The wider workflow
may not be called complete while the combined suite has the known unresolved
baseline failure, Security Rev2 lacks independent revalidation, and the live/A/B
gates remain unexecuted. Promotion additionally requires:

- no quality regression or critical scenario loss;
- at least 20% lower median output tokens;
- p95 latency no more than 10% worse;
- no higher error rate;
- zero cross-chain leaks;
- 100% passing critical continuity, security, and legacy gates.

The current state meets the offline implementation, security-residual and new
critical-test claims. It does not meet workflow-completion, activation, live
capability, A/B, canary, deployment or promotion claims. Resume with the legacy
contract decision and independent review; retain HOLD on all provider-facing or
activating actions until separately authorized.
