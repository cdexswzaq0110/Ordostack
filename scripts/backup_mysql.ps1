param(
    [string]$OutputDirectory = "artifacts/backups",
    [string]$Database = $(if ($env:DB_NAME) { $env:DB_NAME } else { "ordostack" }),
    [string]$User = $(if ($env:DB_USER) { $env:DB_USER } else { "root" }),
    [string]$Password = $(if ($env:DB_PASSWORD) { $env:DB_PASSWORD } else { "" }),
    [string]$ComposeService = "mysql"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repositoryRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$backupDirectory = Join-Path $repositoryRoot $OutputDirectory
New-Item -ItemType Directory -Force -Path $backupDirectory | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupPath = Join-Path $backupDirectory "ordostack-$timestamp.sql"

$dockerArguments = @(
    "compose",
    "exec",
    "-T"
)

if ($Password -ne "") {
    $dockerArguments += @("-e", "MYSQL_PWD=$Password")
}

$dockerArguments += @(
    $ComposeService,
    "mysqldump",
    "--single-transaction",
    "--routines",
    "--events",
    "--skip-add-drop-table",
    "--skip-comments",
    "--no-tablespaces",
    "-u",
    $User,
    $Database
)

$dumpOutput = & docker @dockerArguments
if ($LASTEXITCODE -ne 0) {
    throw "mysqldump failed with exit code $LASTEXITCODE"
}

$dumpOutput | Set-Content -Path $backupPath -Encoding UTF8
$backupFile = Get-Item -Path $backupPath
if ($backupFile.Length -le 0) {
    throw "Backup file is empty: $backupPath"
}

[PSCustomObject]@{
    status = "ok"
    database = $Database
    path = $backupFile.FullName
    bytes = $backupFile.Length
} | ConvertTo-Json
