# Backup And Restore MVP

Issue 32 adds a non-destructive backup and restore drill baseline for the local MySQL-backed MVP.

## Scope

- Create a local SQL backup from the `mysql` Docker Compose service.
- Verify that the backup file exists, contains schema definitions, and does not contain destructive statements.
- Document a restore drill that targets a temporary database or throwaway environment.

No cloud account, paid API, external storage provider, or AWS resource is required for this issue.

## Non-Destructive Rule

The repository does not include an automatic restore script that overwrites the current `ordostack` database.

Any real restore that deletes, truncates, drops, or overwrites existing data must be approved manually before it is executed. The operator must explicitly identify the target database and the data that will be replaced.

## Backup

Start the local stack first:

```powershell
docker compose up --build -d
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\backup_mysql.ps1
```

Linux / WSL:

```bash
bash scripts/backup_mysql.sh
```

The scripts write SQL files under:

```text
artifacts/backups/
```

`artifacts/` is ignored by Git, so generated backup files are not committed.

## Backup Verification

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify_mysql_backup.ps1 -Path artifacts\backups\ordostack-YYYYMMDD-HHMMSS.sql
```

Linux / WSL:

```bash
bash scripts/verify_mysql_backup.sh artifacts/backups/ordostack-YYYYMMDD-HHMMSS.sql
```

Expected result:

- `status` is `ok`.
- Backup file size is greater than zero.
- SQL contains schema definitions.
- SQL does not contain `DROP DATABASE`, `DROP TABLE`, or `TRUNCATE TABLE`.

## Restore Drill

The MVP restore drill must use a temporary target. Do not restore into the active `ordostack` database during QA.

Recommended drill flow:

1. Create a backup using the command above.
2. Verify the backup using the verification script.
3. Start a temporary MySQL container or use a disposable database name.
4. Restore the SQL into the temporary target only.
5. Inspect table count and a sample row count.
6. Destroy the temporary target after review.

Example target naming:

```text
ordostack_restore_drill_YYYYMMDD
```

The exact restore command depends on the target environment and is intentionally not automated in this repository because production restore is a high-risk operation.

## Production Notes

Before production launch, replace this MVP baseline with:

- Encrypted off-host backups.
- Scheduled backup jobs.
- Restore drill runbook with named owner and approval steps.
- Recovery point objective and recovery time objective.
- Retention policy.
- Backup integrity monitoring.
- Access logging for backup artifacts.

Minimum production backup policy:

- Encryption: every backup artifact must be encrypted before leaving the host.
- Off-host storage: at least one backup copy must be stored outside the application host.
- Retention: define daily, weekly, and monthly retention windows before private beta.
- Approval: any restore into a live database requires explicit written approval naming the target database and data that will be replaced.
- Restore isolation: every routine restore drill must use a temporary target, never the active production database.
