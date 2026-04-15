# Pipeline B2B Autônomo - Microsserviço de Extração de Leads

Solução enterprise de prospecção B2B com extração automática de leads, coleta de dados corporativos e persistência em banco de dados SQLite.

## 🏗️ Arquitetura

```
lead-extraction-pipeline/
├── services/
│   └── lead_extractor/          # Microsserviço 1: Extrator de Leads
│       ├── models.py            # Modelos de dados (Empresa, LeadStatus, etc)
│       ├── database.py          # Camada de persistência SQLite
│       ├── extractors.py        # Estratégias de extração (Google Maps, Web Scraping, APIs)
│       ├── config.py            # Configurações centralizadas
│       ├── main.py              # Orquestração do pipeline
│       ├── __init__.py          # Exports do pacote
│       └── requirements.txt     # Dependências Python
├── data/                        # Armazenamento de resultados
│   ├── leads.db                 # Banco SQLite com dados coletados
│   └── backups/                 # Backups do banco
├── logs/                        # Logs de execução
├── .gitignore                   # Arquivos ignorados no git
└── README.md                    # Este arquivo
```

## ✨ Características Principais

### 1. **Tipagem Estática Completa**
- Type hints em todos os módulos
- Validação de tipos em tempo de desenvolvimento
- Compatível com mypy e ferramentas de análise estática

### 2. **Tratamento Robusto de Erros**
- Classes de exceção customizadas (`ExtratorError`, `DatabaseError`)
- Retry automático em falhas de rede
- Logging estruturado em múltiplos níveis

### 3. **Múltiplas Estratégias de Extração**
- **Google Maps API**: Consulta dados de empresas locais
- **Web Scraping**: Extração via CSS selectors com BeautifulSoup
- **APIs Customizadas**: Integração com qualquer API HTTP
- **Demo Mode**: API simulada para testes

### 4. **Persistência em SQLite**
- Schema normalizado com índices otimizados
- Histórico de alterações
- Estatísticas agregadas
- Transações ACID garantidas

### 5. **Configuração Centralizada**
- Suporte a variáveis de ambiente
- Configuração por arquivo ou programaticamente
- Padrões sensatos como defaults

### 6. **Monitoramento e Logging**
- Logs estruturados em arquivo + console
- Diferentes níveis: DEBUG, INFO, WARNING, ERROR
- Rastreamento de execução completo

## 🚀 Inicialização Rápida

### 1. Instalar Dependências

```bash
cd /home/cidquei/Projetos/hunterteck/services/lead_extractor
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente (Opcional)

```bash
# .env
DEBUG=true
LOG_LEVEL=DEBUG
REQUEST_TIMEOUT=30
MAX_RETRIES=3
GOOGLE_API_KEY=sua_chave_aqui
```

### 3. Executar o Pipeline

```bash
python main.py
```

## 📊 Modelos de Dados

### Empresa
Representa uma empresa/lead coletado:

```python
@dataclass
class Empresa:
    nome: str                          # Nome da empresa
    website: str                       # URL do site
    email: Optional[str]               # Email de contato
    telefone: Optional[str]            # Telefone
    endereco: str                      # Endereço completo
    cidade: str                        # Município
    estado: str                        # Estado/Região
    ramo: str                          # Setor/Indústria
    fonte: LeadSource                  # Origem (Google Maps, Web Scrape, etc)
    status: LeadStatus                 # Estado do lead (novo, qualificado, etc)
    data_coleta: datetime              # Quando foi coletado
    ultima_atualizacao: datetime       # Última atualização
```

### LeadSource (Enum)
Fontes de coleta disponíveis:
- `GOOGLE_MAPS`: Google Maps API
- `YELLOWPAGES`: Yellow Pages / Diretórios locais
- `LINKEDIN`: LinkedIn Business
- `WEB_SCRAPE`: Web scraping customizado
- `API`: APIs de terceiros

### LeadStatus (Enum)
Estados possíveis de um lead:
- `NOVO`: Coletado recentemente
- `QUALIFICADO`: Validado como prospect válido
- `EMAIL_VALIDADO`: Email verificado
- `CONTATO_REALIZADO`: Contato estabelecido
- `DESCARTADO`: Lead inválido/não-qualificado

## 🔧 Uso Programático

### Exemplo 1: Extração com Google Maps

```python
from main import PipelineExtracao

