# PowerShell script to verify Vercel configuration files
# Run this script from the project root directory

Write-Host "Verifying Vercel configuration..." -ForegroundColor Cyan
Write-Host ""

$errors = 0
$warnings = 0

# Check vercel.json
Write-Host "Checking vercel.json..." -ForegroundColor Yellow
if (Test-Path "vercel.json") {
    try {
        $vercelConfig = Get-Content "vercel.json" | ConvertFrom-Json
        Write-Host "  [OK] vercel.json exists" -ForegroundColor Green
        
        if ($vercelConfig.buildCommand) {
            Write-Host "  [OK] Build command configured" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] Build command not found" -ForegroundColor Yellow
            $warnings++
        }
        
        if ($vercelConfig.outputDirectory) {
            Write-Host "  [OK] Output directory configured" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] Output directory not found" -ForegroundColor Yellow
            $warnings++
        }
        
        if ($vercelConfig.framework) {
            Write-Host "  [OK] Framework configured: $($vercelConfig.framework)" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] Framework not specified" -ForegroundColor Yellow
            $warnings++
        }
    } catch {
        Write-Host "  [ERROR] Invalid JSON in vercel.json" -ForegroundColor Red
        $errors++
    }
} else {
    Write-Host "  [ERROR] vercel.json not found" -ForegroundColor Red
    $errors++
}

# Check frontend/package.json
Write-Host ""
Write-Host "Checking frontend/package.json..." -ForegroundColor Yellow
if (Test-Path "frontend/package.json") {
    Write-Host "  [OK] package.json exists" -ForegroundColor Green
    try {
        $packageJson = Get-Content "frontend/package.json" | ConvertFrom-Json
        if ($packageJson.scripts.build) {
            Write-Host "  [OK] Build script found" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] Build script not found" -ForegroundColor Yellow
            $warnings++
        }
    } catch {
        Write-Host "  [WARN] Could not parse package.json" -ForegroundColor Yellow
        $warnings++
    }
} else {
    Write-Host "  [ERROR] frontend/package.json not found" -ForegroundColor Red
    $errors++
}

# Check frontend/vite.config.ts
Write-Host ""
Write-Host "Checking frontend/vite.config.ts..." -ForegroundColor Yellow
if (Test-Path "frontend/vite.config.ts") {
    Write-Host "  [OK] vite.config.ts exists" -ForegroundColor Green
} else {
    Write-Host "  [WARN] vite.config.ts not found" -ForegroundColor Yellow
    $warnings++
}

# Check frontend/src/main.tsx
Write-Host ""
Write-Host "Checking frontend/src/main.tsx..." -ForegroundColor Yellow
if (Test-Path "frontend/src/main.tsx") {
    Write-Host "  [OK] main.tsx exists" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] frontend/src/main.tsx not found" -ForegroundColor Red
    $errors++
}

# Check for VITE_API_BASE_URL usage
Write-Host ""
Write-Host "Checking for VITE_API_BASE_URL usage..." -ForegroundColor Yellow
$appTsx = Get-Content "frontend/src/App.tsx" -Raw -ErrorAction SilentlyContinue
if ($appTsx -and $appTsx -match "VITE_API_BASE_URL") {
    Write-Host "  [OK] VITE_API_BASE_URL is used in App.tsx" -ForegroundColor Green
} else {
    Write-Host "  [WARN] VITE_API_BASE_URL might not be configured" -ForegroundColor Yellow
    $warnings++
}

# Summary
Write-Host ""
Write-Host "=" * 50
if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "All checks passed! Ready for Vercel deployment." -ForegroundColor Green
} elseif ($errors -eq 0) {
    Write-Host "Configuration looks good with $warnings warning(s)." -ForegroundColor Yellow
} else {
    Write-Host "Found $errors error(s) and $warnings warning(s)." -ForegroundColor Red
    Write-Host "Please fix errors before deploying to Vercel." -ForegroundColor Red
}
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create Vercel account at https://vercel.com" -ForegroundColor Gray
Write-Host "2. Import GitHub repository" -ForegroundColor Gray
Write-Host "3. Set VITE_API_BASE_URL environment variable" -ForegroundColor Gray
Write-Host "4. Follow DEPLOYMENT_STEPS.md for detailed instructions" -ForegroundColor Gray

exit $errors

