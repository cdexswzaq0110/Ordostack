# Security

## Supported Version

| Version | Status |
| --- | --- |
| `0.51.x` | Local Customer Demo MVP / Technical Preview |

## Reporting

Do not open public issues for secrets, auth bypasses, data exposure, or destructive restore concerns. Use a private channel with the project owner until a hosted security intake address is available.

## Secrets

Never commit:

- `.env`
- `.env.production`
- API keys
- database passwords
- cloud credentials
- ClearML credentials
- private keys
- personal tokens

Run:

```powershell
python scripts\security_audit.py --root .
```

## Known Limits

- Local bearer-token auth exists, but hosted refresh sessions and account recovery are not implemented.
- No hosted monitoring or production incident workflow is configured yet.
- Production secrets must be configured outside Git.
