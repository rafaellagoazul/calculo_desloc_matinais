# Como subir os arquivos da sua máquina (GitHub)

Este guia é baseado no status que você mostrou no PowerShell: há muitos arquivos válidos, mas também muitos artefatos locais (`__pycache__`, `.bak`, `.fixed`, `.db`, logs e planilhas de teste).

## Execução automatizada (PowerShell)

Se preferir, rode o script pronto:

```powershell
.\scripts\prep_first_push.ps1
```

Com remoto já configurado no mesmo comando:

```powershell
.\scripts\prep_first_push.ps1 -RemoteUrl https://github.com/SEU_USUARIO/calculo_desloc_matinais.git
```

## 1) Limpar o stage atual

Como você já deu `git add` em tudo, primeiro limpe o stage:

```powershell
git reset
```

## 2) Aplicar `.gitignore`

Garanta que existe um `.gitignore` para não versionar lixo local.

> Este repositório já recebeu um `.gitignore` com regras para Python, logs, banco local, backups e planilhas de teste.

## 3) Adicionar só o que deve ir para produção

Adicione somente código e arquivos de configuração necessários:

```powershell
git add main.py pyproject.toml README.md
git add application/ core/ ui/ tools/ scripts/ resources/
```

Se algum diretório tiver artefatos locais, adicione por arquivo em vez de pasta inteira.

## 4) Conferir antes do commit

```powershell
git status
```

Revise especialmente se **NÃO** estão staged:
- `__pycache__/`
- `*.bak`, `*.fixed`
- `*.db`
- `logs/`
- `zz arquivos para testes/`
- `ors_api_key.txt`

## 5) Commitar

```powershell
git commit -m "feat: adiciona estrutura inicial do projeto"
```

## 6) Configurar remoto e enviar

Se ainda não tiver remoto:

```powershell
git remote add origin https://github.com/SEU_USUARIO/calculo_desloc_matinais.git
```

Primeiro push:

```powershell
git branch -M main
git push -u origin main
```

## 7) Se já versionou lixo por engano

Remova do índice sem apagar da máquina:

```powershell
git rm -r --cached __pycache__ logs "zz arquivos para testes"
```

Depois:

```powershell
git add .
git commit -m "chore: remove artefatos locais do versionamento"
git push
```

## 8) Validação no PowerShell (sem `&&` e sem `test -s`)

No Windows PowerShell, use este bloco para validar arquivos e diff check:

```powershell
if ((Test-Path .\scripts\prep_first_push.ps1) -and (Test-Path .\GUIA_SUBIR_ARQUIVOS.md)) {
  Write-Host "ok" -ForegroundColor Green
} else {
  Write-Host "faltam arquivos" -ForegroundColor Red
}

git diff --check
```

> Observação: o operador `&&` só funciona em versões mais novas/shells específicos. Este bloco funciona no PowerShell tradicional.

## Checklist rápido de produção

- [ ] `main.py` e código-fonte versionados
- [ ] `pyproject.toml` versionado
- [ ] sem segredos (`ors_api_key.txt`, `.env`)
- [ ] sem banco local (`*.db`)
- [ ] sem cache/backup (`__pycache__`, `*.bak`, `*.fixed`)
- [ ] sem massa de teste pesada (`zz arquivos para testes/`)
