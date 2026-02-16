$ErrorActionPreference = "Stop"

Write-Host "[1/3] Procurando placeholders (SEU_USUARIO/SEU_REPO)" -ForegroundColor Cyan
$targets = @(
    "GUIA_SUBIR_ARQUIVOS.md",
    "scripts"
)

$placeholderMatches = Get-ChildItem $targets -Recurse -File |
    Where-Object { $_.Extension -in @('.md', '.ps1', '.bat') } |
    Select-String -Pattern 'SEU_USUARIO|SEU_REPO'

if ($placeholderMatches) {
    Write-Host "Encontrados placeholders:" -ForegroundColor Yellow
    $placeholderMatches | ForEach-Object { Write-Host " - $($_.Path):$($_.LineNumber)" -ForegroundColor Yellow }
} else {
    Write-Host "Nenhum placeholder encontrado." -ForegroundColor Green
}

Write-Host "[2/3] Verificando arquivos esperados" -ForegroundColor Cyan
if ((Test-Path .\GUIA_SUBIR_ARQUIVOS.md) -and (Test-Path .\scripts\prep_first_push.ps1) -and (Test-Path .\scripts\publish_first_push.bat)) {
    Write-Host "ok" -ForegroundColor Green
} else {
    Write-Host "faltam arquivos obrigatorios" -ForegroundColor Red
    exit 1
}

Write-Host "[3/3] git diff --check" -ForegroundColor Cyan
git diff --check
if ($LASTEXITCODE -ne 0) {
    throw "git diff --check reportou problemas"
}
