@echo off
cd /d "%~dp0"

echo.
echo ==== Atualizando repositório com pull --rebase ====
git pull origin main --rebase

echo.
echo ==== Adicionando todas as mudanças ====
git add .

echo.
set /p msg="Digite a mensagem do commit: "
git commit -m "%msg%"

echo.
echo ==== Enviando para o GitHub ====
git push origin main

echo.
echo ==== Publicando na Vercel ====
vercel --prod

pause
