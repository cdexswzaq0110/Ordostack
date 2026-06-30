# Beta Readiness Review

Issue 53 records the private-beta readiness gate.

## Current Decision

Status: not ready for public launch.

Reason: Docker finalization, hosted deployment execution, production monitoring implementation, production backup automation, and final security review remain open.

Recommended label:

```text
Customer Demo MVP / Technical Preview
```

Next acceptable label after the remaining gates pass:

```text
Private Beta Candidate
```

## 2026-06-30 Verification

Completed in the available Windows environment:

- 60 backend-api tests, 11 scheduler-service tests, and 9 ml-service tests passed.
- Dashboard production build, static accessibility audit, security audit, documentation check, backup policy audit, beta readiness check, and 210 translation keys passed.
- Local E2E smoke passed through auth, task and fixed-event edits, schedule generation, history, rename, comparison, and export.
- Edge browser smoke produced a valid dashboard screenshot; sidebar navigation, demo login, runtime state, and Generate Plan success feedback were also checked interactively.
- Production now blocks the demo-reset endpoint.

Manual verification still required:

- Docker Compose config and clean-checkout startup because Docker is unavailable in the audit environment.
- MySQL persistence across restart, migration execution in Docker, backup creation, and isolated restore drill.
- Reviewed visual-regression baseline and formal manual accessibility sign-off.

The release label remains `Customer Demo MVP / Technical Preview`; these changes do not complete the hosted or Docker private-beta gates.

## Required Gates Before Private Beta

| Gate | Status | Owner | Evidence |
| --- | --- | --- | --- |
| Issue 46 focused QA for Issues 34-45 | Required | QA | `python scripts/release_qa_gate.py` output and manual notes |
| Issue 47 production auth hardening baseline | Complete locally | Engineering | Auth tests and environment docs |
| Issue 48 hosted monitoring baseline | Planned locally | Engineering / PM | `docs/observability.md` |
| Issue 49 production backup automation policy | Planned locally | Engineering / PM | `docs/backup-restore.md` and `python scripts/backup_policy_audit.py` |
| Issue 50 Docker finalization | Deferred | Engineering | Deployment hardening issue |
| Issue 51 hosted beta deployment | Deferred | PM / Engineering | Account and target environment decision |
| Issue 52 manual accessibility QA | Required | QA | `docs/accessibility-qa.md` |
| Security review | Required | Engineering | `python scripts/security_audit.py --root .` plus manual review |
| Product support workflow | Required | PM | Named support owner and escalation path |

## Customer Demo Boundaries

- Use the demo account only for local demonstrations.
- Do not collect real customer personal data in the local MVP.
- Do not claim hosted availability, SLA, mobile support, or managed ML operations.
- Do not enable ClearML credentials until a deliberate MLOps issue is opened.
- Do not run destructive restore commands against the active database.

## Account Decisions Needed Later

No account is needed for the current non-Docker work.

Before Issue 51, decide:

- Hosting target: AWS, another cloud VM, or a private server.
- Domain and TLS ownership.
- Monitoring vendor or self-hosted monitor.
- Off-host backup destination.
- Incident contact route.

## Private Beta Exit Criteria

- All non-Docker release QA gates pass.
- Docker finalization and hosted deployment gates pass.
- Production secrets are configured outside Git.
- Backup restore drill succeeds against a temporary target.
- Monitoring alerts are tested with an intentional failed probe.
- PM approves beta scope, onboarding language, support path, and feedback channel.
