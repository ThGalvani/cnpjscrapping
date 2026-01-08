# 🏪 Guia: Buscar MEI e ME por Região

## 🎯 Nova Funcionalidade AVANÇADA!

Agora você pode **buscar Microempreendedores Individuais (MEI) e Microempresas (ME) em qualquer cidade do Brasil!**

Isso é MUITO MELHOR do que as categorias pré-definidas porque:
- ✅ **Milhões de empresas** (vs. algumas dezenas)
- ✅ **Filtragem por região** (sua cidade específica)
- ✅ **Dados reais da Receita Federal** (oficiais e atualizados)
- ✅ **MEI e ME têm mais telefones públicos**
- ✅ **Até 500 empresas por busca**

---

## 📋 Pré-Requisito: Baixar Dados da Receita

### Por que baixar?

Os dados não vêm incluídos porque são **MUITO grandes** (~3GB essencial, ~30GB completo).
Mas são **públicos e gratuitos**!

### Como baixar:

**Opção 1: Download Automático (Recomendado)**

```powershell
# Windows PowerShell ou CMD
cd caminho\para\cnpjscrapping
py -m cnpj_scraper.scrapers.receita_downloader
```

**Escolha a opção 1** (Download essencial - ~3GB)

**Opção 2: Download Manual**

1. Acesse: https://dadosabertos.rfb.gov.br/CNPJ/
2. Baixe: `Estabelecimentos0.zip` (~3GB)
3. Extraia na pasta `receita_data/`

---

## 🚀 Como Usar

### Interface Web (MAIS FÁCIL!)

1. **Inicie a aplicação:**
   ```powershell
   # Windows
   py -m uvicorn api:app --reload --port 8000

   # Ou use os scripts:
   iniciar.bat  # CMD
   .\iniciar.ps1  # PowerShell
   ```

2. **Acesse:** http://localhost:8000/web

3. **Clique na aba:** "🏪 MEI/ME por Região" (primeira aba)

4. **Preencha:**
   - **Cidade:** Ex: São Paulo, Campinas, Curitiba
   - **Estado:** Selecione a UF
   - **Quantidade:** 20, 50, 100, 200 ou 500
   - **Marque:** "Apenas com telefone" (recomendado)

5. **Clique:** "🔍 Buscar MEI/ME"

6. **Aguarde:** Processamento (pode demorar 10-30s para primeiro resultado)

7. **Veja os resultados** com:
   - Razão Social
   - Nome Fantasia
   - **CNPJ**
   - **Porte** (MEI ou ME)
   - **📞 TELEFONE** (destaque)
   - **📧 Email**
   - **📍 Endereço Completo**
   - Situação Cadastral

8. **Exporte:** Clique em "💾 Exportar para CSV"

---

## 📊 Exemplos Práticos

### Exemplo 1: MEI/ME em São Paulo

```
Cidade: São Paulo
Estado: SP
Quantidade: 50
Apenas com telefone: ✓

Resultado: 50 MEI/ME com telefones em SP
```

### Exemplo 2: ME em Campinas

```
Cidade: Campinas
Estado: SP
Quantidade: 100
Apenas com telefone: ✓

Resultado: 100 microempresas de Campinas
```

### Exemplo 3: Todos os MEI do Rio

```
Cidade: Rio de Janeiro
Estado: RJ
Quantidade: 500
Apenas com telefone: ✓

Resultado: Até 500 MEIs do RJ
```

---

## 🎯 Por que MEI e ME?

### MEI (Microempreendedor Individual)
- Faturamento até R$ 81mil/ano
- 1 funcionário
- **Maioria tem telefone público**
- Exemplos: Cabeleireiros, eletricistas, freelancers

### ME (Microempresa)
- Faturamento até R$ 360mil/ano (comércio) ou R$ 900mil (indústria)
- Até 19 funcionários
- **Maioria tem telefone público**
- Exemplos: Lojas pequenas, prestadores de serviço

### Por que são melhores?

1. **Quantidade**: Milhões vs. centenas
2. **Telefones**: ~70% têm telefone público
3. **Locais**: Próximos à população
4. **Atualizados**: Base da Receita é oficial

---

## 💻 Uso via API

```bash
# Buscar MEI/ME em São Paulo
curl -X POST "http://localhost:8000/api/discover/mei-me-by-region?cidade=São Paulo&estado=SP&limit=50&only_with_phone=true"

# Ver status dos dados
curl "http://localhost:8000/api/receita/status"
```

---

## 📈 Performance

### Primeira Busca
- **Tempo:** 10-60 segundos
- **Por quê:** Processa arquivos grandes

### Buscas Subsequentes (mesma cidade)
- **Tempo:** < 1 segundo
- **Por quê:** Usa cache

### Otimizações
- Cache automático por cidade
- Leitura otimizada dos CSVs
- Filtros em tempo de leitura

---

## 🔧 Configurações Avançadas

### Baixar Base Completa (~30GB)

Para buscar em TODAS as cidades sem delay:

```powershell
py -m cnpj_scraper.scrapers.receita_downloader
# Escolha opção 2
```

