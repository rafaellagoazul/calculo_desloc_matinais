param(
    [Parameter(Mandatory=$true)]
    [string]$RemoteUrl,
    [string]$Branch = "main",
    [string]$CommitMessage = "feat: primeiro envio do projeto"
)

$ErrorActionPreference = "Stop"

Write-Host "==> Validando estrutura" -ForegroundColor Cyan
& "$PSScriptRoot\check_repo.ps1"

Write-Host "==> Preparando stage seguro" -ForegroundColor Cyan
& "$PSScriptRoot\prep_first_push.ps1" -RemoteUrl $RemoteUrl -Branch $Branch

Write-Host "==> Commit" -ForegroundColor Cyan
$hasChanges = (git diff --cached --name-only)
if (-not $hasChanges) {
    Write-Host "Nada no stage para commit." -ForegroundColor Yellow
    exit 1
}

git commit -m $CommitMessage

Write-Host "==> Push" -ForegroundColor Cyan
git push -u origin $Branch

Write-Host "Concluído com sucesso." -ForegroundColor Green
