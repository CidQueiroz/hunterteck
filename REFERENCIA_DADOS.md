# 📊 Referência de Dados e Schemas

Documentação completa de todas as estruturas de dados, enums e schemas do pipeline.

## 🗂️ Modelos Principais

### 1. Empresa (LeadSource)

```python
@dataclass
class Empresa:
    nome: str                          # Nome da empresa
    website: str                       # URL do website
    email: Optional[str]               # Email de contato
    telefone: Optional[str]            # Telefone
    endereco: str                      # Endereço completo
    cidade: str                        # Município
    estado: str                        # Estado/UF
    ramo: str                          # Setor/Indústria
    fonte: LeadSource                  # Origem (GOOGLE_MAPS, WEB_SCRAPE, etc)
    status: LeadStatus                 # Estado (NOVO, QUALIFICADO, etc)
    data_coleta: datetime              # Quando foi coletado
    ultima_atualizacao: datetime       # Última modificação
```

**Enums:**
```python
class LeadSource(str, Enum):
    GOOGLE_MAPS = "google_maps"
    YELLOWPAGES = "yellowpages"
    LINKEDIN = "linkedin"
    WEB_SCRAPE = "web_scrape"
    API = "api"

class LeadStatus(str, Enum):
    NOVO = "novo"
    QUALIFICADO = "qualificado"
    EMAIL_VALIDADO = "email_validado"
    CONTATO_REALIZADO = "contato_realizado"
    DESCARTADO = "descartado"
```

### 2. DadosEnriquecidos

```python
@dataclass
class DadosEnriquecidos:
    empresa_id: int                    # FK para tabela empresas
    dominio_website: str               # Domínio extraído
    receita_anual: Optional[str]       # "1M", "10M", "100M", "1B"
    num_funcionarios: Optional[str]    # "1-10", "50-100", "500-1000"
    ano_fundacao: Optional[int]        # 1995, 2010, etc
    setor_industria: Optional[str]     # "Technology", "Healthcare"
    linkedin_url: Optional[str]        # URL do LinkedIn da empresa
    facebook_url: Optional[str]        # URL do Facebook
    twitter_url: Optional[str]         # URL do Twitter
    instagram_url: Optional[str]       # URL do Instagram
    descricao: Optional[str]           # Descrição/Bio
    tags: List[str]                    # ["tech", "startup", "seed"]
    data_enriquecimento: datetime      # Quando foi enriquecido
    fonte_dados: str                   # "clearbit", "apollo", "hunter", "manual"
```

### 3. Pessoa

```python
@dataclass
class Pessoa:
    nome: str                          # Nome completo
    cargo: str                         # Título do cargo
    empresa_nome: str                  # Nome da empresa
    email: Optional[str]               # Email corporativo
    telefone: Optional[str]            # Telefone
    linkedin_url: Optional[str]        # URL do LinkedIn
    titulo: str                        # "C-Level", "Executive", "Senior", "Active"
    nivel_hierarquia: int              # 0=C-level, 1=Exec, 2=Senior, 3=Active
    confianca_email: float             # 0.0-1.0 (confidence score)
    fonte: str                         # "linkedin", "clearbit", "hunter", "manual"
    data_descoberta: datetime          # Quando foi encontrado
```

### 4. EmailGerado

```python
@dataclass
class EmailGerado:
    destinatario_email: str            # Email do recipient
    destinatario_nome: str             # Nome do recipient
    assunto: str                       # Subject line
    corpo: str                         # Email body
    tipo: TipoEmail                    # PRIMEIRO_CONTATO, SEGUIMENTO_1, etc
    contexto: Dict[str, Any]           # Variáveis usadas
    gerado_por: str                    # "template" ou "openai"
    data_geracao: datetime             # Quando foi gerado
    versao_ab: Optional[str]           # "A", "B", ou None

class TipoEmail(str, Enum):
    PRIMEIRO_CONTATO = "primeiro_contato"
    SEGUIMENTO_1 = "seguimento_1"
    SEGUIMENTO_2 = "seguimento_2"
    SEGUIMENTO_3 = "seguimento_3"
    REENGAJAMENTO = "reengajamento"
```

### 5. ContextoEmail

```python
@dataclass
class ContextoEmail:
    nome_pessoa: str                   # Nome do decision maker
    cargo_pessoa: str                  # Sua posição
    empresa_nome: str                  # Nome da empresa alvo
    setor_empresa: str                 # Indústria
    tamanho_empresa: Optional[str]     # "1-10", "50-100", etc
    receita_empresa: Optional[str]     # "1M", "10M", etc
    website_empresa: str               # URL da empresa
    linkedin_url: Optional[str]        # LinkedIn profile
    pain_points: List[str]             # Problemas identificados
    valor_proposto: str                # Proposição de valor
    tipo_email: TipoEmail              # Tipo de email
    empresa_vendedora_nome: str        # Sua empresa
    vendedor_nome: str                 # Seu nome
    vendedor_email: str                # Seu email
    cta_url: Optional[str]             # Call-to-action URL
```

