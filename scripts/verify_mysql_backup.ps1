param(
    [Parameter(Mandatory = $true)]
    [string]$Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$backupPath = Resolve-Path $Path
$backupFile = Get-Item -Path $backupPath
if ($backupFile.Length -le 0) {
    throw "Backup file is empty: $backupPath"
}

$content = Get-Content -Path $backupPath -Raw
if ($content -notmatch "CREATE TABLE") {
    throw "Backup does not contain schema definitions."
}

$forbiddenPatterns = @(
    "DROP DATABASE",
    "DROP TABLE",
    "TRUNCATE TABLE"
)

foreach ($pattern in $forbiddenPatterns) {
    if ($content -match $pattern) {
        throw "Backup contains forbidden destructive statement: $pattern"
    }
}

[PSCustomObject]@{
    status = "ok"
    path = $backupFile.FullName
    bytes = $backupFile.Length
    contains_schema = $true
    destructive_statements = "none"
} | ConvertTo-Json
