param(
    [ValidateSet("flow", "security", "xlsx", "all")]
    [string]$TagSet = "all",
    [string]$DatabaseName = "trae_autoinfo_hr_expense_cash_tracking_test",
    [string]$OdooRoot = "C:\odoo\odoo-15.0",
    [switch]$KeepDb
)

$ErrorActionPreference = "Stop"

$pythonPath = Join-Path $OdooRoot ".venv\Scripts\python.exe"
$odooBinPath = Join-Path $OdooRoot "src\odoo-bin"
$configPath = Join-Path $OdooRoot "odoo.test.conf"
$dataDir = Join-Path $PSScriptRoot ".odoo_test_data"

$addonsPaths = @(
    (Join-Path $OdooRoot "src\addons"),
    (Join-Path $OdooRoot "src\odoo\addons"),
    "C:\odoo\addons_autoinfo\custom15_autoinfo",
    "C:\odoo\addons_autoinfo\odoo15_apps_oca_server_ux",
    "C:\odoo\addons_autoinfo\odoo15_mods_accounting",
    "C:\odoo\addons_oca\reporting-engine-src"
)

$missingPaths = @()
foreach ($path in @($pythonPath, $odooBinPath, $configPath) + $addonsPaths) {
    if (-not (Test-Path $path)) {
        $missingPaths += $path
    }
}

if ($missingPaths.Count -gt 0) {
    Write-Error ("Missing required path(s):`n- " + ($missingPaths -join "`n- "))
}

if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir | Out-Null
}

$testTags = switch ($TagSet) {
    "flow" { "expense_cash_tracking_flow" }
    "security" { "expense_cash_tracking_security" }
    "xlsx" { "expense_cash_tracking_xlsx" }
    "all" {
        "expense_employee_ux,expense_cash_tracking_flow,expense_cash_tracking_security,expense_cash_tracking_xlsx"
    }
    default { $null }
}

function Remove-PostgresDatabaseIfExists {
    param(
        [string]$PythonPath,
        [string]$DbName
    )

    $script = @"
import os
import psycopg2

db_name = os.environ["TRAE_TEST_DB"]
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="odoo",
    password="odoo",
    dbname="postgres",
)
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
exists = cur.fetchone()
if exists:
    cur.execute(
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
        "WHERE datname = %s AND pid <> pg_backend_pid()",
        (db_name,),
    )
    cur.execute('DROP DATABASE "%s"' % db_name.replace('"', '""'))
cur.close()
conn.close()
"@
    $scriptPath = Join-Path $env:TEMP "trae_drop_test_db.py"

    $env:TRAE_TEST_DB = $DbName
    try {
        [System.IO.File]::WriteAllText($scriptPath, $script)
        & $PythonPath $scriptPath | Out-Null
    } finally {
        Remove-Item $scriptPath -ErrorAction SilentlyContinue
        Remove-Item Env:\TRAE_TEST_DB -ErrorAction SilentlyContinue
    }
}

Write-Host "Preparing test database: $DatabaseName"
Remove-PostgresDatabaseIfExists -PythonPath $pythonPath -DbName $DatabaseName

$odooArgs = @(
    $odooBinPath
    "-c"
    $configPath
    "--addons-path=$($addonsPaths -join ',')"
    "--data-dir=$dataDir"
    "-d"
    $DatabaseName
    "-i"
    "autoinfo_hr_expense_cash_tracking"
    "--test-enable"
    "--without-demo=all"
    "--stop-after-init"
)

if ($testTags) {
    $odooArgs += @("--test-tags", $testTags)
}

Write-Host "Running Odoo tests with tag set: $TagSet"

try {
    & $pythonPath @odooArgs
    $exitCode = $LASTEXITCODE
} finally {
    if (-not $KeepDb) {
        Write-Host "Cleaning test database: $DatabaseName"
        Remove-PostgresDatabaseIfExists -PythonPath $pythonPath -DbName $DatabaseName
    }
}

exit $exitCode
