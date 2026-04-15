# 📑 Índice de Documentação

Guia de navegação completo para o Pipeline B2B Autônomo.

## 🚀 Comece por aqui

1. **[RESUMO_EXECUTIVO.md](./RESUMO_EXECUTIVO.md)** ← LEIA ISSO PRIMEIRO
   - O que foi construído
   - Comparação com AutoGTM
   - Arquitetura geral
   - Checklist de implementação

## 📚 Documentação Principal

### Para Desenvolvedores
- **[README.md](./README.md)** - Documentação técnica completa
  - Arquitetura detalhada
  - Schema do banco de dados
  - Como usar cada microsserviço
  - Exemplos de código

- **[ARQUITETURA.md](./ARQUITETURA.md)** - Design técnico
  - Fluxo de dados completo
  - Stack tecnológico
  - Roadmap de implementação
  - Estratégia de custos

- **[REFERENCIA_DADOS.md](./REFERENCIA_DADOS.md)** - Dados & Schemas
  - Modelos de dados
  - Enums e tipos
  - Schema SQL
  - Conversões JSON
  - Exemplos de dados

### Para Usar/Executar
- **[QUICK_START.md](./QUICK_START.md)** - Guia prático
  - Setup em 3 passos
  - Exemplos de código
  - Configuração .env
  - Troubleshooting
  - Performance

- **[services/lead_extractor/PRODUCT_MATCHER.md](./services/lead_extractor/PRODUCT_MATCHER.md)** - Classificador de Produtos
  - Como mapear leads a produtos
  - Algoritmo de matching
  - Integração no pipeline
  - Exemplos de uso
  - Modo LLM (opcional)

- **[INTEGRACAO_AIDA_EMAIL.md](./INTEGRACAO_AIDA_EMAIL.md)** - Email Generator com AIDA Framework
  - Integração Product Matcher + Email Generator
  - Framework AIDA (Atenção, Interesse, Desejo, Ação)
  - Como gerar emails personalizados por produto
  - Exemplos de uso com batch processing
  - Configuração com/sem IA (GPT-4)

- **[SMTP_DISPATCHER.md](./SMTP_DISPATCHER.md)** - Roteamento Dinâmico de Remetentes
  - Disparo de emails com roueteamento por produto
  - Integração Zoho Mail SMTP
  - Roteamento automático: Produto → Alias de Email
  - Type-safe e structured logging
  - Auditoria completa

- **[AIDA_QUICK_REFERENCE.md](./AIDA_QUICK_REFERENCE.md)** - Quick Ref: AIDA + Product Match
  - Setup em 3 linhas
  - Cheat sheet rápido
  - Troubleshooting
  - Checklist de uso

- **[SMTP_QUICK_REFERENCE.md](./SMTP_QUICK_REFERENCE.md)** - Quick Ref: SMTP Dispatcher
  - Setup em 3 passos
  - Roteamento Produto → Email
  - Integração completa
  - Batch processing

## 🗂️ Estrutura do Projeto

```
hunterteck/
├── 📖 DOCUMENTAÇÃO
│   ├── README.md                 ← Técnico & Conceitual
│   ├── RESUMO_EXECUTIVO.md       ← Visão geral & ROI
│   ├── ARQUITETURA.md            ← Design & Roadmap
│   ├── QUICK_START.md            ← Prático & Uso
│   ├── REFERENCIA_DADOS.md       ← Schemas & Tipos
│   └── INDEX.md                  ← Este arquivo
│
├── 💻 CÓDIGO - Orquestrador
│   ├── orquestrador.py           ← Pipeline completo (MS1-MS7 coordenados)
│   └── exemplos.py               ← Exemplos interativos
│
└── 🔧 CÓDIGO - Microsserviços
    └── services/lead_extractor/
        ├── main.py               ← MS1: Lead Extractor (Orquestração básica)
        ├── database.py           ← Camada de persistência SQLite
        ├── models.py             ← Dataclasses (Empresa, Pessoa, etc)
        ├── config.py             ← Configuração centralizada
        ├── extractors.py         ← MS1: Strategies (Google Maps, Web Scrape)
        ├── validator.py          ← MS2: Data Validator
        ├── enricher.py           ← MS3: Data Enricher
        ├── person_finder.py      ← MS4: Person Finder
        ├── email_generator.py    ← MS6: Email Generator
        ├── product_matcher.py    ← MS: Product Matcher (Classificador de Produtos)
        ├── __init__.py           ← Package exports
        ├── PRODUCT_MATCHER.md    ← Documentação do Product Matcher
        └── requirements.txt      ← Dependências Python

```