pipeline = PipelineExtracao()

# Extrair leads
empresas = pipeline.extrair_com_google_maps(
    query="restaurantes em",
    cidade="São Paulo",
    estado="SP",
    limite=50
)

# Persistir no banco
resultado = pipeline.persistir_leads(empresas)
print(f"Inseridas {resultado['sucesso']}/{resultado['total']} empresas")
```

### Exemplo 2: Web Scraping Customizado

```python
seletores = {
    'elemento': '.negocio-item',      # Container de cada empresa
    'nome': '.nome-empresa',           # Nome da empresa
    'website': 'a.website',            # Link do site
    'email': '.email',                 # Email
    'telefone': '.telefone',           # Telefone
    'endereco': '.endereco'            # Endereço
}

empresas = pipeline.extrair_com_web_scraping(
    url_base="https://exemplo.com/empresas",
    ramo="Varejo",
    cidade="Rio de Janeiro",
    estado="RJ",
    seletores=seletores
)

pipeline.persistir_leads(empresas)
```

### Exemplo 3: Consultar Dados

```python
# Obter estatísticas
stats = pipeline.obter_estatisticas()
print(f"Total de empresas: {stats['total_empresas']}")
print(f"Por status: {stats['por_status']}")
print(f"Cidades com mais leads: {stats['por_cidade']}")

# Listar leads recentes
leads = pipeline.listar_leads_recentes(limite=50)
for lead in leads:
    print(f"{lead['nome']} | {lead['cidade']}")
```

## 🗄️ Schema do Banco de Dados

### Tabela: empresas
```sql
CREATE TABLE empresas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    website TEXT NOT NULL UNIQUE,
    email TEXT,
    telefone TEXT,
    endereco TEXT NOT NULL,
    cidade TEXT NOT NULL,
    estado TEXT NOT NULL,
    ramo TEXT NOT NULL,
    fonte TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'novo',
    data_coleta DATETIME NOT NULL,
    ultima_atualizacao DATETIME NOT NULL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_empresas_cidade ON empresas(cidade);
CREATE INDEX idx_empresas_ramo ON empresas(ramo);
CREATE INDEX idx_empresas_status ON empresas(status);
```

### Tabela: historico_alteracoes
```sql
CREATE TABLE historico_alteracoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    campo TEXT NOT NULL,
    valor_anterior TEXT,
    valor_novo TEXT,
    data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas (id) ON DELETE CASCADE
);
```

## 📝 Tratamento de Erros

O microsserviço implementa tratamento robusto em múltiplas camadas:

### 1. Validação de Dados
```python
try:
    empresa = Empresa(nome="", website="http://exemplo.com")
except ValueError as e:
    print(f"Erro de validação: {e}")
    # ValueError: Nome da empresa deve ser uma string não vazia
```

### 2. Erros de Rede
- Retry automático com backoff exponencial
- Tratamento de timeout, conexão recusada, rate limit
- Logging detalhado de cada tentativa

### 3. Erros de Banco de Dados
- Transações atômicas (ACID)
- Rollback automático em falha
- Tratamento de duplicatas

```python
try:
    resultado = pipeline.persistir_leads(empresas)
except DatabaseError as e:
    print(f"Erro de persistência: {e}")
