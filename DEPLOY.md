# 🚀 Guia de Deploy - CNPJ Scraper API

Este guia mostra como fazer deploy da aplicação CNPJ Scraper em diferentes plataformas de hospedagem.

## 📋 Índice

- [Opções de Deploy](#opções-de-deploy)
- [Railway (Recomendado)](#railway-recomendado)
- [Render](#render)
- [Fly.io](#flyio)
- [Google Cloud Run](#google-cloud-run)
- [Docker](#docker-local)
- [Desenvolvimento Local](#desenvolvimento-local)

---

## 🎯 Opções de Deploy

### Comparação de Plataformas

| Plataforma | Plano Gratuito | Python Support | Facilidade | Recomendado |
|------------|---------------|----------------|------------|-------------|
| **Railway** | ✅ $5 créditos/mês | ✅ Excelente | ⭐⭐⭐⭐⭐ | ✅ **Sim** |
| **Render** | ✅ 750h/mês | ✅ Nativo | ⭐⭐⭐⭐ | ✅ Sim |
| **Fly.io** | ✅ Limitado | ✅ Docker | ⭐⭐⭐ | ✅ Sim |
| **Vercel** | ✅ Ilimitado | ⚠️ Serverless | ⭐⭐ | ❌ Não* |
| **Heroku** | ❌ Pago | ✅ Nativo | ⭐⭐⭐⭐ | ⚠️ Pago |

\* Vercel tem limitações para Python e scraping de longa duração

---

## 🚂 Railway (Recomendado)

Railway é a opção mais fácil e com melhor suporte para Python.

### Vantagens
- ✅ Deploy automático via GitHub
- ✅ $5 em créditos grátis por mês
- ✅ Suporte nativo para Python
- ✅ Fácil configuração
- ✅ Logs em tempo real
- ✅ Domínio HTTPS gratuito

### Passo a Passo

1. **Criar conta no Railway**
   - Acesse: https://railway.app
   - Faça login com GitHub

2. **Criar novo projeto**
   ```bash
   # Opção 1: Deploy via GitHub
   - Clique em "New Project"
   - Selecione "Deploy from GitHub repo"
   - Escolha o repositório cnpjscrapping

   # Opção 2: Deploy via CLI
   npm install -g @railway/cli
   railway login
   railway init
   railway up
   ```

3. **Configurar variáveis de ambiente** (opcional)
   ```
   PORT=8000
   LOG_LEVEL=INFO
   ```

4. **Acessar a aplicação**
   - Railway gerará uma URL automática
   - Exemplo: `https://cnpj-scraper-production.up.railway.app`
   - Acesse `/web` para o frontend
   - Acesse `/docs` para a documentação da API

### Configuração Automática

O arquivo `railway.json` já está configurado:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api:app --host 0.0.0.0 --port $PORT"
  }
}
```

---

## 🎨 Render

Render oferece um plano gratuito generoso com 750 horas/mês.

### Vantagens
- ✅ 750 horas gratuitas/mês
- ✅ Deploy automático via GitHub
- ✅ SSL/TLS gratuito
- ✅ Suporte nativo para Python
- ⚠️ Pode hibernar após inatividade (plano gratuito)

### Passo a Passo

1. **Criar conta no Render**
   - Acesse: https://render.com
   - Faça login com GitHub

2. **Criar novo Web Service**
   - Clique em "New +" → "Web Service"
   - Conecte o repositório do GitHub
   - Render detectará automaticamente o `render.yaml`

3. **Configurações**
   ```yaml
   # Já configurado em render.yaml
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn api:app --host 0.0.0.0 --port $PORT
   ```

4. **Deploy**
   - Clique em "Create Web Service"
   - Aguarde o build completar
   - Acesse a URL gerada

### Atenção
- No plano gratuito, o serviço hiberna após 15 min de inatividade
- Primeira requisição após hibernação pode demorar ~30s

---

## ✈️ Fly.io

Fly.io usa Docker e oferece recursos generosos no plano gratuito.

### Vantagens
- ✅ 3 VMs gratuitas (256MB RAM cada)
- ✅ Deploy global (várias regiões)
- ✅ Baseado em Docker
- ✅ Escala automática

### Passo a Passo

1. **Instalar Fly CLI**
   ```bash
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh

   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Login e inicializar**
   ```bash
   fly auth login
   fly launch
   ```

3. **Configurar aplicação**
   ```bash
   # Fly perguntará:
   - App name: cnpj-scraper (ou seu nome)
   - Region: São Paulo (gru) ou nearest
   - Database: No
   ```

4. **Deploy**
   ```bash
   fly deploy
   ```

5. **Abrir aplicação**
   ```bash
   fly open /web
   ```

### Comandos Úteis
```bash
fly status              # Status da app
fly logs                # Ver logs
fly scale count 1       # Escalar para 1 instância
fly secrets set KEY=VAL # Definir variáveis de ambiente
```

---

## ☁️ Google Cloud Run

Para quem já usa Google Cloud Platform.

### Passo a Passo

1. **Instalar gcloud CLI**
   - https://cloud.google.com/sdk/docs/install

2. **Autenticar**
   ```bash
   gcloud auth login
   gcloud config set project SEU_PROJETO
   ```

3. **Build e Deploy**
   ```bash
   # Build da imagem
   gcloud builds submit --tag gcr.io/SEU_PROJETO/cnpj-scraper

   # Deploy no Cloud Run
   gcloud run deploy cnpj-scraper \
     --image gcr.io/SEU_PROJETO/cnpj-scraper \
     --platform managed \
     --region southamerica-east1 \
     --allow-unauthenticated \
     --port 8000
   ```

4. **Acessar URL**
   - Cloud Run fornecerá uma URL HTTPS automática

---

## 🐳 Docker (Local)

Para desenvolvimento e testes locais.

### Opção 1: Docker Compose (Recomendado)

```bash
# Iniciar aplicação
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar aplicação
docker-compose down

# Acessar
# http://localhost:8000/web
# http://localhost:8000/docs
```

### Opção 2: Docker Manual

```bash
# Build da imagem
docker build -t cnpj-scraper .

# Executar container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/cache:/app/cache \
  --name cnpj-scraper \
  cnpj-scraper

# Ver logs
docker logs -f cnpj-scraper

# Parar container
docker stop cnpj-scraper
docker rm cnpj-scraper
```

---

## 💻 Desenvolvimento Local

Para desenvolver localmente sem Docker.

### 1. Instalar Dependências

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Executar API

```bash
# Modo desenvolvimento (com reload)
uvicorn api:app --reload --port 8000

# Ou usando Python
python api.py
```

### 3. Acessar Aplicação

- **Frontend**: http://localhost:8000/web
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 4. Testar API

```bash
# Consultar CNPJ
curl -X POST "http://localhost:8000/api/cnpj/search" \
  -H "Content-Type: application/json" \
  -d '{"cnpj": "00000000000191", "source": "receitaws"}'

# Health check
curl http://localhost:8000/health

# Estatísticas
curl http://localhost:8000/api/stats
```

---

## 🔧 Configurações Avançadas

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```bash
cp .env.example .env
```

Variáveis disponíveis:
```env
PORT=8000                    # Porta da API
HOST=0.0.0.0                # Host da API
LOG_LEVEL=INFO              # Nível de log
CACHE_DURATION_HOURS=24     # Duração do cache
DEFAULT_DELAY=2             # Delay entre requisições
MAX_RETRIES=3               # Tentativas máximas
```

### Domínio Customizado

#### Railway
1. Vá em Settings → Domains
2. Adicione seu domínio
3. Configure DNS CNAME

#### Render
1. Vá em Settings → Custom Domain
2. Adicione seu domínio
3. Configure DNS

---

## 🎯 Recomendação Final

**Para começar rapidamente: Railway** 🚂
- Mais fácil de configurar
- Deploy em minutos
- $5 de créditos grátis
- Melhor suporte para Python

**Para produção com mais controle: Fly.io** ✈️
- Baseado em Docker
- Deploy global
- Mais configurável

**Para uso empresarial: Google Cloud Run** ☁️
- Escalável
- Integração com GCP
- Pay-per-use

---

## 🆘 Problemas Comuns

### Erro: "Module not found"
```bash
# Certifique-se que requirements.txt está completo
pip install -r requirements.txt
```

### Erro: "Port already in use"
```bash
# Mudar porta
PORT=8001 uvicorn api:app
```

### API muito lenta
```bash
# Verificar delay e cache
# Ajustar em config.json
```

### Cache ocupando muito espaço
```bash
# Limpar cache via API
curl -X POST http://localhost:8000/api/cache/clear
```

---

## 📚 Recursos Adicionais

- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs/)

---

## 🤝 Suporte

Encontrou algum problema? Abra uma issue no GitHub!

**Desenvolvido com ❤️ para a comunidade Python Brasil**
