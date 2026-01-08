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
from cnpj_scraper.scrapers.discovery import CNPJDiscovery, MassDataCollector
from cnpj_scraper.scrapers.receita_data import get_sample_cnpjs_by_category
from cnpj_scraper.scrapers.receita_processor import ReceitaProcessor
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


@app.post("/api/discover/by-category")
async def discover_by_category(
    category: str = Query(..., description="Categoria (tecnologia, varejo, bancos, servicos, industria)"),
    source: str = Query("receitaws", description="Fonte de dados"),
    collect_phones: bool = Query(True, description="Coletar telefones")
):
    """
    Busca empresas por categoria e coleta telefones

    Categorias disponíveis:
    - tecnologia: Empresas de TI e tecnologia
    - varejo: Redes de varejo
    - bancos: Instituições financeiras
    - servicos: Empresas de serviços
    - industria: Indústrias

    Exemplo:
    POST /api/discover/by-category?category=tecnologia&collect_phones=true
    """
    try:
        # Obtém CNPJs de exemplo da categoria
        cnpjs = get_sample_cnpjs_by_category(category)

        if not cnpjs:
            raise HTTPException(
                status_code=404,
                detail=f"Categoria '{category}' não encontrada"
            )

        logger.info(f"Categoria {category}: {len(cnpjs)} empresas")

        # Se não precisa coletar telefones, retorna apenas os CNPJs
        if not collect_phones:
            return {
                "success": True,
                "category": category,
                "total_cnpjs": len(cnpjs),
                "cnpjs": cnpjs
            }

        # Coleta dados completos incluindo telefones
        scraper = get_scraper(source)
        collector = MassDataCollector(scraper, max_workers=3)

        results = []
        for cnpj in cnpjs:
            data = await fetch_company_async(cnpj, source)
            if data:
                results.append({
                    'cnpj': format_cnpj(data.get('cnpj', '')),
                    'razao_social': data.get('razao_social'),
                    'nome_fantasia': data.get('nome_fantasia'),
                    'telefone': data.get('telefone'),
                    'email': data.get('email'),
                    'endereco_completo': f"{data.get('endereco', {}).get('logradouro', '')}, "
                                       f"{data.get('endereco', {}).get('numero', '')} - "
                                       f"{data.get('endereco', {}).get('municipio', '')}/{data.get('endereco', {}).get('uf', '')}",
                    'situacao': data.get('situacao_cadastral')
                })

        # Filtra apenas empresas com telefone
        results_with_phone = [r for r in results if r.get('telefone')]

        return {
            "success": True,
            "category": category,
            "total_found": len(results),
            "with_phone": len(results_with_phone),
            "data": results_with_phone if results_with_phone else results
        }

    except Exception as e:
        logger.error(f"Erro na busca por categoria: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/discover/by-criteria")
