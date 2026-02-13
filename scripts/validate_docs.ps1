$ErrorActionPreference = "Stop"

$ok = $true

if (-not (Test-Path .\GUIA_SUBIR_ARQUIVOS.md)) {
    Write-Host "ERRO: GUIA_SUBIR_ARQUIVOS.md não encontrado." -ForegroundColor Red
    $ok = $false
}

if (-not (Test-Path .\scripts\prep_first_push.ps1)) {
    Write-Host "ERRO: scripts\prep_first_push.ps1 não encontrado." -ForegroundColor Red
    $ok = $false
}

if ($ok) {
    Write-Host "ok" -ForegroundColor Green
} else {
    exit 1
}

# Verifica inconsistências de whitespace no diff
git diff --check
