# Environment Setup Script (PowerShell)
# Helps set up environment-specific configuration files

param(
    [Parameter(Position=0)]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment = "development"
)

Write-Host "Setting up $Environment environment..." -ForegroundColor Cyan

# Backend setup
if (Test-Path "backend") {
    Write-Host "Setting up backend environment..." -ForegroundColor Yellow
    
    $backendEnvFile = switch ($Environment) {
        "development" { "backend\.env.development" }
        "staging" { "backend\.env.staging" }
        "production" { "backend\.env.production" }
    }
    
    $backendExampleFile = switch ($Environment) {
        "development" { "backend\.env.development.example" }
        "staging" { "backend\.env.staging.example" }
        "production" { "backend\.env.production.example" }
    }
    
    if (-not (Test-Path $backendEnvFile)) {
        if (Test-Path $backendExampleFile) {
            Copy-Item $backendExampleFile $backendEnvFile
            Write-Host "✅ Created $backendEnvFile" -ForegroundColor Green
            Write-Host "⚠️  Please edit $backendEnvFile and add your API keys" -ForegroundColor Yellow
        } else {
            Write-Host "❌ Example file not found: $backendExampleFile" -ForegroundColor Red
        }
    } else {
        Write-Host "ℹ️  $backendEnvFile already exists" -ForegroundColor Blue
    }
}

# Frontend setup
if (Test-Path "frontend") {
    Write-Host "Setting up frontend environment..." -ForegroundColor Yellow
    
    $frontendEnvFile = switch ($Environment) {
        "development" { "frontend\.env.development" }
        "staging" { "frontend\.env.staging" }
        "production" { "frontend\.env.production" }
    }
    
    $frontendExampleFile = switch ($Environment) {
        "development" { "frontend\.env.development.example" }
        "staging" { "frontend\.env.staging.example" }
        "production" { "frontend\.env.production.example" }
    }
    
    if (-not (Test-Path $frontendEnvFile)) {
        if (Test-Path $frontendExampleFile) {
            Copy-Item $frontendExampleFile $frontendEnvFile
            Write-Host "✅ Created $frontendEnvFile" -ForegroundColor Green
        } else {
            Write-Host "❌ Example file not found: $frontendExampleFile" -ForegroundColor Red
        }
    } else {
        Write-Host "ℹ️  $frontendEnvFile already exists" -ForegroundColor Blue
    }
}

Write-Host ""
Write-Host "✅ Environment setup complete for $Environment" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit the .env files and add your API keys"
Write-Host "2. Verify configuration matches your environment"
Write-Host "3. Test locally before deploying"

