# Script to publish PyMLS to production PyPI using uv
# 
# Prerequisites:
# 1. Create an account at https://pypi.org/account/register/
# 2. Generate an API token at https://pypi.org/manage/account/token/
# 3. Set the token as an environment variable or pass it via --token
#
# Usage:
#   .\publish_pypi.ps1
#   .\publish_pypi.ps1 -Token "your-token-here"

param(
    [string]$Token = $env:PYPI_TOKEN
)

if (-not $Token) {
    Write-Host "Error: PyPI token not provided." -ForegroundColor Red
    Write-Host "Either set PYPI_TOKEN environment variable or pass -Token parameter" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To get a token:" -ForegroundColor Yellow
    Write-Host "1. Create account at https://pypi.org/account/register/" -ForegroundColor Cyan
    Write-Host "2. Generate token at https://pypi.org/manage/account/token/" -ForegroundColor Cyan
    exit 1
}

Write-Host "Building package..." -ForegroundColor Green
uv build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Publishing to PyPI..." -ForegroundColor Green
# For production PyPI, you can either:
# 1. Omit --publish-url (defaults to production)
# 2. Explicitly use: --publish-url https://upload.pypi.org/legacy/
uv publish --token $Token

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Successfully published to PyPI!" -ForegroundColor Green
    Write-Host "Install with: pip install PyMls" -ForegroundColor Cyan
    Write-Host "View at: https://pypi.org/project/PyMls/" -ForegroundColor Cyan
} else {
    Write-Host "Publishing failed!" -ForegroundColor Red
    exit 1
}

