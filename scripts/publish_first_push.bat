@echo off
if "%~1"=="" (
  echo Uso: scripts\publish_first_push.bat https://github.com/rafaellagoazul/calculo_desloc_matinais.git [branch]
  exit /b 1
)
set REMOTE=%~1
set BRANCH=%~2
if "%BRANCH%"=="" set BRANCH=main
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0publish_first_push.ps1" -RemoteUrl "%REMOTE%" -Branch "%BRANCH%"
