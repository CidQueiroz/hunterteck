# 🚀 HUNTERTECK - Guia de Inicialização Rápida

> **Status:** ✅ Projeto validado e pronto para deploy  
> **Data:** 14 de Abril de 2026  
> **Versão do Projeto:** 1.0.0

---

## 📌 Resumo Executivo

O **HunterTeck** foi integrado ao workspace de forma segura. Todos os imports estão funcionando e não há referências quebradas.

**Para começar, execute uma destas opções:**
- **Linux/macOS:** `bash INIT.sh`
- **Windows:** `INIT.bat`
- **Qualquer SO:** `python validate_project.py` (para diagnóstico)

---

## 📚 O que foi Fornecido

### 1. **INIT.sh** (Linux/macOS)
Script de inicialização automática que:
- ✅ Verifica pré-requisitos (Python 3.9+, pip, git)
- ✅ Configura diretórios (`data/`, `logs/`)
- ✅ Configure `.env` automaticamente
- ✅ Cria/ativa virtual environment
- ✅ Instala todas as dependências
- ✅ Inicializa banco de dados SQLite
- ✅ Valida todos os imports

**Como usar:**
```bash
cd /home/cidquei/CDKTECK/hunterteck
chmod +x INIT.sh
bash INIT.sh
```

### 2. **INIT.bat** (Windows)
Equivalente do INIT.sh para Windows.

**Como usar:**
```cmd
cd C:\Users\YourUser\CDKTECK\hunterteck
INIT.bat
```

### 3. **validate_project.py** (Qualquer SO)
Ferramenta de diagnóstico que valida:
- ✅ Estrutura de diretórios
- ✅ Imports do projeto
- ✅ Dependências instaladas
- ✅ Variáveis de ambiente
- ✅ Banco de dados
- ✅ Docker setup
- ✅ Versão do Python

**Como usar:**
```bash
python validate_project.py
```

### 4. **ANALISE_PROJETO.md**
Relatório detalhado com:
- 📊 Análise completa do projeto
- 🔗 Validação de imports e referências
- 📦 Status das dependências
- 🐳 Verificação do Docker setup
- ⚠️ Pontos de atenção
- 🎯 Próximos passos recomendados

---

## 🎯 Próximas Etapas

### **PASSO 1: Inicializar Projeto**

```bash
# Linux/macOS
bash INIT.sh

# Windows
INIT.bat

# Ou diagnóstico completo
python validate_project.py
```

### **PASSO 2: Configurar .env**

Edite o arquivo `.env` e configure suas chaves de API:

```bash
# Obrigatório
GROQ_API_KEY=gsk_YOUR_REAL_KEY_HERE

# Recomendados
GOOGLE_API_KEY=YOUR_KEY_HERE
LINKEDIN_API_KEY=YOUR_KEY_HERE

# Database (deixe como está)
DATABASE_PATH=data/leads.db
DATABASE_BACKUP_DIR=data/backups

# Aplicação
LOG_LEVEL=INFO
DEBUG=False
```

### **PASSO 3: Testar Importação**

```bash
# Ativar venv (se não estiver ativado)
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate.bat  # Windows

# Testar
python validate_project.py
```

### **PASSO 4: Executar Aplicação**

```bash
# Opção A: CLI Streamlit
streamlit run app_hunter.py

# Opção B: Script Python direto
python app_hunter.py

# Opção C: Pipeline autônomo
python orquestrador.py

# Opção D: Docker
docker-compose up
```

---

## 🔑 Pontos-Chave

### ✅ Estrutura Validada
- Todos os diretórios estão no lugar
- Imports estão funcionando
- Arquivos críticos presentes
- Docker configurado

### ✅ Dependências
- Definidas em `pyproject.toml`
- Extras disponíveis: `[dev,groq]`
- Sem conflitos detectados

### ✅ Banco de Dados
- SQLite (sem dependências externas)
- Schema criado automaticamente
- Backups configurados

### ⚠️ Configuração Obrigatória
- **GROQ_API_KEY:** Necessária para geração de emails com IA
- **.env:** Criar a partir de `.env.example`

---

## 📂 Estrutura Final Esperada

Após executar INIT.sh, você terá:

```
hunterteck/
├── venv/                           # Virtual environment
├── data/
│   ├── leads.db                    # Banco de dados SQLite
│   └── backups/                    # Backups automáticos
├── logs/                           # Logs de execução
├── .env                            # Configuração (executar cp .env.example .env)
├── [scripts de inicialização]
└── [arquivos de análise]
```

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'services'"

