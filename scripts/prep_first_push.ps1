param(
    [string]$RemoteUrl = "",
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

Write-Host "==> [1/6] Limpando stage atual" -ForegroundColor Cyan
git reset | Out-Null

Write-Host "==> [2/6] Re-adicionando .gitignore" -ForegroundColor Cyan
git add .gitignore

Write-Host "==> [3/6] Adicionando código e configuração principais" -ForegroundColor Cyan
$paths = @(
    "main.py",
    "pyproject.toml",
    "README.md",
    "application",
    "core",
    "ui",
    "tools",
    "scripts",
    "resources"
)

foreach ($p in $paths) {
    if (Test-Path $p) {
        git add -- $p
    }
}

Write-Host "==> [4/6] Mostrando status para revisão" -ForegroundColor Cyan
git status

Write-Host "==> [5/6] Verificando possíveis artefatos indevidos no stage" -ForegroundColor Cyan
$staged = git diff --cached --name-only
$patterns = @(
    "__pycache__/",
    ".bak",
    ".fixed",
    ".db",
    "logs/",
    "zz arquivos para testes/",
    "ors_api_key.txt"
)

$found = @()
foreach ($f in $staged) {
    foreach ($pat in $patterns) {
        if ($f -like "*$pat*") {
            $found += $f
            break
        }
    }
}

if ($found.Count -gt 0) {
    Write-Host "ATENÇÃO: arquivos potencialmente indevidos no stage:" -ForegroundColor Yellow
    $found | Sort-Object -Unique | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
    Write-Host "Remova com: git restore --staged <arquivo>" -ForegroundColor Yellow
} else {
    Write-Host "Nenhum artefato crítico detectado no stage." -ForegroundColor Green
}

Write-Host "==> [6/6] Configuração opcional de remoto" -ForegroundColor Cyan
if ($RemoteUrl -ne "") {
    $hasOrigin = git remote | Select-String -SimpleMatch "origin"
    if ($hasOrigin) {
        git remote set-url origin $RemoteUrl
    } else {
        git remote add origin $RemoteUrl
    }
    git branch -M $Branch
    Write-Host "Remote configurado. Para enviar: git push -u origin $Branch" -ForegroundColor Green
} else {
    Write-Host "Remote não informado. Exemplo de uso:" -ForegroundColor DarkGray
    Write-Host ".\\scripts\\prep_first_push.ps1 -RemoteUrl https://github.com/SEU_USUARIO/calculo_desloc_matinais.git" -ForegroundColor DarkGray
}