async def discover_by_criteria(
    cidade: Optional[str] = Query(None, description="Cidade"),
    estado: Optional[str] = Query(None, description="UF"),
    cnae: Optional[str] = Query(None, description="CNAE"),
    category: Optional[str] = Query(None, description="Categoria pré-definida"),
    limit: int = Query(20, description="Limite de resultados", le=100),
    source: str = Query("receitaws", description="Fonte de dados"),
    collect_phones: bool = Query(True, description="Coletar telefones")
):
    """
    Busca empresas por critérios e coleta telefones

    Opções:
    1. Por categoria pré-definida (tecnologia, varejo, etc.)
    2. Por cidade/estado (NOTA: requer dados da Receita Federal)
    3. Por CNAE (NOTA: requer dados da Receita Federal)

    Exemplo 1 - Por categoria:
    POST /api/discover/by-criteria?category=tecnologia&limit=10

    Exemplo 2 - Por cidade:
    POST /api/discover/by-criteria?cidade=São Paulo&estado=SP&limit=50

    IMPORTANTE: Para busca por cidade/CNAE, você precisa dos dados abertos da Receita Federal.
    Veja: https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/cadastros/consultas/dados-publicos-cnpj
    """
    try:
        cnpjs = []

        # Opção 1: Por categoria pré-definida (mais rápido)
        if category:
            cnpjs = get_sample_cnpjs_by_category(category)
            logger.info(f"Usando categoria {category}: {len(cnpjs)} CNPJs")

        # Opção 2: Por cidade/estado (requer dados da Receita)
        elif cidade and estado:
            logger.warning(
                "Busca por cidade requer dados da Receita Federal. "
                "Usando CNPJs de exemplo para demonstração."
            )
            # Por ora, usa categoria padrão
            cnpjs = get_sample_cnpjs_by_category("servicos")

        # Opção 3: Por CNAE (requer dados da Receita)
        elif cnae:
            logger.warning(
                "Busca por CNAE requer dados da Receita Federal. "
                "Usando CNPJs de exemplo para demonstração."
            )
            cnpjs = get_sample_cnpjs_by_category("tecnologia")

        else:
            raise HTTPException(
                status_code=400,
                detail="Forneça pelo menos um critério: category, cidade+estado, ou cnae"
            )

        # Limita resultados
        cnpjs = cnpjs[:limit]

        if not collect_phones:
            return {
                "success": True,
                "total_cnpjs": len(cnpjs),
                "cnpjs": cnpjs
            }

        # Coleta dados incluindo telefones
        scraper = get_scraper(source)
        results = []

        for cnpj in cnpjs:
            data = await fetch_company_async(cnpj, source)
            if data:
                phone_info = {
                    'cnpj': format_cnpj(data.get('cnpj', '')),
                    'razao_social': data.get('razao_social'),
                    'nome_fantasia': data.get('nome_fantasia'),
                    'telefone': data.get('telefone'),
                    'email': data.get('email'),
                    'cidade': data.get('endereco', {}).get('municipio'),
                    'estado': data.get('endereco', {}).get('uf'),
                    'situacao': data.get('situacao_cadastral'),
                    'cnae_descricao': data.get('cnae_principal', {}).get('descricao', '')
                }
                results.append(phone_info)

        # Filtra por telefone se solicitado
        results_with_phone = [r for r in results if r.get('telefone')]

        return {
            "success": True,
            "criteria": {
                "cidade": cidade,
                "estado": estado,
                "cnae": cnae,
                "category": category
            },
            "total_found": len(results),
            "with_phone": len(results_with_phone),
            "percentage_with_phone": round(len(results_with_phone) / len(results) * 100, 1) if results else 0,
            "data": results_with_phone if results_with_phone else results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na descoberta por critérios: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/categories")
async def list_categories():
    """Lista categorias disponíveis para busca"""
    return {
        "categories": [
            {
                "id": "tecnologia",
                "name": "Tecnologia",
                "description": "Empresas de TI, software, hardware",
                "sample_count": 5
            },
            {
                "id": "varejo",
                "name": "Varejo",
                "description": "Lojas, e-commerce, supermercados",
                "sample_count": 5
            },
            {
                "id": "bancos",
                "name": "Bancos e Financeiras",
                "description": "Instituições financeiras",
                "sample_count": 5
            },
            {
                "id": "servicos",
                "name": "Serviços",
                "description": "Empresas de serviços diversos",
                "sample_count": 5
            },
            {
                "id": "industria",
                "name": "Indústria",
                "description": "Indústrias e manufaturas",
                "sample_count": 5
            }
        ]
    }


@app.post("/api/discover/mei-me-by-region")
async def discover_mei_me_by_region(
    cidade: str = Query(..., description="Nome da cidade"),
    estado: str = Query(..., description="UF (ex: SP, RJ, MG)"),
    limit: int = Query(50, description="Limite de resultados", le=500),
    only_with_phone: bool = Query(True, description="Apenas empresas com telefone")
):
    """
    Busca MEI e ME (Microempresas) em uma região específica

    REQUER: Dados da Receita Federal baixados
    Para baixar: python -m cnpj_scraper.scrapers.receita_downloader

    Exemplo:
    POST /api/discover/mei-me-by-region?cidade=São Paulo&estado=SP&limit=50

    Retorna:
    - CNPJs de MEI e ME da região
    - Razão Social
    - Nome Fantasia
    - Telefone (se disponível)
    - Email
    - Endereço completo
    - Porte (MEI ou ME)
    """
    try:
        processor = ReceitaProcessor()

        # Verifica se dados estão disponíveis
        estabelecimentos_files = processor.find_files('Estabelecimentos')
        if not estabelecimentos_files:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Dados da Receita Federal não disponíveis",
                    "solution": "Execute: python -m cnpj_scraper.scrapers.receita_downloader",
                    "info": "Será necessário baixar ~3GB de dados públicos da Receita Federal",
                    "url": "https://dadosabertos.rfb.gov.br/CNPJ/"
                }
            )

        logger.info(f"Buscando MEI/ME em {cidade}/{estado}")

        # Busca empresas
        results = processor.search_mei_me_by_city(
            cidade=cidade,
            estado=estado,
            limit=limit,
            only_with_phone=only_with_phone
        )

        # Formata resultados
        formatted_results = []
        for empresa in results:
            formatted_results.append({
                'cnpj': format_cnpj(empresa['cnpj']),
                'razao_social': empresa.get('razao_social', ''),
                'nome_fantasia': empresa.get('nome_fantasia', ''),
                'porte': empresa.get('porte', 'Não informado'),
                'telefone': empresa.get('telefone', ''),
                'email': empresa.get('email', ''),
                'endereco_completo': f"{empresa['endereco']['logradouro']}, {empresa['endereco']['numero']} - {empresa['endereco']['bairro']} - {empresa['endereco']['municipio']}/{empresa['endereco']['uf']}",
                'situacao': empresa.get('situacao', ''),
                'cnae': empresa.get('cnae', ''),
                'matriz_filial': empresa.get('matriz_filial', ''),
                'data_abertura': empresa.get('data_abertura', '')
            })

        with_phone = sum(1 for r in formatted_results if r['telefone'])

        return {
            "success": True,
            "source": "Receita Federal (Dados Abertos)",
            "query": {
                "cidade": cidade,
                "estado": estado,
                "limit": limit,
                "only_with_phone": only_with_phone
            },
            "results": {
                "total_found": len(formatted_results),
                "with_phone": with_phone,
                "percentage_with_phone": round(with_phone / len(formatted_results) * 100, 1) if formatted_results else 0
            },
            "data": formatted_results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na busca MEI/ME: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/receita/status")
async def receita_status():
    """
    Verifica status dos dados da Receita Federal

    Retorna informações sobre:
    - Arquivos baixados
    - Tamanho total
    - Cache disponível
    """
    try:
        processor = ReceitaProcessor()

        estabelecimentos = processor.find_files('Estabelecimentos')
        empresas = processor.find_files('Empresas')
        cache_stats = processor.get_cache_stats()

        return {
            "status": "available" if estabelecimentos else "not_available",
            "files": {
                "estabelecimentos": len(estabelecimentos),
                "empresas": len(empresas)
            },
            "cache": cache_stats,
            "download_url": "https://dadosabertos.rfb.gov.br/CNPJ/",
            "download_command": "python -m cnpj_scraper.scrapers.receita_downloader",
            "note": "Dados da Receita Federal são públicos e gratuitos (~3GB essencial, ~30GB completo)"
        }

    except Exception as e:
        logger.error(f"Erro ao verificar status: {e}")
        return {
            "status": "error",
            "error": str(e)
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