Inclui:
- 10 arquivos de Estabelecimentos
- 10 arquivos de Empresas
- Tabelas auxiliares (CNAEs, Municípios, etc.)

### Limpar Cache

```powershell
# Via API
curl -X POST "http://localhost:8000/api/cache/clear"

# Via Python
py -c "from cnpj_scraper.scrapers.receita_processor import ReceitaProcessor; ReceitaProcessor().clear_cache()"
```

---

## 🎁 Casos de Uso

### 1. Cold Calling por Região
```
Objetivo: Ligar para MEIs de um bairro
Busca: Cidade específica + Apenas com telefone
Resultado: Lista focada e local
```

### 2. Pesquisa de Mercado
```
Objetivo: Entender quantidade de MEs em uma cidade
Busca: Cidade + Sem filtro de telefone
Resultado: Visão completa do mercado
```

### 3. Prospecção B2B
```
Objetivo: Vender para microempresas
Busca: Múltiplas cidades + 500 resultados
Resultado: Base ampla de prospects
```

### 4. Análise Setorial
```
Objetivo: Estudar MEIs de uma região
Busca: Cidade + Exportar tudo
Resultado: Planilha para análise
```

---

## 🐛 Problemas Comuns

### "Dados da Receita Federal não disponíveis"

**Solução:**
```powershell
py -m cnpj_scraper.scrapers.receita_downloader
# Escolha opção 1 (3GB)
# Aguarde download
# Tente novamente
```

### "Nenhuma empresa encontrada"

**Causas:**
- Nome da cidade errado (tente sem acent

os)
- Estado errado
- Cidade muito pequena (< 50 empresas)

**Solução:**
- Verifique ortografia
- Tente cidade maior próxima
- Desmarque "apenas com telefone"

### "Busca muito lenta"

**Normal na primeira busca!**
- Primeira vez: 10-60s (processa arquivo)
- Próximas vezes: < 1s (usa cache)

**Acelerar:**
- Baixe base completa (~30GB)
- Reduza quantidade de resultados
- Use cache (automático)

### "Poucas empresas com telefone"

**Normal!** Nem todas têm telefone público.

**Dica:**
- Aumente quantidade de resultados
- Desmarque "apenas com telefone"
- Tente cidade maior

---

## 📚 Dados Técnicos

### Formato dos Arquivos

**Estabelecimentos:**
- Formato: CSV separado por ;
- Encoding: Latin-1
- Tamanho: ~300MB cada (10 arquivos)
- Contém: Telefones, endereços, emails

**Empresas:**
- Formato: CSV separado por ;
- Encoding: Latin-1
- Tamanho: ~100MB cada (10 arquivos)
- Contém: Razão social, porte, capital

### Códigos de Porte

- `01`: MEI
- `03`: ME (Microempresa)
- `05`: EPP (Empresa de Pequeno Porte)
- `00`: Não Informado

### Situação Cadastral

- `02`: ATIVA (filtro padrão)
- `01`: NULA
- `03`: SUSPENSA
- `04`: INAPTA
- `08`: BAIXADA

---

## 🔗 Links Úteis

- **Dados Oficiais:** https://dadosabertos.rfb.gov.br/CNPJ/
- **Layout dos Arquivos:** https://www.gov.br/receitafederal/dados-publicos-cnpj
- **API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:8000/web

---

## ⚡ Resumo Rápido

### Para começar:

```powershell
# 1. Baixar dados (uma vez só, ~3GB)
py -m cnpj_scraper.scrapers.receita_downloader
# Escolha opção 1

# 2. Iniciar aplicação
py -m uvicorn api:app --reload --port 8000

# 3. Acessar
http://localhost:8000/web

# 4. Aba "MEI/ME por Região"
# 5. Preencher cidade + estado
# 6. Buscar!
```

---

## 🎉 Vantagens vs. Busca por Categoria

| Aspecto | Categoria | MEI/ME por Região |
|---------|-----------|-------------------|
| **Quantidade** | ~5-10 empresas | Até 500 empresas |
| **Fonte** | APIs públicas | Receita Federal |
| **Cobertura** | Grandes empresas | Todas (MEI/ME) |
| **Região** | Nacional | Sua cidade |
| **Telefones** | ~40% | ~70% |
| **Dados** | Amostra | Base completa |
| **Velocidade** | 5-10s | 10-60s (cache: <1s) |
| **Setup** | Zero | Download 3GB |

---

## 💡 Dicas Profissionais

1. **Cache é seu amigo:**
   - Primeira busca demora
   - Próximas são instantâneas
   - Cache persiste entre sessões

2. **Quantidade ideal:**
   - Teste: 20-50
   - Produção: 100-200
   - Máximo: 500

3. **Exportação:**
   - Sempre exporte para CSV
   - Importe no Excel/CRM
   - Mantenha backup local

4. **Múltiplas cidades:**
   - Faça buscas separadas
   - Exporte cada uma
   - Combine depois no Excel

5. **Atualização:**
   - Receita atualiza mensalmente
   - Re-baixe dados periodicamente
   - Limpe cache ao atualizar

---

**Desenvolvido para maximizar seus resultados! 🎯**

**Dúvidas? Acesse `/docs` para documentação completa da API.**
