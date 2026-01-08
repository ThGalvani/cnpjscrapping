@echo off
echo ============================================
echo   CNPJ Scraper - Iniciando Aplicacao
echo ============================================
echo.

if not exist venv (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Execute primeiro: instalar.bat
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo Iniciando API...
echo.
echo A aplicacao estara disponivel em:
echo   http://localhost:8000/web
echo.
echo Pressione CTRL+C para parar
echo.

uvicorn api:app --reload --port 8000
