# PowerShell script to verify Railway configuration files
# Run this script from the project root directory

Write-Host "Verifying Railway configuration..." -ForegroundColor Cyan
Write-Host ""

$errors = 0
$warnings = 0

# Check railway.json
Write-Host "Checking railway.json..." -ForegroundColor Yellow
if (Test-Path "railway.json") {
    try {
        $railwayConfig = Get-Content "railway.json" | ConvertFrom-Json
        Write-Host "  [OK] railway.json exists" -ForegroundColor Green
        
        if ($railwayConfig.deploy.startCommand) {
            Write-Host "  [OK] Start command configured" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] Start command not found" -ForegroundColor Yellow
            $warnings++
        }
    } catch {
        Write-Host "  [ERROR] Invalid JSON in railway.json" -ForegroundColor Red
        $errors++
    }
} else {
    Write-Host "  [ERROR] railway.json not found" -ForegroundColor Red
    $errors++
}

# Check nixpacks.toml
Write-Host ""
Write-Host "Checking nixpacks.toml..." -ForegroundColor Yellow
if (Test-Path "nixpacks.toml") {
    Write-Host "  [OK] nixpacks.toml exists" -ForegroundColor Green
} else {
    Write-Host "  [WARN] nixpacks.toml not found (Railway will auto-detect)" -ForegroundColor Yellow
    $warnings++
}

# Check backend/requirements.txt
Write-Host ""
Write-Host "Checking backend/requirements.txt..." -ForegroundColor Yellow
if (Test-Path "backend/requirements.txt") {
    Write-Host "  [OK] requirements.txt exists" -ForegroundColor Green
    $reqCount = (Get-Content "backend/requirements.txt" | Measure-Object -Line).Lines
    Write-Host "  [INFO] Found $reqCount dependency lines" -ForegroundColor Gray
} else {
    Write-Host "  [ERROR] backend/requirements.txt not found" -ForegroundColor Red
    $errors++
}

# Check backend/main.py
Write-Host ""
Write-Host "Checking backend/main.py..." -ForegroundColor Yellow
if (Test-Path "backend/main.py") {
    Write-Host "  [OK] main.py exists" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] backend/main.py not found" -ForegroundColor Red
    $errors++
}

# Summary
Write-Host ""
Write-Host "=" * 50
if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "All checks passed! Ready for Railway deployment." -ForegroundColor Green
} elseif ($errors -eq 0) {
    Write-Host "Configuration looks good with $warnings warning(s)." -ForegroundColor Yellow
} else {
    Write-Host "Found $errors error(s) and $warnings warning(s)." -ForegroundColor Red
    Write-Host "Please fix errors before deploying to Railway." -ForegroundColor Red
}
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create Railway account at https://railway.app" -ForegroundColor Gray
Write-Host "2. Create new project from GitHub repository" -ForegroundColor Gray
Write-Host "3. Follow DEPLOYMENT_STEPS.md for detailed instructions" -ForegroundColor Gray

exit $errors

