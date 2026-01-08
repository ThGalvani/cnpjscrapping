# CNPJ Scraper - Script de Instalação para Windows
# Execute: .\instalar.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  CNPJ Scraper - Instalacao Windows" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Passo 1: Verificar Python
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = py --version 2>&1
    Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Python nao encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, instale Python de: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "IMPORTANTE: Marque a opcao 'Add Python to PATH'" -ForegroundColor Yellow
    Read-Host "Pressione ENTER para sair"
    exit 1
}
Write-Host ""

# Passo 2: Criar ambiente virtual
Write-Host "[2/5] Criando ambiente virtual..." -ForegroundColor Yellow
try {
    py -m venv venv
    Write-Host "Ambiente virtual criado!" -ForegroundColor Green
} catch {
    Write-Host "ERRO ao criar ambiente virtual!" -ForegroundColor Red
    Read-Host "Pressione ENTER para sair"
    exit 1
}
Write-Host ""

# Passo 3: Ativar ambiente virtual
Write-Host "[3/5] Ativando ambiente virtual..." -ForegroundColor Yellow
try {
    & .\venv\Scripts\Activate.ps1
    Write-Host "Ambiente virtual ativado!" -ForegroundColor Green
} catch {
    Write-Host "AVISO: Nao foi possivel ativar automaticamente." -ForegroundColor Yellow
    Write-Host "Execute manualmente: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Se der erro, execute como Administrador:" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
}
Write-Host ""

# Passo 4: Atualizar pip
Write-Host "[4/5] Atualizando pip..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip --quiet
    Write-Host "pip atualizado!" -ForegroundColor Green
} catch {
    Write-Host "AVISO: Erro ao atualizar pip (continuando...)" -ForegroundColor Yellow
}
Write-Host ""

# Passo 5: Instalar dependências
Write-Host "[5/5] Instalando dependencias..." -ForegroundColor Yellow
Write-Host "(Isso pode demorar alguns minutos...)" -ForegroundColor Gray
try {
    pip install -r requirements.txt
    Write-Host "Dependencias instaladas!" -ForegroundColor Green
} catch {
    Write-Host "ERRO ao instalar dependencias!" -ForegroundColor Red
    Write-Host "Tente manualmente: pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Pressione ENTER para sair"
    exit 1
}
Write-Host ""

# Sucesso
Write-Host "============================================" -ForegroundColor Green
Write-Host "  INSTALACAO CONCLUIDA COM SUCESSO!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar a aplicacao:" -ForegroundColor Cyan
Write-Host "  .\iniciar.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Ou manualmente:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  uvicorn api:app --reload --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "Depois acesse: http://localhost:8000/web" -ForegroundColor Yellow
Write-Host ""

Read-Host "Pressione ENTER para sair"