## 🎯 Por Caso de Uso

### Quero entender o projeto rapidamente
1. [RESUMO_EXECUTIVO.md](./RESUMO_EXECUTIVO.md) (5 min)
2. [ARQUITETURA.md](./ARQUITETURA.md) (10 min)
3. [README.md](./README.md) (15 min)

### Quero instalar e rodar
1. [QUICK_START.md](./QUICK_START.md) (5 min)
2. Executar: `python orquestrador.py`

### Quero entender o código
1. [README.md](./README.md) - Fluxo de dados
2. [REFERENCIA_DADOS.md](./REFERENCIA_DADOS.md) - Modelos
3. Examinar: `services/lead_extractor/models.py`

### Quero customizar/estender
1. [ARQUITETURA.md](./ARQUITETURA.md) - Design
2. [REFERENCIA_DADOS.md](./REFERENCIA_DADOS.md) - APIs
3. Editar os arquivos em `services/lead_extractor/`

### Quero integrar com meu sistema
1. [QUICK_START.md](./QUICK_START.md) - Exemplos programáticos
2. `from orquestrador import PipelineAutonomoB2B`

## 📊 Resumo de Cada Documento

### RESUMO_EXECUTIVO.md
```
✅ Checklist do que foi entregue
✅ Comparação AutoGTM vs Nossa solução
✅ Stack tecnológico
✅ Arquitetura visual
✅ Métricas & Performance
✅ Roadmap futuro
📄 1,500+ linhas | Leitura: 10 min
```

### README.md
```
✅ Documentação técnica completa
✅ Schema do banco (SQL)
✅ Como usar cada microsserviço
✅ Exemplos de código
✅ Tratamento de erros
✅ Boas práticas
📄 2,000+ linhas | Leitura: 20 min
```

### ARQUITETURA.md
```
✅ Design completo do pipeline
✅ Fluxo de dados (7 microsserviços)
✅ Stack tecnológico
✅ Roadmap de implementação (3 fases)
✅ Estimativa de custos
✅ Conceitos avançados
📄 400+ linhas | Leitura: 15 min
```

### QUICK_START.md
```
✅ Setup em 3 passos
✅ Exemplos de código (copy-paste)
✅ Variáveis de ambiente
✅ Troubleshooting
✅ Dicas de performance
✅ Advanced examples
📄 300+ linhas | Leitura: 10 min
```

### REFERENCIA_DADOS.md
```
✅ Modelos de dados (dataclasses)
✅ Enums (LeadSource, LeadStatus, TipoEmail)
✅ Schema SQL (5 tabelas)
✅ Conversões JSON/SQL
✅ Agregações & Queries
✅ Scores & Métricas
📄 600+ linhas | Referência
```

## 🔍 Arquivo → Microsserviço

| Arquivo | Microsserviço | O Que Faz |
|---------|---------------|----------|
| main.py | MS1 | Extrai leads de APIs e web scraping |
| database.py | Comum | Camada de persistência SQLite |
| validator.py | MS2 | Valida, deduplica, score qualidade |
| enricher.py | MS3 | Enriquece com receita, funcionários, etc |
| person_finder.py | MS4 | Localiza decisores e gera emails |
| email_generator.py | MS6 | Gera emails (template ou IA) |
| orquestrador.py | MS5 | Coordena MS1-MS7 automaticamente |
| exemplos.py | Demo | Exemplos interativos |

