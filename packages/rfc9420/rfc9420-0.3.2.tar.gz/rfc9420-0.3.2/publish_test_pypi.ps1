# Script to publish RFC9420 to test PyPI using uv
# 
# Prerequisites:
# 1. Create an account at https://test.pypi.org/account/register/
# 2. Generate an API token at https://test.pypi.org/manage/account/token/
# 3. Set the token as an environment variable or pass it via --token
#
# Usage:
#   .\publish_test_pypi.ps1
#   .\publish_test_pypi.ps1 -Token "your-token-here"

param(
    [string]$Token = $env:TEST_PYPI_TOKEN
)

if (-not $Token) {
    Write-Host "Error: Test PyPI token not provided." -ForegroundColor Red
    Write-Host "Either set TEST_PYPI_TOKEN environment variable or pass -Token parameter" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To get a token:" -ForegroundColor Yellow
    Write-Host "1. Create account at https://test.pypi.org/account/register/" -ForegroundColor Cyan
    Write-Host "2. Generate token at https://test.pypi.org/manage/account/token/" -ForegroundColor Cyan
    exit 1
}

Write-Host "Building package..." -ForegroundColor Green
uv build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Publishing to test PyPI..." -ForegroundColor Green
uv publish --publish-url https://test.pypi.org/legacy/ --token $Token

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Successfully published to test PyPI!" -ForegroundColor Green
    Write-Host "Install with: pip install -i https://test.pypi.org/simple/ rfc9420" -ForegroundColor Cyan
} else {
    Write-Host "Publishing failed!" -ForegroundColor Red
    exit 1
}

