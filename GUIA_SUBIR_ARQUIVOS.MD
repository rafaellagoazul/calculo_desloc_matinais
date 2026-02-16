# Como subir os arquivos da sua máquina (GitHub)

Este guia é baseado no status que você mostrou no PowerShell: há muitos arquivos válidos, mas também muitos artefatos locais (`__pycache__`, `.bak`, `.fixed`, `.db`, logs e planilhas de teste).

## Execução automatizada (PowerShell)

Se preferir, rode o script pronto:

```powershell
.\scripts\prep_first_push.ps1
```

Com remoto já configurado no mesmo comando:

```powershell
.\scripts\prep_first_push.ps1 -RemoteUrl https://github.com/rafaellagoazul/calculo_desloc_matinais.git
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
git remote add origin https://github.com/rafaellagoazul/calculo_desloc_matinais.git
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

Execute o script de validação:

```powershell
.\scripts\validate_docs.ps1
```

Ou, se preferir sem script, use este bloco:

```powershell
if ((Test-Path .\scripts\prep_first_push.ps1) -and (Test-Path .\GUIA_SUBIR_ARQUIVOS.md)) {
  Write-Host "ok" -ForegroundColor Green
} else {
  Write-Host "faltam arquivos" -ForegroundColor Red
}

git diff --check
```

> Observação: o operador `&&` só funciona em versões mais novas/shells específicos. Este bloco funciona no PowerShell tradicional.


## 9) Erro: `script não é reconhecido` no PowerShell

Se aparecer algo como:

```text
.\scripts\validate_docs.ps1 : ... não é reconhecido ...
```

faça esta sequência no **PowerShell dentro da pasta do projeto**:

```powershell
pwd
git status
git pull
Get-ChildItem .\scripts
```

Depois execute de novo:

```powershell
.\scripts\validate_docs.ps1
```

Se ainda falhar, rode sem depender de arquivo de script:

```powershell
if ((Test-Path .\scripts\prep_first_push.ps1) -and (Test-Path .\GUIA_SUBIR_ARQUIVOS.md)) {
  Write-Host "ok" -ForegroundColor Green
} else {
  Write-Host "faltam arquivos no clone local" -ForegroundColor Red
}

git diff --check
```

## Checklist rápido de produção

- [ ] `main.py` e código-fonte versionados
- [ ] `pyproject.toml` versionado
- [ ] sem segredos (`ors_api_key.txt`, `.env`)
- [ ] sem banco local (`*.db`)
- [ ] sem cache/backup (`__pycache__`, `*.bak`, `*.fixed`)
- [ ] sem massa de teste pesada (`zz arquivos para testes/`)


## 10) VSCode sobe automaticamente no commit?

**Não automaticamente.** O `git commit` só envia o que está em *staging* (`git add`).

- Se `.vscode/` está no `.gitignore`, ele **não entra** por padrão.
- Só sobe se você forçar (`git add -f .vscode/...`) ou remover a regra do `.gitignore`.

Para conferir o que vai subir:

```powershell
git status
```

Se quiser versionar apenas alguns arquivos do VSCode (ex.: recomendações), faça assim:

```powershell
# manter ignorado por padrão
# e versionar só arquivos específicos
git add -f .vscode/extensions.json
```

## 11) Aviso LF/CRLF no `git diff --check`

Esse aviso:

```text
warning: in the working copy of 'README.md', LF will be replaced by CRLF ...
```

não é erro de commit. É apenas conversão de fim de linha no Windows.

Este repositório agora tem `.gitattributes` para normalizar final de linha.

Se quiser reduzir esses avisos no seu clone, rode:

```powershell
git config core.autocrlf true
git add --renormalize .
git status
```

Depois commit e push normalmente.



## 12) Comandos de validação para PowerShell (copiar e colar)


> ⚠️ **PowerShell tradicional**: não use `test -s` nem `&&` (sintaxe de bash).  
> Use somente os comandos desta seção.

Use **este comando** no lugar de `test -s ... && ...`:

```powershell
.\scripts\check_repo.ps1
```

Se houver bloqueio de política de execução, rode:

```powershell
.\scripts\check_repo.bat
```

Se quiser validar manualmente sem script:

```powershell
if ((Test-Path .gitattributes) -and (Test-Path .\GUIA_SUBIR_ARQUIVOS.md)) {
  Write-Host "ok" -ForegroundColor Green
} else {
  Write-Host "faltam arquivos" -ForegroundColor Red
}

git diff --check
```


## 13) Publicação em um comando (PowerShell)

Para fazer validação + preparação + commit + push de uma vez:

```powershell
.\scripts\publish_first_push.ps1 -RemoteUrl https://github.com/rafaellagoazul/calculo_desloc_matinais.git
```


> ✅ URL do seu repositório configurada nos exemplos abaixo (`rafaellagoazul/calculo_desloc_matinais`).

Opcionalmente, defina branch e mensagem:

```powershell
.\scripts\publish_first_push.ps1 -RemoteUrl https://github.com/rafaellagoazul/calculo_desloc_matinais.git -Branch main -CommitMessage "feat: primeiro envio do projeto"
```

Fallback `.bat` (quando política de execução bloquear `.ps1`):

```powershell
.\scripts\publish_first_push.bat https://github.com/rafaellagoazul/calculo_desloc_matinais.git main
```
