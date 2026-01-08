# 🪟 Guia de Instalação - Windows

## 📋 Passo a Passo para Iniciantes

### ✅ Passo 1: Verificar se Python está instalado

Abra o **PowerShell** ou **CMD** e tente:

```powershell
python --version
```

ou

```powershell
py --version
```

**Resultado esperado:**
```
Python 3.11.x
```

---

### 🔧 Passo 2A: Se Python NÃO está instalado

1. **Baixe Python:**
   - Acesse: https://www.python.org/downloads/
   - Clique em "Download Python 3.11.x"

2. **IMPORTANTE na instalação:**
   - ✅ **MARQUE** a opção: **"Add Python to PATH"** (MUITO IMPORTANTE!)
   - Clique em "Install Now"
   - Aguarde a instalação

3. **Reinicie o PowerShell/CMD**

4. **Teste novamente:**
   ```powershell
   python --version
   ```

---

### 🔧 Passo 2B: Se Python está instalado mas pip não funciona

No Windows, tente usar `py` ao invés de `python` e `pip`:

```powershell
# Ao invés de:
pip install -r requirements.txt

# Use:
py -m pip install -r requirements.txt
```

---

### 📦 Passo 3: Instalar Dependências

**Navegue até o diretório do projeto:**

```powershell
cd caminho\para\cnpjscrapping
```

**Instale as dependências:**

```powershell
# Opção 1 (se pip funcionar):
pip install -r requirements.txt

# Opção 2 (mais seguro no Windows):
py -m pip install -r requirements.txt

# Opção 3 (se python funcionar):
python -m pip install -r requirements.txt
```

**Aguarde a instalação** (~2-3 minutos)

---

### 🚀 Passo 4: Iniciar a Aplicação

**Depois de instalar, inicie a API:**

```powershell
# Opção 1:
uvicorn api:app --reload --port 8000

# Opção 2 (se uvicorn não funcionar):
py -m uvicorn api:app --reload --port 8000

# Opção 3:
python -m uvicorn api:app --reload --port 8000
```

**Ou use o script Python direto:**

```powershell
python api.py
```

---

### 🌐 Passo 5: Acessar a Aplicação

Abra o navegador em:

**Interface Web:**
```
http://localhost:8000/web
```

**Documentação da API:**
```
http://localhost:8000/docs
```

---

## 🐛 Problemas Comuns

### Problema 1: "python não é reconhecido"

**Solução:**
```powershell
# Use 'py' ao invés de 'python'
py --version
py -m pip install -r requirements.txt
```

### Problema 2: "pip não é reconhecido"

**Solução:**
```powershell
# Use 'py -m pip'
py -m pip install -r requirements.txt
py -m pip install --upgrade pip
```

### Problema 3: "uvicorn não é reconhecido"

**Solução:**
```powershell
# Use 'py -m uvicorn'
py -m uvicorn api:app --reload --port 8000

# Ou rode o script diretamente:
py api.py
```

### Problema 4: "Erro de permissão"

**Solução:**
Abra o PowerShell como **Administrador**:
1. Clique com botão direito no PowerShell
2. Selecione "Executar como Administrador"
3. Tente novamente

### Problema 5: "ModuleNotFoundError"

**Solução:**
```powershell
# Reinstale as dependências
py -m pip install -r requirements.txt --force-reinstall
```

---

## 🎯 Método Alternativo: Usando Ambiente Virtual

**Recomendado para evitar conflitos:**

### Criar ambiente virtual:

```powershell
# Navegue até o projeto
cd caminho\para\cnpjscrapping

# Crie o ambiente virtual
py -m venv venv

# Ative o ambiente virtual
.\venv\Scripts\Activate.ps1
```

**Se der erro de política de execução:**
```powershell
# Execute como Administrador:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Depois tente ativar novamente:
.\venv\Scripts\Activate.ps1
```

### Instalar dependências no ambiente virtual:

```powershell
# Com ambiente ativo (você verá "(venv)" no início da linha)
pip install -r requirements.txt
```

### Iniciar aplicação:

```powershell
# Com ambiente ativo
uvicorn api:app --reload --port 8000
```

### Desativar ambiente virtual:

```powershell
deactivate
```

---

## 📝 Script Completo de Instalação (Copie e Cole)

Salve isso como `instalar.ps1` e execute:

```powershell
# Verifica Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
py --version

# Cria ambiente virtual
Write-Host "`nCriando ambiente virtual..." -ForegroundColor Yellow
py -m venv venv

# Ativa ambiente virtual
Write-Host "`nAtivando ambiente virtual..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Atualiza pip
Write-Host "`nAtualizando pip..." -ForegroundColor Yellow
py -m pip install --upgrade pip

# Instala dependências
Write-Host "`nInstalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt

# Confirma instalação
Write-Host "`nInstalação concluída!" -ForegroundColor Green
Write-Host "Para iniciar a aplicação, execute:" -ForegroundColor Cyan
Write-Host "uvicorn api:app --reload --port 8000" -ForegroundColor White
```

**Para executar:**
```powershell
.\instalar.ps1
```

---

## 🎯 Método Mais Simples (SEM Instalar Nada Local)

Se está com muita dificuldade, use o **deploy online**:

### Opção 1: Railway (Mais Fácil)

1. Acesse: https://railway.app
2. Faça login com GitHub
3. "New Project" → "Deploy from GitHub"
4. Selecione o repositório `cnpjscrapping`
5. Aguarde 2 minutos
6. Acesse a URL gerada + `/web`

**Pronto! Funciona no navegador, sem instalar nada!** 🎉

### Opção 2: Render (100% Grátis)

1. Acesse: https://render.com
2. Login com GitHub
3. "New +" → "Web Service"
4. Conecte o repositório
5. Aguarde o deploy
6. Acesse a URL + `/web`

---

## 💡 Resumo Rápido

**Para instalar e rodar LOCAL no Windows:**

```powershell
# 1. Navegue até o projeto
cd caminho\para\cnpjscrapping

# 2. Instale dependências (teste estes na ordem):
pip install -r requirements.txt
# OU
py -m pip install -r requirements.txt
# OU
python -m pip install -r requirements.txt

# 3. Inicie a aplicação (teste estes na ordem):
uvicorn api:app --reload --port 8000
# OU
py -m uvicorn api:app --reload --port 8000
# OU
python api.py
# OU
py api.py

# 4. Acesse no navegador:
http://localhost:8000/web
```

---

## 🆘 Ainda com Problemas?

**Envie print da tela com:**

```powershell
# Execute estes comandos e copie o resultado:
python --version
py --version
where python
where py
pip --version
py -m pip --version
```

---

## ✅ Checklist de Sucesso

- [ ] Python instalado
- [ ] `python --version` ou `py --version` funciona
- [ ] Dependências instaladas (sem erros)
- [ ] API iniciada (vê mensagem no terminal)
- [ ] Navegador abre em `http://localhost:8000/web`
- [ ] Interface web carrega
- [ ] Consegue fazer busca de telefones

---

**Tente os comandos acima e me diga qual funcionou!** 🚀

**Ou se preferir simplicidade, faça o deploy no Railway (2 minutos, sem instalar nada local)!** ⚡