## 🗄️ Schema do Banco de Dados

### Tabela: empresas

```sql
CREATE TABLE IF NOT EXISTS empresas (
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

-- Índices
CREATE INDEX idx_empresas_cidade ON empresas(cidade);
CREATE INDEX idx_empresas_ramo ON empresas(ramo);
CREATE INDEX idx_empresas_status ON empresas(status);
```

**Tamanho típico por linha:** ~500 bytes
**Exemplo de row:**
```python
{
    'id': 1,
    'nome': 'Restaurante Delícia',
    'website': 'https://restaurante-delicia.com.br',
    'email': 'contato@restaurante-delicia.com.br',
    'telefone': '+55 11 98765-4321',
    'endereco': 'Rua das Flores 123, Centro',
    'cidade': 'São Paulo',
    'estado': 'SP',
    'ramo': 'Restaurantes',
    'fonte': 'google_maps',
    'status': 'novo',
    'data_coleta': '2024-04-13T10:30:45.123456',
    'ultima_atualizacao': '2024-04-13T10:30:45.123456',
    'criado_em': '2024-04-13T10:30:45.123456'
}
```

### Tabela: historico_alteracoes

```sql
CREATE TABLE IF NOT EXISTS historico_alteracoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    campo TEXT NOT NULL,
    valor_anterior TEXT,
    valor_novo TEXT,
    data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas (id) ON DELETE CASCADE
);

-- Tracking automaticamente todas as mudanças
```

**Exemplo:**
```python
{
    'id': 1,
    'empresa_id': 1,
    'campo': 'status',
    'valor_anterior': 'novo',
    'valor_novo': 'qualificado',
    'data_alteracao': '2024-04-13T15:45:30.000000'
}
```

## 📊 Tipos de Dados

### Strings Padronizadas

**Email:**
- Padrão: `nome.sobrenome@empresa.com.br` ou `nome@empresa.com.br`
- Validação: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- Exemplo: `joao.silva@techcorp.com.br`

**Website:**
- Padrão: `https://empresa.com.br` (sempre com protocolo)
- Validação: `^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$`
- Exemplo: `https://restaurante-delicia.com.br/`

**Telefone:**
- Padrão: `+55 11 98765-4321` (com DDD)
- Validação: `^\+?[\d\s\-\(\)]{10,}$`
- Exemplo: `+55 11 98765-4321` ou `(11) 98765-4321`

**Estado (UF):**
- Formato: 2 letras maiúsculas
- Exemplos: `SP`, `RJ`, `MG`, `BA`, `PE`

**Receita Anual:**
- Formato: `"{número}{sufixo}"`
- Valores: `"1M"`, `"10M"`, `"100M"`, `"1B"`, `"10B"`
- Significado: Million, Bilhão

**Número de Funcionários:**
- Formato: `"{min}-{max}"`
- Valores: `"1-10"`, `"50-100"`, `"500-1000"`, `"1000-5000"`, `"5000+"`

**Setor:**
- Exemplos: `"Technology"`, `"Healthcare"`, `"E-commerce"`, `"Varejo"`
- Case-sensitive: use Title Case para consistency

## 🔄 Conversões de Tipos

### JSON Serialization

```python
# Empresa para JSON
empresa_json = empresa.to_dict()
# {
#     "nome": "TechCorp",
#     "website": "https://techcorp.com.br",
#     "fonte": "google_maps",  # Enum convertido para string
#     "status": "novo",        # Enum convertido para string
#     "data_coleta": "2024-04-13T10:30:45.123456"  # ISO format
# }

# DadosEnriquecidos para JSON
enriquecidos_json = dados.to_dict()

# EmailGerado para JSON
email_json = email.to_dict()
```

### De/Para Banco de Dados

```python
# SQL → Python
row_sqlite = cursor.fetchone()
empresa = _row_para_empresa(row_sqlite)

# Python → SQL
cursor.execute(
    "INSERT INTO empresas (nome, ...) VALUES (?, ?, ...)",
    (empresa.nome, empresa.website, ...)
)
```

## 📈 Estatísticas Agregadas

### Estrutura de Retorno

