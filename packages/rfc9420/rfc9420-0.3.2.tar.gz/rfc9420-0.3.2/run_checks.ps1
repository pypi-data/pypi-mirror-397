# Script to run mypy, ruff, and pytest checks
# Outputs results to mypy_output.txt, ruff_output.txt, and test_output.txt

Write-Host "Running type checks with mypy..." -ForegroundColor Cyan
uv run mypy src > mypy_output.txt 2>&1
$mypyExitCode = $LASTEXITCODE

Write-Host "Running linting with ruff..." -ForegroundColor Cyan
uv run ruff check . > ruff_output.txt 2>&1
$ruffExitCode = $LASTEXITCODE

Write-Host "Running tests with pytest..." -ForegroundColor Cyan
uv run pytest -v > test_output.txt 2>&1
$pytestExitCode = $LASTEXITCODE

Write-Host ""
Write-Host "Results:" -ForegroundColor Yellow
Write-Host "  mypy:   $mypy_output.txt (exit code: $mypyExitCode)" -ForegroundColor $(if ($mypyExitCode -eq 0) { "Green" } else { "Red" })
Write-Host "  ruff:   $ruff_output.txt (exit code: $ruffExitCode)" -ForegroundColor $(if ($ruffExitCode -eq 0) { "Green" } else { "Red" })
Write-Host "  pytest: $test_output.txt (exit code: $pytestExitCode)" -ForegroundColor $(if ($pytestExitCode -eq 0) { "Green" } else { "Red" })

$totalExitCode = $mypyExitCode + $ruffExitCode + $pytestExitCode
if ($totalExitCode -eq 0) {
    Write-Host ""
    Write-Host "All checks passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host ""
    Write-Host "Some checks failed. Check the output files for details." -ForegroundColor Red
    exit 1
}

