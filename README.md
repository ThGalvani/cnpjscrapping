# 🏢 CNPJ Scraper

Ferramenta ética de web scraping para coleta de dados públicos de empresas brasileiras.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

## 📋 Índice

- [Sobre](#sobre)
- [Aviso Legal](#aviso-legal)
- [Características](#características)
- [Instalação](#instalação)
- [Uso](#uso)
- [Exemplos](#exemplos)
- [Configuração](#configuração)
- [Fontes de Dados](#fontes-de-dados)
- [Boas Práticas](#boas-práticas)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Desenvolvimento](#desenvolvimento)
- [FAQ](#faq)
- [Licença](#licença)

## 🎯 Sobre

O **CNPJ Scraper** é uma ferramenta Python desenvolvida para coletar dados públicos de empresas brasileiras de forma ética e responsável. A ferramenta implementa todas as boas práticas de web scraping, incluindo:

- ✅ Verificação automática de `robots.txt`
- ✅ Rate limiting configurável
- ✅ Retry logic com backoff exponencial
- ✅ Cache inteligente para evitar requisições duplicadas
- ✅ User-Agent identificável e honesto
- ✅ Logging completo de atividades
- ✅ Múltiplos formatos de exportação

## ⚖️ Aviso Legal

**IMPORTANTE:** Esta ferramenta deve ser usada APENAS para fins legais e éticos.

### Uso Permitido

- ✅ Pesquisa acadêmica
- ✅ Análise de mercado
- ✅ Verificação de dados públicos
- ✅ Estudos estatísticos
- ✅ Conformidade regulatória

### Responsabilidades do Usuário

Ao usar esta ferramenta, você se compromete a:

1. **Respeitar** os termos de uso dos sites consultados
2. **Não sobrecarregar** os servidores com requisições excessivas
3. **Conformidade** com a LGPD (Lei Geral de Proteção de Dados)
4. **Uso ético** dos dados coletados
5. **Não coletar** dados sensíveis ou protegidos

### Limitações

- ❌ Não use para SPAM ou marketing não solicitado
- ❌ Não use para fins fraudulentos
- ❌ Não ignore as configurações de rate limiting
- ❌ Não desabilite a verificação de robots.txt sem motivo válido

**O desenvolvedor não se responsabiliza pelo uso indevido desta ferramenta.**

## ✨ Características

### Funcionalidades Principais

- 🔍 **Busca por CNPJ**: Consulta individual ou em lote
- 🎯 **Filtros Avançados**: Estado, cidade, CNAE, situação cadastral, porte
- 📊 **Múltiplas Fontes**: ReceitaWS, BrasilAPI (extensível)
- 💾 **Exportação**: CSV, Excel, JSON
- 🚀 **Performance**: Cache inteligente e rate limiting configurável
- 📝 **Logging**: Registro completo de todas as operações
- 🛡️ **Segurança**: Validação de CNPJ, sanitização de dados

### Recursos Técnicos

- **Rate Limiting**: Controle de frequência de requisições
- **Retry Logic**: Tentativas automáticas com backoff exponencial
- **Cache System**: Evita requisições duplicadas
- **Robots.txt**: Respeita as regras de scraping dos sites
- **Progress Bar**: Visualização do progresso em tempo real
- **Dry-run Mode**: Teste sem fazer requisições reais
- **Deduplicação**: Remove automaticamente registros duplicados

## 📦 Instalação

### Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

### Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/cnpjscrapping.git
cd cnpjscrapping

# Instale as dependências
pip install -r requirements.txt
```

### Instalação com Ambiente Virtual (Recomendado)

```bash
# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Linux/Mac:
source venv/bin/activate
# No Windows:
venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

### Dependências

- `requests>=2.31.0` - Requisições HTTP
- `beautifulsoup4>=4.12.0` - Parsing HTML
- `pandas>=2.1.0` - Manipulação de dados
- `openpyxl>=3.1.0` - Exportação Excel
- `tqdm>=4.66.0` - Barra de progresso
- `selenium>=4.15.0` - Automação web (opcional)

## 🚀 Uso

### Sintaxe Básica

```bash
python scraper.py [opções]
```

### Opções Principais

#### Entrada de Dados

```bash
--cnpj CNPJ                 # CNPJ único para consulta
--cnpj-file ARQUIVO         # Arquivo com lista de CNPJs
```

#### Configuração

```bash
--source {receitaws,brasilapi}  # Fonte de dados (padrão: receitaws)
--delay SEGUNDOS                # Delay entre requisições (padrão: 2)
--no-cache                      # Desabilita cache
--no-robots                     # Ignora robots.txt (não recomendado)
```

#### Filtros

```bash
--estado UF                 # Filtrar por estado (ex: SP, RJ)
--cidade CIDADE             # Filtrar por cidade
--cnae CODIGO               # Filtrar por CNAE
--situacao SITUACAO         # Filtrar por situação cadastral
--porte PORTE               # Filtrar por porte
--apenas-matriz             # Apenas matrizes (excluir filiais)
```

#### Saída

```bash
--output NOME               # Nome do arquivo (sem extensão)
--format {csv,excel,json}   # Formato de exportação
```

#### Controle

```bash
--dry-run                   # Modo teste (não faz requisições)
--verbose                   # Modo verboso (logs detalhados)
--clear-cache               # Limpar cache antes de iniciar
--skip-disclaimer           # Pular aviso legal
```

## 📚 Exemplos

### Exemplo 1: Consultar um único CNPJ

```bash
python scraper.py --cnpj 00000000000191
```

### Exemplo 2: Consultar múltiplos CNPJs

```bash
# Crie um arquivo cnpjs.txt com um CNPJ por linha
echo "00000000000191" > cnpjs.txt
echo "11222333000181" >> cnpjs.txt

# Execute o scraper
python scraper.py --cnpj-file cnpjs.txt --output empresas
```

### Exemplo 3: Filtrar empresas de São Paulo

```bash
python scraper.py --cnpj-file cnpjs.txt --estado SP --output empresas_sp
```

### Exemplo 4: Empresas de TI ativas em SP

```bash
python scraper.py \
  --cnpj-file cnpjs.txt \
  --estado SP \
  --cnae 6201 \
  --situacao ATIVA \
  --output empresas_ti_sp
```

### Exemplo 5: Exportar para Excel

```bash
python scraper.py --cnpj-file cnpjs.txt --format excel --output relatorio
```

### Exemplo 6: Exportar para JSON

```bash
python scraper.py --cnpj-file cnpjs.txt --format json --output dados
```

### Exemplo 7: Modo dry-run (teste)

```bash
# Valida CNPJs sem fazer requisições
python scraper.py --cnpj-file cnpjs.txt --dry-run
```

### Exemplo 8: Modo verboso para debugging

```bash
python scraper.py --cnpj 00000000000191 --verbose
```

### Exemplo 9: Usar fonte alternativa

```bash
python scraper.py --cnpj 00000000000191 --source brasilapi
```

### Exemplo 10: Limpar cache e coletar dados novos

```bash
python scraper.py --cnpj-file cnpjs.txt --clear-cache --no-cache
```

### Exemplo 11: Apenas matrizes

```bash
python scraper.py --cnpj-file cnpjs.txt --apenas-matriz --output matrizes
```

### Exemplo 12: Delay customizado

```bash
# Aguarda 5 segundos entre cada requisição
python scraper.py --cnpj-file cnpjs.txt --delay 5
```

## ⚙️ Configuração

O arquivo `config.json` permite personalizar o comportamento da ferramenta:

```json
{
  "scraping": {
    "user_agent": "CNPJ Scraper Bot/1.0 (Educational Purpose)",
    "default_delay": 2,
    "timeout": 30,
    "max_retries": 3,
    "backoff_factor": 2,
    "respect_robots_txt": true,
    "cache_enabled": true,
    "cache_duration_hours": 24
  },
  "export": {
    "default_format": "csv",
    "output_directory": "data",
    "include_timestamp": true
  },
  "logging": {
    "level": "INFO",
    "log_directory": "logs",
    "max_log_size_mb": 10,
    "backup_count": 5
  }
}
```

### Parâmetros Importantes

- **user_agent**: Identifica sua aplicação (seja honesto!)
- **default_delay**: Tempo entre requisições (respeite os servidores)
- **max_retries**: Número de tentativas em caso de falha
- **cache_duration_hours**: Tempo de validade do cache
- **respect_robots_txt**: SEMPRE deixe como `true`

## 🌐 Fontes de Dados

### ReceitaWS (Padrão)

- **URL**: https://www.receitaws.com.br
- **Tipo**: API REST pública
- **Rate Limit**: 3 requisições/minuto
- **Autenticação**: Não requerida
- **Status**: ✅ Ativa

### BrasilAPI

- **URL**: https://brasilapi.com.br
- **Tipo**: API REST pública
- **Rate Limit**: 2 requisições/segundo
- **Autenticação**: Não requerida
- **Status**: ✅ Ativa

### Como Adicionar Novas Fontes

1. Crie uma classe que herda de `BaseScraper`
2. Implemente os métodos `fetch_company_data()` e `get_source_name()`
3. Adicione a configuração em `config.json`

Exemplo:

```python
from cnpj_scraper.scrapers import BaseScraper

class MinhaAPIScaper(BaseScraper):
    def get_source_name(self):
        return "MinhaAPI"

    def fetch_company_data(self, cnpj):
        # Sua implementação aqui
        pass
```

## 🎯 Boas Práticas

### Rate Limiting

**SEMPRE** respeite o rate limiting:

- ✅ Use delay mínimo de 2 segundos
- ✅ Aumente o delay se necessário
- ✅ Monitore a carga do servidor
- ❌ Não faça requisições em paralelo sem autorização

### Robots.txt

**SEMPRE** respeite o robots.txt:

```bash
# ✅ CORRETO (padrão)
python scraper.py --cnpj-file cnpjs.txt

# ❌ ERRADO (só use se tiver certeza)
python scraper.py --cnpj-file cnpjs.txt --no-robots
```

### Cache

Use o cache para evitar requisições duplicadas:

- ✅ Deixe o cache habilitado (padrão)
- ✅ Limpe o cache periodicamente
- ✅ Use `--clear-cache` para forçar atualização

### User-Agent

Use um User-Agent identificável:

```json
{
  "user_agent": "NomeDoProjeto/1.0 (email@exemplo.com; Finalidade)"
}
```

### Horários

Evite horários de pico:

- ✅ Faça scraping em horários de menor tráfego
- ✅ Distribua requisições ao longo do dia
- ❌ Não faça scraping intensivo em horário comercial

## 📁 Estrutura do Projeto

```
cnpjscrapping/
├── cnpj_scraper/                 # Pacote principal
│   ├── __init__.py
│   ├── filters.py                # Filtros de dados
│   ├── scrapers/                 # Módulos de scraping
│   │   ├── __init__.py
│   │   ├── base_scraper.py       # Classe base
│   │   ├── receitaws_scraper.py  # Scraper ReceitaWS
│   │   └── brasilapi_scraper.py  # Scraper BrasilAPI
│   ├── exporters/                # Exportação de dados
│   │   ├── __init__.py
│   │   └── data_exporter.py      # Exportador
│   └── utils/                    # Utilitários
│       ├── __init__.py
│       ├── cnpj_validator.py     # Validação de CNPJ
│       ├── robots_checker.py     # Verificação robots.txt
│       ├── logger.py             # Sistema de logs
│       └── cache_manager.py      # Gerenciamento de cache
├── logs/                         # Arquivos de log
├── data/                         # Dados exportados
├── cache/                        # Cache de requisições
├── config.json                   # Configurações
├── requirements.txt              # Dependências
├── scraper.py                    # Script principal
└── README.md                     # Este arquivo
```

## 💻 Desenvolvimento

### Executar Testes

```bash
# TODO: Adicionar testes
python -m pytest tests/
```

### Validar CNPJ Programaticamente

```python
from cnpj_scraper.utils import validate_cnpj, format_cnpj

cnpj = "00000000000191"
if validate_cnpj(cnpj):
    print(f"CNPJ válido: {format_cnpj(cnpj)}")
```

### Usar Scraper Programaticamente

```python
from cnpj_scraper.scrapers import ReceitaWSScraper
from cnpj_scraper.utils import CacheManager

# Configura cache
cache = CacheManager()

# Cria scraper
scraper = ReceitaWSScraper(
    user_agent="Meu App/1.0",
    delay=2,
    cache_manager=cache
)

# Busca dados
data = scraper.fetch_company_data("00000000000191")
print(data)
```

### Contribuir

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## ❓ FAQ

### O scraper é legal?

Sim, desde que usado para coletar apenas dados públicos e respeitando os termos de uso dos sites.

### Preciso de autorização?

Para dados públicos de CNPJs, não. Mas sempre verifique os termos de uso de cada fonte.

### Qual o limite de requisições?

Depende da fonte. ReceitaWS: ~3/min. BrasilAPI: ~2/seg. Sempre respeite o rate limiting.

### Os dados são confiáveis?

Os dados vêm de fontes públicas que consultam a Receita Federal. Sempre valide informações críticas.

### Posso usar comercialmente?

Sim, mas verifique a licença das APIs usadas e a LGPD.

### Como reportar problemas?

Abra uma issue no GitHub com detalhes do problema.

### O scraper está lento?

Isso é intencional (rate limiting). Não aumente a velocidade sem necessidade.

### Posso desabilitar o robots.txt?

Tecnicamente sim, mas é altamente desencorajado e antiético.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

```
MIT License

Copyright (c) 2024 CNPJ Scraper Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Agradecimentos

- [ReceitaWS](https://www.receitaws.com.br) - API pública de CNPJs
- [BrasilAPI](https://brasilapi.com.br) - API pública de dados brasileiros
- Comunidade Python Brasil

## 📞 Contato

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/cnpjscrapping/issues)
- **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/cnpjscrapping/discussions)

---

**⚠️ LEMBRE-SE: Use esta ferramenta de forma ética e responsável!**

Desenvolvido com ❤️ para a comunidade Python Brasil
