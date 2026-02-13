$ErrorActionPreference = "Stop"

$requiredFiles = @(
    ".gitattributes",
    "GUIA_SUBIR_ARQUIVOS.md"
)

$missing = @()
foreach ($f in $requiredFiles) {
    if (-not (Test-Path $f)) { $missing += $f }
}

if ($missing.Count -gt 0) {
    Write-Host "ERRO: arquivos ausentes:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
    exit 1
}

Write-Host "ok" -ForegroundColor Green
git diff --check
