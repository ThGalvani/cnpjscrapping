# 📞 Guia: Buscar Telefones de Empresas em Massa

## 🎯 Nova Funcionalidade!

Agora você pode **buscar telefones de várias empresas de uma vez** sem precisar fornecer CNPJs manualmente!

## Como Funciona?

A ferramenta agora permite:
1. ✅ **Buscar empresas por categoria** (Tecnologia, Varejo, Bancos, etc.)
2. ✅ **Coletar dados de múltiplas empresas automaticamente**
3. ✅ **Filtrar apenas empresas com telefone**
4. ✅ **Exportar para CSV com um clique**

## 🚀 Como Usar

### Opção 1: Interface Web (Mais Fácil!)

1. **Acesse** `http://localhost:8000/web` (ou sua URL de deploy)
2. **Clique** na aba "📞 Buscar Telefones"
3. **Selecione** uma categoria:
   - 💻 Tecnologia
   - 🛒 Varejo
   - 🏦 Bancos
   - 🔧 Serviços
   - 🏭 Indústria
4. **Clique** em "🔍 Buscar Telefones"
5. **Veja** os resultados com telefones destacados
6. **Exporte** para CSV clicando em "💾 Exportar para CSV"

### Opção 2: API (Para Integração)

```bash
# Buscar empresas de tecnologia com telefones
curl -X POST "http://localhost:8000/api/discover/by-category?category=tecnologia&collect_phones=true"

# Ver categorias disponíveis
curl "http://localhost:8000/api/categories"

# Buscar com filtros customizados
curl -X POST "http://localhost:8000/api/discover/by-criteria?category=varejo&limit=20"
```

## 📊 Exemplos de Uso

### Exemplo 1: Buscar Telefones de Empresas de TI

```
1. Selecione categoria: Tecnologia
2. Fonte: ReceitaWS
3. Marque: "Retornar apenas com telefone"
4. Clique em "Buscar"
```

**Resultado:** Lista de empresas de tecnologia com seus telefones

### Exemplo 2: Buscar Telefones de Lojas de Varejo

```
1. Selecione categoria: Varejo
2. Fonte: BrasilAPI
3. Clique em "Buscar"
```

**Resultado:** Lojas e e-commerces com dados de contato

### Exemplo 3: Exportar para Excel/CRM

```
1. Faça a busca
2. Clique em "Exportar para CSV"
3. Abra no Excel ou importe no seu CRM
```

## 📱 Dados Coletados

Para cada empresa, você recebe:
- ✅ **CNPJ** (formatado)
- ✅ **Razão Social**
- ✅ **Nome Fantasia**
- ✅ **📞 Telefone** (destaque)
- ✅ **📧 Email**
- ✅ **📍 Endereço Completo**
- ✅ **Situação Cadastral**

## 🎯 Casos de Uso

### Para Vendas/Marketing
- Montar lista de prospects por setor
- Coletar telefones para cold calling
- Segmentar por região e atividade

### Para Pesquisa
- Estudar empresas de um setor
- Análise de mercado regional
- Validação de dados públicos

### Para Conformidade
- Verificar situação cadastral
- Validar dados de parceiros
- Auditoria de informações

## 🔄 Fontes de Dados

### ReceitaWS (Padrão)
- ✅ Dados completos
- ✅ Telefones e emails
- ⚠️ Rate limit: 3 req/min

### BrasilAPI
- ✅ Dados oficiais
- ✅ Rápido
- ⚠️ Menos telefones disponíveis

## 📈 Estatísticas

Após a busca, você vê:
- Total de empresas encontradas
- Quantas têm telefone
- Percentual de cobertura

## 💡 Dicas

### Para Melhor Cobertura
1. Use **ReceitaWS** (mais telefones)
2. Teste **ambas as fontes**
3. Combine resultados

### Para Exportação
- Exporte para CSV
- Abra no Excel
- Importe no Google Sheets
- Use em ferramentas de CRM

### Para Grandes Volumes
- Busque por categoria primeiro
- Depois refine manualmente
- Use a consulta em lote para CNPJs específicos

## ⚠️ Limitações e Avisos

### Limitações Técnicas
- **Categorias**: 5 pré-definidas (por enquanto)
- **Volume**: ~5-10 empresas por categoria (amostra)
- **Rate Limiting**: Respeita limites das APIs

### Para Busca por Cidade/CNAE
Para buscar por **cidade específica** ou **CNAE**:
1. Baixe dados abertos da Receita Federal
2. URL: https://www.gov.br/receitafederal/dados-publicos-cnpj
3. Configure o módulo `receita_data.py`

### Uso Ético
- ✅ Apenas dados públicos
- ✅ Respeite LGPD
- ✅ Use para fins legítimos
- ❌ Não use para SPAM
- ❌ Não sobrecarregue APIs

## 🚀 Próximos Passos

### Expansão Planejada
1. **Mais categorias**
   - Saúde
   - Educação
   - Alimentação
   - Construção

2. **Busca por região**
   - Por estado
   - Por cidade
   - Por CEP

3. **Busca por CNAE**
   - CNAE específico
   - Subcategorias
   - Atividades similares

4. **Filtros avançados**
   - Porte da empresa
   - Capital social
   - Data de abertura

## 📚 Documentação da API

### Endpoints Novos

**GET /api/categories**
```json
{
  "categories": [
    {
      "id": "tecnologia",
      "name": "Tecnologia",
      "description": "Empresas de TI, software, hardware",
      "sample_count": 5
    }
  ]
}
```

**POST /api/discover/by-category**
```
?category=tecnologia
&source=receitaws
&collect_phones=true
```

**POST /api/discover/by-criteria**
```
?category=varejo
&limit=20
&collect_phones=true
```

## 🆘 Problemas Comuns

### "Nenhuma empresa encontrada"
- ✅ Tente outra categoria
- ✅ Tente outra fonte de dados
- ✅ Verifique conexão com API

### "Poucas empresas com telefone"
- ✅ Normal - nem todas têm telefone público
- ✅ Tente ReceitaWS (mais completo)
- ✅ Combine com busca manual

### "API lenta"
- ✅ Rate limiting está ativo (proposital)
- ✅ Aguarde entre requisições
- ✅ Use cache quando possível

## 🎉 Exemplo Completo

```bash
# 1. Iniciar API
uvicorn api:app --reload

# 2. Acessar interface
# http://localhost:8000/web

# 3. Buscar telefones
# - Selecionar: Tecnologia
# - Clicar: Buscar Telefones
# - Ver: 5 empresas com dados

# 4. Exportar
# - Clicar: Exportar para CSV
# - Abrir: telefones_empresas_2024-01-07.csv

# 5. Usar dados
# - Importar no CRM
# - Fazer cold calling
# - Enviar emails
```

## 🔗 Links Úteis

- **API Docs**: `/docs`
- **Frontend**: `/web`
- **Stats**: `/api/stats`
- **Código**: `cnpj_scraper/scrapers/discovery.py`

---

**Desenvolvido para facilitar coleta ética de dados públicos!** 🎯

**Dúvidas?** Consulte `/docs` para documentação completa da API.