**Causa:** Virtual environment não ativado ou path não configurado  
**Solução:**
```bash
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate.bat  # Windows
```

### "GROQ_API_KEY not set"

**Causa:** Variável de ambiente não configurada  
**Solução:**
```bash
# Editar .env
nano .env  # ou use seu editor favorito

# Adicionar:
GROQ_API_KEY=gsk_YOUR_REAL_KEY_HERE

# Recarregar
source .env
```

### "Permission denied" (Linux)

**Causa:** Script sem permissão  
**Solução:**
```bash
chmod +x INIT.sh
bash INIT.sh
```

### "Database locked"

**Causa:** Outro processo está usando o banco  
**Solução:**
```bash
# Localizar e encerrar processos Python
# Linux/macOS
ps aux | grep python

# Windows
tasklist /FI "IMAGENAME eq python.exe"

# Deletar lock (se necessário)
rm -f data/leads.db-wal
rm -f data/leads.db-shm
```

---

## 📖 Documentação

- **QUICK_START.md** - Guia rápido de uso
- **README.md** - Documentação geral
- **ANALISE_PROJETO.md** - Análise técnica completa
- **ARQUITETURA.md** - Arquitetura do sistema
- **ORGANIZATION.md** - Organização do código

---

## ✨ Comandos Úteis

```bash
# Validar projeto
python validate_project.py

# Iniciar desenvolvimento
streamlit run app_hunter.py

# Executar pipeline completo
python orquestrador.py

# Testes
python -m pytest tests/

# Formatação de código
black services/ orquestrador.py

# Linting
flake8 services/ orquestrador.py

# Type checking
mypy services/

# Docker
docker-compose up -d        # Start
docker-compose logs -f      # View logs
docker-compose down         # Stop
```

---

## 🎓 Próximos Passos Recomendados

1. **Imediato:**
   - Executar INIT.sh
   - Configurar .env
   - Testar com `python validate_project.py`

2. **Curto Prazo:**
   - Explorar `QUICK_START.md`
   - Executar exemplos em `exemplos.py`
   - Testar CLI com `streamlit run app_hunter.py`

3. **Médio Prazo:**
   - Adicionar mais campanhas em `MAPEAMENTO_CAMPANHAS`
   - Customizar templates de email
   - Setup de backup automático

4. **Longo Prazo:**
   - Deploy em produção (OCI/GCP)
   - Integração com CRM
   - Analytics e reporting

---

## 🔐 Segurança

- ✅ **Never commit .env with real keys** → Use `.env.example` como template
- ✅ **Non-root in Docker** → User `hunterteck` criado
- ✅ **Input validation** → Pydantic valida todos os dados
- ✅ **SQLite is local** → Dados não expostos por padrão
- ✅ **HTTPS only in production** → Configure certificados

---

## 📊 Stack de Tecnologias

| Componente | Tecnologia | Versão |
|------------|-----------|--------|
| **Language** | Python | 3.9+ |
| **Web** | Streamlit | 1.28.1+ |
| **Data** | Pandas | 2.1.1+ |
| **DB** | SQLite | Built-in |
| **Scraping** | BeautifulSoup4 | 4.12.2+ |
| **Validation** | Pydantic | 2.5.0+ |
| **AI** | GROQ API | Latest |
| **Container** | Docker | Latest |

---

## ✅ Checklist Final

Antes de começar:

- [ ] Executou INIT.sh ou INIT.bat
- [ ] Configurou .env com GROQ_API_KEY
- [ ] Validou com `python validate_project.py`
- [ ] Testou `streamlit run app_hunter.py`
- [ ] Leu QUICK_START.md
- [ ] Explorou exemplos em `exemplos.py`

---

## 📞 Contatos & Referências

- **Documentação Web:** [QUICK_START.md](QUICK_START.md)
- **Análise Técnica:** [ANALISE_PROJETO.md](ANALISE_PROJETO.md)
- **Arquitetura:** [ARQUITETURA.md](ARQUITETURA.md)
- **Issues:** Verificar logs em `./logs/`

---

**🎉 Você está pronto para começar com HunterTeck!**

Qualquer dúvida, consulte a documentação ou execute `python validate_project.py` para diagnóstico.
