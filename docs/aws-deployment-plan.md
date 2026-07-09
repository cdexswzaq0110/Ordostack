# AWS Deployment Plan

This is a future deployment plan. The repository does not provision AWS resources, DNS, TLS, monitoring, or production credentials.

## Private Beta Target

The minimum credible AWS beta is a single Linux EC2 instance running the existing Compose services behind an Application Load Balancer or Nginx with HTTPS. Use RDS MySQL when operational ownership and budget allow; otherwise keep MySQL on the instance only for a time-limited beta with encrypted off-host backups.

```text
Route 53 -> TLS / ALB -> web-dashboard + backend-api
                              |-> internal scheduler-service
                              |-> internal ml-service
                              `-> RDS MySQL or private MySQL volume
CloudWatch <- logs, health alarms, host metrics
S3 <- encrypted database backups
Secrets Manager / SSM <- production secrets
```

Only the dashboard and backend API may be public. MySQL, scheduler-service, and ml-service remain private.

## Deployment Sequence

1. Build immutable service images from a tagged commit and scan them.
2. Store images in ECR.
3. Create a private network path for internal services and the database.
4. Store `AUTH_TOKEN_SECRET` and database credentials outside Git.
5. Apply Alembic migrations as a release step before serving traffic.
6. Start services, verify readiness, then enable load-balancer traffic.
7. Run the hosted smoke flow from `docs/deployment.md`.
8. Enable alarms and backup jobs before entering customer data.

## Required Environment Separation

| Environment | Data | Credentials | Public traffic |
| --- | --- | --- | --- |
| Local demo | Seed/demo only | Local defaults | No |
| Beta/staging | Synthetic or approved beta data | Separate beta secrets | Restricted |
| Production | Customer data | Production-only secrets | Approved launch only |

Never reuse databases, auth secrets, or backup buckets between environments.

## Monitoring And Backup

- Probe dashboard, backend readiness, scheduler readiness, and ML readiness every 60 seconds.
- Alert after three failures and on sustained 5xx rates.
- Keep application logs free of request bodies, auth headers, cookies, and secrets.
- Encrypt backups, store them off-host, define retention, and test restore into a temporary database.

The detailed policies remain in `docs/observability.md` and `docs/backup-restore.md`.

## Rollback

- Keep the previous image tag and deployment definition.
- Do not automatically downgrade destructive database migrations.
- If a release fails before a schema change, restore the previous images.
- If a migration changes stored data, stop traffic and follow the approved backup/restore runbook.

## Exit Gate

AWS deployment is not complete until HTTPS, secret retrieval, migration execution, readiness, smoke tests, alarms, backup creation, isolated restore, and rollback have all been demonstrated and recorded.
