param (
    [string]$Root = ".",
    [string]$OutFile = "analise_final_projeto.csv"
)

Write-Host "🔍 Analisando projeto Python..." -ForegroundColor Cyan

$files = Get-ChildItem $Root -Recurse -Filter *.py |
    Where-Object {
        $_.FullName -notmatch "\\venv\\" -and
        $_.FullName -notmatch "__pycache__" -and
        $_.FullName -notmatch "\\.git\\"
    }

$importsMap = @{}
$importedBy = @{}
$results = @()

# ───────── COLETA DE IMPORTS ─────────
foreach ($file in $files) {
    $rel = $file.FullName.Replace((Resolve-Path $Root), "").TrimStart("\")
    $importsMap[$rel] = @()

    foreach ($line in Get-Content $file.FullName -ErrorAction SilentlyContinue) {
        if ($line -match '^\s*(import|from)\s+([a-zA-Z0-9_\.]+)') {
            $importsMap[$rel] += $Matches[2]
        }
    }
}

# ───────── MAPA INVERSO ─────────
foreach ($file in $importsMap.Keys) {
    foreach ($imp in $importsMap[$file]) {
        foreach ($target in $importsMap.Keys) {
            if ($target -like "*$($imp -replace '\.', '\')*.py") {
                if (-not $importedBy.ContainsKey($target)) {
                    $importedBy[$target] = @()
                }
                $importedBy[$target] += $file
            }
        }
    }
}

# ───────── ANÁLISE ─────────
foreach ($file in $files) {
    $rel = $file.FullName.Replace((Resolve-Path $Root), "").TrimStart("\")
    $content = Get-Content $file.FullName -ErrorAction SilentlyContinue

    $hasMain = $false
    $sideEffects = $false

    foreach ($line in $content) {
        if ($line -match "__name__\s*==\s*['""]__main__['""]") {
            $hasMain = $true
        }

        if (
            $line -match '^\s*(print|open|sys\.exit|threading\.Thread|requests\.|tkinter|customtkinter)' -and
            $line -notmatch '^\s*(def|class)\s+'
        ) {
            $sideEffects = $true
        }
    }

    $imports = $importsMap[$rel].Count
    $usedBy = if ($importedBy.ContainsKey($rel)) { $importedBy[$rel].Count } else { 0 }

    $area =
        if ($rel -like "ui\*") { "UI" }
        elseif ($rel -like "core\*") { "CORE" }
        elseif ($rel -like "admin\*") { "ADMIN" }
        elseif ($rel -like "scripts\*") { "SCRIPT" }
        else { "OUTRO" }

    $risk = 0
    if ($usedBy -eq 0) { $risk += 3 }
    if ($sideEffects) { $risk += 2 }
    if ($imports -eq 0 -and -not $hasMain) { $risk += 1 }

    $suggest =
        if ($risk -ge 5) { "ORFAO / CANDIDATO A EXCLUSAO" }
        elseif ($risk -ge 3) { "SUSPEITO" }
        else { "ATIVO" }

    $results += [PSCustomObject]@{
        Arquivo      = $rel
        Area         = $area
        Imports      = $imports
        ImportadoPor = $usedBy
        TemMain      = $hasMain
        SideEffects  = $sideEffects
        Risco        = $risk
        Sugestao     = $suggest
    }
}

# ───────── SAÍDA ─────────
$results |
    Sort-Object Risco -Descending |
    Export-Csv $OutFile -NoTypeInformation -Encoding UTF8

Write-Host "✔ Análise concluída. Arquivo gerado: $OutFile" -ForegroundColor Green