```python
{
    'total_empresas': 45,
    'por_status': {
        'novo': 30,
        'qualificado': 10,
        'email_validado': 4,
        'contato_realizado': 1,
        'descartado': 0
    },
    'por_cidade': {
        'São Paulo': 25,
        'Rio de Janeiro': 15,
        'Belo Horizonte': 5
    },
    'por_ramo': {
        'restaurantes': 20,
        'lojas': 15,
        'consultoria': 10
    }
}
```

## 🎯 Scores e Métricas

### Quality Score (0-100)

**Fórmula:**
```
base_score = 50
+ nome_válido (10)
+ email_corporativo (15)
+ telefone_presente (10)
+ endereco_detalhado (10)
+ website_funcional (15)
+ ramo_válido (10)
- flags_alerta (variável)
```

**Ranges:**
- 0-30: Baixa qualidade (descartável)
- 30-60: Qualidade média (validar manualmente)
- 60-80: Boa qualidade (processar automaticamente)
- 80-100: Excelente (priorizar)

### Email Confidence (0-1)

**Fórmula:**
```
base = 0.50
+ email_matches_domain (0.25)
+ title_is_common (0.10)
+ hierarchy_level_high (0.15)
```

**Ranges:**
- 0.0-0.5: Baixa confiança (validar via API)
- 0.5-0.7: Média confiança (usar com cuidado)
- 0.7-0.9: Alta confiança (usar diretamente)
- 0.9-1.0: Muito alta (usar automaticamente)

## 🔍 Queryables Importantes

### Empresas por Status
```sql
SELECT nome, email, status, data_coleta 
FROM empresas 
WHERE status = 'qualificado' 
ORDER BY data_coleta DESC 
LIMIT 100;
```

### Leads não contatados
```sql
SELECT * FROM empresas 
WHERE status = 'novo' 
AND data_coleta > datetime('now', '-7 days')
LIMIT 50;
```

### Empresas por ramo e cidade
```sql
SELECT ramo, cidade, COUNT(*) as total 
FROM empresas 
GROUP BY ramo, cidade 
ORDER BY total DESC;
```

### Performance do enriquecimento
```sql
SELECT 
    COUNT(*) as total,
    COUNT(DISTINCT setor_industria) as setores_unicos,
    AVG(score_qualidade) as score_medio
FROM empresas 
WHERE fonte = 'google_maps';
```

## ⚙️ Configurações

### ExtratorConfig

```python
@dataclass
class ExtratorConfig:
    timeout_segundos: int = 30           # Timeout para requisições
    max_tentativas: int = 3              # Número máximo de retries
    intervalo_requisicoes: float = 1.0   # Delay entre requests (segundos)
    user_agent: str = "Mozilla/5.0..."   # User-Agent para web scraping
    banco_dados: str = "leads.db"        # Caminho do arquivo SQLite
```

### Environment Variables

```bash
# Database
DATABASE_PATH=./data/leads.db
DATABASE_BACKUP_DIR=./data/backups

# APIs
GOOGLE_API_KEY=sk-xxxxx
LINKEDIN_API_KEY=sk-xxxxx
OPENAI_API_KEY=sk-xxxxx

# Comportamento
REQUEST_TIMEOUT=30
MAX_RETRIES=3
REQUEST_INTERVAL=1.0
USER_AGENT=Mozilla/5.0...

# Logging
LOG_LEVEL=INFO
DEBUG=false

# Execução
WORKERS=4
```

## 📝 Exemplos de Dados

### Lead Completo
```json
{
    "id": 1,
    "nome": "TechCorp Brasil",
    "website": "https://techcorp.com.br",
    "email": "contato@techcorp.com.br",
    "telefone": "+55 11 3456-7890",
    "endereco": "Avenida Paulista, 1000, Sala 200",
    "cidade": "São Paulo",
    "estado": "SP",
    "ramo": "Technology",
    "fonte": "google_maps",
    "status": "qualificado",
    "data_coleta": "2024-04-13T08:30:00",
    "ultima_atualizacao": "2024-04-13T15:45:00",
    "criado_em": "2024-04-13T08:30:00"
}
```

### Email Gerado
```json
{
    "destinatario_email": "joao.silva@techcorp.com.br",
    "destinatario_nome": "João Silva",
    "assunto": "🎯 TechCorp: Aumento de ~30% em eficiência",
    "corpo": "Olá João,\n\nEncontrei seu perfil enquanto pesquisava líderes de CTO em Technology.\n\nEstou ajudando empresas como TechCorp a aumentar produtividade...",
    "tipo": "primeiro_contato",
    "gerado_por": "template",
    "versao_ab": "A",
    "data_geracao": "2024-04-13T16:30:00"
}
```

---

**Última atualização:** Abril 2024
