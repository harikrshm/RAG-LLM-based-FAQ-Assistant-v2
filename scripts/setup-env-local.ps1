# PowerShell script to set up local .env file for backend
# Run this script from the project root directory

Write-Host "Setting up local .env file for backend..." -ForegroundColor Cyan

$backendEnvPath = "backend\.env"

# Check if .env file already exists
if (Test-Path $backendEnvPath) {
    Write-Host "Warning: backend\.env already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "Skipping .env file creation." -ForegroundColor Yellow
        exit 0
    }
}

# Prompt for Gemini API key
Write-Host ""
Write-Host "Please enter your Google Gemini API key." -ForegroundColor Cyan
Write-Host "Get your API key from: https://makersuite.google.com/app/apikey" -ForegroundColor Gray
Write-Host ""

$apiKey = Read-Host "Enter your GEMINI_API_KEY"

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host "Error: API key cannot be empty!" -ForegroundColor Red
    exit 1
}

# Create .env file content
$envContent = @"
# Google Gemini API Key
GEMINI_API_KEY=$apiKey

# Environment Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# CORS Configuration (for local development)
# CORS_ORIGINS_ENV=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173

# Vector Database Paths
VECTORDB_PATH=data/vectordb
METADATA_PATH=data/metadata_index.json
SOURCE_URLS_PATH=data/source_urls.json
"@

# Write to file
try {
    $envContent | Out-File -FilePath $backendEnvPath -Encoding utf8 -NoNewline
    Write-Host ""
    Write-Host "Successfully created backend\.env file!" -ForegroundColor Green
    Write-Host "Location: $backendEnvPath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Verify the .env file contains your API key" -ForegroundColor Gray
    Write-Host "2. Test locally: cd backend && uvicorn main:app --reload" -ForegroundColor Gray
    Write-Host "3. Follow DEPLOYMENT_STEPS.md for Railway and Vercel deployment" -ForegroundColor Gray
} catch {
    Write-Host "Error creating .env file: $_" -ForegroundColor Red
    exit 1
}

