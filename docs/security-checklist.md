# Security Checklist

Status reflects repository evidence, not a formal penetration test.

| Control | Status | Evidence / next action |
| --- | --- | --- |
| Secrets excluded from Git | Implemented locally | `.gitignore`, blank production template, `scripts/security_audit.py` |
| Production auth secret validation | Implemented | backend runtime rejects missing, local-default, or short secrets |
| Password policy and login lockout | Implemented baseline | backend auth tests |
| User data scoping | Implemented baseline | authenticated dependencies and user-isolation test |
| Demo reset disabled in production | Implemented | production guard and API regression test |
| CORS | Local-only baseline | Replace fixed localhost origins with an explicit hosted allowlist |
| Token lifetime | Configurable baseline | Define beta TTL; refresh sessions and revocation remain open |
| Password recovery | Not implemented | Required before public launch |
| General API rate limiting | Not implemented | Add at the hosted edge after expected traffic is known |
| TLS | Not provisioned | Required for hosted beta |
| Dependency audit | Local npm audit available | Add Python and image scanning to the hosted release gate |
| Debug mode disabled | Implemented by current startup commands | Reverify deployed process arguments |
| Database network isolation | Planned | Keep MySQL private in hosted topology |
| Encrypted off-host backups | Planned | Required before customer data |
| Security incident intake | Planned | Name private contact and response owner |

## Release Gate

Before hosted beta:

- Run repository secret, dependency, and image scans.
- Verify HTTPS redirect and secure response headers at the public edge.
- Confirm only dashboard and backend API are public.
- Test authentication failures, user isolation, demo-reset production blocking, and backup restore isolation.
- Record accepted risks with owners and dates.