```

## 🔒 Segurança e Boas Práticas

- ✅ Validação de entrada em todos os endpoints
- ✅ Prepared statements para prevenir SQL injection
- ✅ Tratamento seguro de credenciais via variáveis de ambiente
- ✅ Logging sem expor dados sensíveis
- ✅ Tipagem estática para detectar bugs em compile-time
- ✅ Context managers para garantir limpeza de recursos

## 📊 Monitoramento

### Logs
```
2024-04-13 10:30:45,123 - __main__ - INFO - Pipeline de extração inicializado
2024-04-13 10:30:46,456 - extractors - INFO - Iniciando extração Google Maps
2024-04-13 10:30:48,789 - database - INFO - Inserção em lote: 15/15 empresas inseridas
```

### Estatísticas
```json
{
    "total_empresas": 45,
    "por_status": {
        "novo": 30,
        "qualificado": 10,
        "email_validado": 5
    },
    "por_cidade": {
        "São Paulo": 25,
        "Rio de Janeiro": 15,
        "Belo Horizonte": 5
    },
    "por_ramo": {
        "restaurantes": 20,
        "lojas": 15,
        "consultoria": 10
    }
}
```

## 🚦 Microsserviços Implementados

Este é o **Pipeline B2B Completo** com vários microsserviços integrados:

### ✅ Implementados (Production Ready)

- **MS1**: Lead Extractor - Extração automática de leads (Google Maps, Web Scraping)
- **MS2**: Data Validator - Validação de email, telefone, dados estruturados
- **MS3**: Data Enricher - Enriquecimento com dados de social media, receita
- **MS4**: Person Finder - Identificação de decisores via LinkedIn patterns
- **MS6**: Email Generator - Geração de cold emails com templates ou IA (GPT-4)
  - ✨ **NOW**: Integração com Product Matcher + AIDA Framework
  - 📗 Documentação: [INTEGRACAO_AIDA_EMAIL.md](./INTEGRACAO_AIDA_EMAIL.md)
  - ⚡ Quick ref: [AIDA_QUICK_REFERENCE.md](./AIDA_QUICK_REFERENCE.md)

- **SMTP Dispatcher** - Roteamento dinâmico de remetentes por produto 🆕
  - Cada produto tem seu alias de email (SenseiDB, GestaoRPD, etc)
  - Integração Zoho Mail SMTP
  - Type-safe com structured logging
  - 📗 Documentação: [SMTP_DISPATCHER.md](./SMTP_DISPATCHER.md)
  - ⚡ Quick ref: [SMTP_QUICK_REFERENCE.md](./SMTP_QUICK_REFERENCE.md)

- **Product Matcher**: Classificação automática de leads para 5 produtos CDKTeck
  - 📗 Documentação: [PRODUCT_MATCHER.md](./services/lead_extractor/PRODUCT_MATCHER.md)
  - 170+ palavras-chave, 25+ nichos, score 0-100

### 📋 Planejado

- **MS5**: ICP Generator - Geração de perfil ideal de cliente
- **MS7**: Outreach Orchestrator - Agendamento e envio de emails em escala
- **MS8**: Analytics Dashboard - Métricas de performance, open rate, click rate

## 📚 Documentação Principal

- **[RESUMO_EXECUTIVO.md](./RESUMO_EXECUTIVO.md)** - Visão geral do projeto
- **[ARQUITETURA.md](./ARQUITETURA.md)** - Design técnico e roadmap
- **[QUICK_START.md](./QUICK_START.md)** - Como começar
- **[REFERENCIA_DADOS.md](./REFERENCIA_DADOS.md)** - Modelos e schemas
- **[INTEGRACAO_AIDA_EMAIL.md](./INTEGRACAO_AIDA_EMAIL.md)** - Email com AIDA (NOVO!)
- **[AIDA_QUICK_REFERENCE.md](./AIDA_QUICK_REFERENCE.md)** - Cheat sheet (NOVO!)
- **[SMTP_DISPATCHER.md](./SMTP_DISPATCHER.md)** - Roteamento SMTP (NOVO!)
- **[SMTP_QUICK_REFERENCE.md](./SMTP_QUICK_REFERENCE.md)** - Cheat sheet SMTP (NOVO!)
- **[INDEX.md](./INDEX.md)** - Índice de toda documentação

## 📄 Licença

Projeto propriedário de SDR Agent.

## 👨‍💼 Suporte

Para problemas ou dúvidas, consulte a documentação ou entre em contato com a equipe de desenvolvimento.

---

**Versão**: 2.1.0 (com AIDA + Product Match + SMTP Dispatcher)  
**Última Atualização**: Hoje  
**Status**: Production Ready ✅