## 💡 Quick Commands

```bash
# Instalar
pip install -r services/lead_extractor/requirements.txt

# Rodar pipeline completo
python orquestrador.py

# Rodar exemplos interativos
python exemplos.py

# Rodar um microsserviço específico
python -m services.lead_extractor.validator

# Verificar logs
tail -f logs/lead_extractor_*.log

# Consultar banco de dados
sqlite3 data/leads.db
> SELECT COUNT(*) FROM empresas;
> SELECT * FROM empresas LIMIT 5;
```

## 🎓 Aprendizado Recomendado

### Iniciante (0-1h)
1. RESUMO_EXECUTIVO.md (10 min)
2. QUICK_START.md (20 min)
3. Rodar `python orquestrador.py` (10 min)
4. Explorar `data/leads.db` (10 min)

### Intermediário (1-3h)
1. README.md completo (30 min)
2. REFERENCIA_DADOS.md (20 min)
3. Examinar `services/lead_extractor/models.py` (20 min)
4. Examinar `services/lead_extractor/main.py` (30 min)
5. Customizar um email template (30 min)

### Avançado (3-8h)
1. ARQUITETURA.md completo (30 min)
2. Examinar todo código Python (2h)
3. Implementar MS5 (ICP Generator) (2h)
4. Implementar MS7 (Outreach Scheduler) (2h)
5. Deploy em produção (1h)

## 📊 Estatísticas do Projeto

```
📝 CÓDIGO PYTHON
  - Microsserviços:     2,690 linhas
  - Orquestrador+Demo:    710 linhas
  - Total:             3,400 linhas

📖 DOCUMENTAÇÃO
  - README:             2,000 linhas
  - ARQUITETURA:          400 linhas
  - QUICK_START:          300 linhas
  - REFERENCIA:           600 linhas
  - RESUMO:            1,500 linhas
  - Total:             4,800 linhas

⏱️ TEMPO TOTAL
  - Código:           30-40h
  - Documentação:     10-15h
  - Total:           40-55h

💾 TAMANHO DO REPOSITÓRIO
  - Código:            ~150 KB
  - Documentação:      ~50 KB
  - Total:            ~200 KB
```

## ✅ Checklist de Leitura

Após ler o README, você deve entender:

- [ ] O que é o pipeline e como funciona
- [ ] Qual é o objetivo geral (competir com AutoGTM)
- [ ] Os 5+ microsserviços implementados
- [ ] Como extrair, validar, enriquecer e gerar emails
- [ ] Como persistir dados no SQLite
- [ ] Como executar o orquestrador
- [ ] Próximas fases de desenvolvimento

## 🔗 Links Importantes

### Dentro do Projeto
- [Código principal](./services/lead_extractor/)
- [Base de dados](./data/)
- [Logs](./logs/)
- [.env template](./.env.example)

### Fora do Projeto
- [AutoGTM Explee](https://explee.com/auto-gtm)
- [Google Maps API](https://developers.google.com/maps)
- [OpenAI GPT-4](https://openai.com/api/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [SQLite](https://www.sqlite.org/)

## 🎯 Próximos Passos

1. **Ler**: RESUMO_EXECUTIVO.md (entender o projeto)
2. **Instalar**: `pip install -r services/lead_extractor/requirements.txt`
3. **Executar**: `python orquestrador.py`
4. **Explorar**: Examinar `data/leads.db`
5. **Customizar**: Modificar templates em `email_generator.py`
6. **Integrar**: Usar `PipelineAutonomoB2B` em seu código

---

**Desenvolvido por:** Arquiteto de Soluções  
**Data:** Abril 2024  
**Status:** Production Ready ✅  
**Licença:** Propriétade de SDR Agent

**Precisa de ajuda?** Verifique [QUICK_START.md](./QUICK_START.md) → Seção Troubleshooting
