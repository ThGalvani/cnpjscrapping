@echo off
echo ============================================
echo   CNPJ Scraper - Instalacao Windows
echo ============================================
echo.

echo [1/5] Verificando Python...
py --version
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo.
    echo Por favor, instale Python de: https://www.python.org/downloads/
    echo IMPORTANTE: Marque a opcao "Add Python to PATH"
    pause
    exit /b 1
)
echo OK!
echo.

echo [2/5] Criando ambiente virtual...
py -m venv venv
if %errorlevel% neq 0 (
    echo ERRO ao criar ambiente virtual!
    pause
    exit /b 1
)
echo OK!
echo.

echo [3/5] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERRO ao ativar ambiente virtual!
    pause
    exit /b 1
)
echo OK!
echo.

echo [4/5] Atualizando pip...
python -m pip install --upgrade pip
echo OK!
echo.

echo [5/5] Instalando dependencias...
echo (Isso pode demorar alguns minutos...)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO ao instalar dependencias!
    pause
    exit /b 1
)
echo OK!
echo.

echo ============================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo ============================================
echo.
echo Para iniciar a aplicacao, execute:
echo   iniciar.bat
echo.
echo Ou manualmente:
echo   venv\Scripts\activate.bat
echo   uvicorn api:app --reload --port 8000
echo.
echo Depois acesse: http://localhost:8000/web
echo.
pause
