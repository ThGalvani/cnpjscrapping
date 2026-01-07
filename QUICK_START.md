# 🚀 Quick Start - Deploy em 5 Minutos

## Opção 1: Railway (MAIS FÁCIL - Recomendado) 🚂

1. **Acesse**: https://railway.app
2. **Faça login** com sua conta GitHub
3. **Clique em** "New Project"
4. **Selecione** "Deploy from GitHub repo"
5. **Escolha** o repositório `cnpjscrapping`
6. **Aguarde** o deploy automático (~2 minutos)
7. **Acesse** a URL gerada e adicione `/web` no final

✅ **Pronto!** Sua aplicação está online com:
- Interface web em `https://seu-app.up.railway.app/web`
- API docs em `https://seu-app.up.railway.app/docs`

**Custo**: $5 grátis por mês (suficiente para uso moderado)

---

## Opção 2: Render (100% GRÁTIS) 🎨

1. **Acesse**: https://render.com
2. **Faça login** com GitHub
3. **Clique** em "New +" → "Web Service"
4. **Conecte** o repositório GitHub
5. **Render detectará** automaticamente o `render.yaml`
6. **Clique** em "Create Web Service"
7. **Aguarde** o deploy (~3 minutos)

✅ **Pronto!** Acesse em:
- `https://seu-app.onrender.com/web`

**Custo**: 100% grátis (750h/mês)
**Atenção**: Hiberna após 15 min de inatividade

---

## Opção 3: Local (Desenvolvimento) 💻

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar API
uvicorn api:app --reload --port 8000

# Acessar
# http://localhost:8000/web
```

---

## Opção 4: Docker 🐳

```bash
# Iniciar com Docker Compose
docker-compose up -d

# Acessar
# http://localhost:8000/web
```

---

## 📱 Como Usar Após o Deploy

1. **Acesse** `sua-url/web`
2. **Digite** um CNPJ ou lista de CNPJs
3. **Clique** em "Consultar"
4. **Veja** os resultados em tempo real!

**Recursos disponíveis:**
- ✅ Consulta única
- ✅ Consulta em lote (até 100 CNPJs)
- ✅ Filtros por estado, cidade, CNAE, situação
- ✅ Estatísticas em tempo real
- ✅ Cache automático

---

## 🆘 Precisa de Ajuda?

- 📚 **Documentação Completa**: [DEPLOY.md](DEPLOY.md)
- 🐛 **Problemas**: Abra uma issue no GitHub
- 💬 **Dúvidas**: Consulte o [README.md](README.md)

---

## ⚡ Dicas Rápidas

**Para testar rapidamente:**
1. Use o Railway (mais rápido)
2. Acesse `/web` (interface visual)
3. Digite um CNPJ válido: `00000000000191`

**Para produção:**
1. Configure variáveis de ambiente
2. Ajuste rate limiting em `config.json`
3. Monitore uso via `/api/stats`

**Para desenvolver:**
1. Clone o repo
2. `pip install -r requirements.txt`
3. `uvicorn api:app --reload`

---

## 🎯 Próximos Passos

Depois do deploy:

1. **Teste** a interface web
2. **Configure** filtros personalizados
3. **Monitore** estatísticas em `/api/stats`
4. **Ajuste** rate limiting se necessário
5. **Compartilhe** com seu amigo! 🎉

**Desenvolvido com ❤️ para facilitar seu trabalho**
