"""
API Web para CNPJ Scraper
FastAPI application para expor funcionalidades do scraper via REST API
"""
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import uvicorn
import os
import json
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from cnpj_scraper.utils import (
    validate_cnpj, clean_cnpj, format_cnpj,
    CacheManager, setup_logger
)
from cnpj_scraper.scrapers import ReceitaWSScraper, BrasilAPIScraper
from cnpj_scraper.exporters import DataExporter
from cnpj_scraper.filters import CompanyFilter


# Configuração
app = FastAPI(
    title="CNPJ Scraper API",
    description="API para coleta ética de dados públicos de empresas brasileiras",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger
logger = setup_logger(verbose=False)

# Cache e executor
cache_manager = CacheManager(cache_dir='cache', duration_hours=24)
executor = ThreadPoolExecutor(max_workers=3)

# Scraper pool
scrapers = {
    'receitaws': None,
    'brasilapi': None
}


# Models
class CNPJRequest(BaseModel):
    cnpj: str = Field(..., description="CNPJ para consulta")
    source: str = Field("receitaws", description="Fonte de dados")

    @validator('cnpj')
    def validate_cnpj_field(cls, v):
        cleaned = clean_cnpj(v)
        if not validate_cnpj(cleaned):
            raise ValueError(f"CNPJ inválido: {v}")
        return cleaned

    @validator('source')
    def validate_source(cls, v):
        if v not in ['receitaws', 'brasilapi']:
            raise ValueError("Fonte deve ser 'receitaws' ou 'brasilapi'")
        return v


class BulkCNPJRequest(BaseModel):
    cnpjs: List[str] = Field(..., description="Lista de CNPJs")
    source: str = Field("receitaws", description="Fonte de dados")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros opcionais")

    @validator('cnpjs')
    def validate_cnpjs(cls, v):
        if len(v) > 100:
            raise ValueError("Máximo de 100 CNPJs por requisição")

        valid_cnpjs = []
        for cnpj in v:
            cleaned = clean_cnpj(cnpj)
            if validate_cnpj(cleaned):
                valid_cnpjs.append(cleaned)

        if not valid_cnpjs:
            raise ValueError("Nenhum CNPJ válido fornecido")

        return valid_cnpjs


class FilterRequest(BaseModel):
    estado: Optional[str] = None
    cidade: Optional[str] = None
    cnae: Optional[str] = None
    situacao: Optional[str] = None
    porte: Optional[str] = None
    apenas_matriz: bool = False


# Funções auxiliares
def get_scraper(source: str):
    """Obtém ou cria scraper"""
    if scrapers[source] is None:
        if source == 'receitaws':
            scrapers[source] = ReceitaWSScraper(
                user_agent="CNPJ Scraper API/1.0",
                delay=2,
                cache_manager=cache_manager
            )
        else:
            scrapers[source] = BrasilAPIScraper(
                user_agent="CNPJ Scraper API/1.0",
                delay=2,
                cache_manager=cache_manager
            )

    return scrapers[source]


async def fetch_company_async(cnpj: str, source: str) -> Optional[Dict[str, Any]]:
    """Busca dados de empresa de forma assíncrona"""
    loop = asyncio.get_event_loop()
    scraper = get_scraper(source)

    try:
        data = await loop.run_in_executor(
            executor,
            scraper.fetch_company_data,
            cnpj
        )
        return data
    except Exception as e:
        logger.error(f"Erro ao buscar CNPJ {cnpj}: {e}")
        return None


# Rotas
@app.get("/")
async def root():
    """Endpoint raiz - redireciona para documentação"""
    return {
        "message": "CNPJ Scraper API",
        "version": "1.0.0",
        "docs": "/docs",
        "frontend": "/web"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_stats": cache_manager.get_stats()
    }


@app.post("/api/cnpj/validate")
async def validate_cnpj_endpoint(cnpj: str = Query(..., description="CNPJ para validar")):
    """
    Valida um CNPJ sem fazer consulta

    Exemplo: /api/cnpj/validate?cnpj=00000000000191
    """
    cleaned = clean_cnpj(cnpj)
    is_valid = validate_cnpj(cleaned)

    return {
        "cnpj": cnpj,
        "cnpj_formatado": format_cnpj(cleaned) if is_valid else None,
        "valido": is_valid,
        "mensagem": "CNPJ válido" if is_valid else "CNPJ inválido"
    }


@app.post("/api/cnpj/search")
async def search_cnpj(request: CNPJRequest):
    """
    Busca dados de uma empresa por CNPJ

    Body:
    {
        "cnpj": "00000000000191",
        "source": "receitaws"
    }
    """
    try:
        data = await fetch_company_async(request.cnpj, request.source)

        if data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Dados não encontrados para CNPJ {format_cnpj(request.cnpj)}"
            )

        return {
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cnpj/bulk")
async def bulk_search(request: BulkCNPJRequest):
    """
    Busca dados de múltiplas empresas

    Body:
    {
        "cnpjs": ["00000000000191", "33000167000101"],
        "source": "receitaws",
        "filters": {
            "estado": "SP",
            "situacao": "ATIVA"
        }
    }
    """
    try:
        # Busca dados de forma assíncrona
        tasks = [
            fetch_company_async(cnpj, request.source)
            for cnpj in request.cnpjs
        ]

        results = await asyncio.gather(*tasks)

        # Filtra resultados nulos
        valid_results = [r for r in results if r is not None]

        # Aplica filtros se fornecidos
        if request.filters:
            valid_results = CompanyFilter.apply_filters(
                valid_results,
                estado=request.filters.get('estado'),
                cidade=request.filters.get('cidade'),
                cnae=request.filters.get('cnae'),
                situacao=request.filters.get('situacao'),
                porte=request.filters.get('porte'),
                apenas_matriz=request.filters.get('apenas_matriz', False)
            )

        return {
            "success": True,
            "total_solicitado": len(request.cnpjs),
            "total_encontrado": len(valid_results),
            "data": valid_results,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Erro na busca em lote: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """
    Retorna estatísticas de uso da API
    """
    stats = {}

    for source, scraper in scrapers.items():
        if scraper is not None:
            stats[source] = scraper.get_stats()

    return {
        "scrapers": stats,
        "cache": cache_manager.get_stats(),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/cache/clear")
async def clear_cache():
    """Limpa o cache"""
    try:
        cleared = cache_manager.clear_all()
        return {
            "success": True,
            "files_removed": cleared,
            "message": f"Cache limpo: {cleared} arquivos removidos"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cache/stats")
async def cache_stats():
    """Retorna estatísticas do cache"""
    return cache_manager.get_stats()


@app.get("/api/sources")
async def list_sources():
    """Lista fontes de dados disponíveis"""
    return {
        "sources": [
            {
                "id": "receitaws",
                "name": "ReceitaWS",
                "url": "https://www.receitaws.com.br",
                "rate_limit": "3 req/min",
                "status": "active"
            },
            {
                "id": "brasilapi",
                "name": "BrasilAPI",
                "url": "https://brasilapi.com.br",
                "rate_limit": "2 req/sec",
                "status": "active"
            }
        ]
    }


# Serve arquivos estáticos (frontend)
if os.path.exists("static"):
    app.mount("/web", StaticFiles(directory="static", html=True), name="static")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Inicialização da aplicação"""
    logger.info("CNPJ Scraper API iniciada")
    logger.info("Documentação disponível em: /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Finalização da aplicação"""
    logger.info("CNPJ Scraper API finalizada")
    executor.shutdown(wait=True)


# Executar aplicação
if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
