param(
    [Parameter(Mandatory=$true)]
    [string]$RemoteUrl,
    [string]$Branch = "main",
    [string]$CommitMessage = "feat: primeiro envio do projeto"
)

$ErrorActionPreference = "Stop"

function Assert-LastCommand {
    param([string]$Step)
    if ($LASTEXITCODE -ne 0) {
        throw "Falha em: $Step (exit code $LASTEXITCODE)."
    }
}

if ($RemoteUrl -match "SEU_USUARIO|SEU_REPO") {
    throw "RemoteUrl ainda esta com placeholder. Troque para a URL real do seu repositorio."
}

Write-Host "==> Validando estrutura" -ForegroundColor Cyan
& "$PSScriptRoot\check_repo.ps1"
Assert-LastCommand "validacao da estrutura"

Write-Host "==> Preparando stage seguro" -ForegroundColor Cyan
& "$PSScriptRoot\prep_first_push.ps1" -RemoteUrl $RemoteUrl -Branch $Branch
Assert-LastCommand "preparacao do stage"

Write-Host "==> Commit" -ForegroundColor Cyan
$hasChanges = (git diff --cached --name-only)
Assert-LastCommand "leitura de staged files"
if (-not $hasChanges) {
    Write-Host "Nada no stage para commit." -ForegroundColor Yellow
    exit 1
}

git commit -m $CommitMessage
Assert-LastCommand "git commit"

Write-Host "==> Push" -ForegroundColor Cyan
git push -u origin $Branch
Assert-LastCommand "git push"

Write-Host "Concluido com sucesso." -ForegroundColor Green
