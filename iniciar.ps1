# CNPJ Scraper - Script de Inicialização
# Execute: .\iniciar.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  CNPJ Scraper - Iniciando Aplicacao" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se ambiente virtual existe
if (-not (Test-Path "venv")) {
    Write-Host "ERRO: Ambiente virtual nao encontrado!" -ForegroundColor Red
    Write-Host "Execute primeiro: .\instalar.ps1" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Pressione ENTER para sair"
    exit 1
}

# Ativar ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
try {
    & .\venv\Scripts\Activate.ps1
    Write-Host "Ambiente virtual ativado!" -ForegroundColor Green
} catch {
    Write-Host "AVISO: Erro ao ativar ambiente virtual" -ForegroundColor Yellow
    Write-Host "Continuando mesmo assim..." -ForegroundColor Gray
}
Write-Host ""

# Mostrar informações
Write-Host "Iniciando API..." -ForegroundColor Yellow
Write-Host ""
Write-Host "A aplicacao estara disponivel em:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000/web" -ForegroundColor White
Write-Host ""
Write-Host "Documentacao da API:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Pressione CTRL+C para parar" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Iniciar aplicação
try {
    uvicorn api:app --reload --port 8000
} catch {
    Write-Host ""
    Write-Host "ERRO ao iniciar aplicacao!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Tente manualmente:" -ForegroundColor Yellow
    Write-Host "  py -m uvicorn api:app --reload --port 8000" -ForegroundColor White
    Write-Host "ou" -ForegroundColor Gray
    Write-Host "  python api.py" -ForegroundColor White
    Write-Host ""
    Read-Host "Pressione ENTER para sair"
    exit 1
}
