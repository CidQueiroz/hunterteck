# 🎯 Guia Rápido - Pipeline B2B Autônomo

## Comparação com AutoGTM

| Funcionalidade | AutoGTM | Nossa Solução |
|---|---|---|
| **Leads Encontrados/mês** | 2,000 | 2,000+ (ilimitado) |
| **Prospect Research** | ✅ Deep research agent | ✅ MS3 (Enricher) |
| **Email Generation** | ✅ Personalização IA | ✅ MS6 (Template + OpenAI) |
| **Auto-Sequências** | ✅ 1,000 sequences | ✅ Customizável |
| **Taxa de Entrega** | 97% | 95%+ (melhorável) |
| **Meetings/mês** | 3-15 | Escalável |
| **Custo/mês** | $2,000-5,000 | ~$100-500 (open-source) |
| **Customização** | Limitada | **Total controle** |

## 🚀 Quick Start

### 1. Instalação

```bash
# Clonar repositório
cd /home/cidquei/Projetos/hunterteck

# Instalar dependências
pip install -r services/lead_extractor/requirements.txt

# Setup do banco de dados
python -c "from services.lead_extractor.database import DatabaseConnection; db = DatabaseConnection(); db.criar_tabelas()"
```

### 2. Executar Pipeline Completo

```bash
python orquestrador.py
```

**Resultado esperado:**
```
✅ [MS1] EXTRAÇÃO: 10 leads extraídos
✅ [MS2] VALIDAÇÃO: 8 leads válidos (80%)
✅ [MS3] ENRIQUECIMENTO: 8 leads enriquecidos
✅ [MS4] DECISORES: 24 pessoas encontradas
✅ [MS6] EMAILS: 20 emails gerados
```

### 3. Exemplos de Uso Programático

#### Opção A: Usar Componentes Individuais

```python
from services.lead_extractor.main import PipelineExtracao

# Extrator de leads
pipeline = PipelineExtracao()

# Extrair
leads = pipeline.extrair_com_api_demo(
    ramo="restaurantes",
    cidade="São Paulo",
    estado="SP"
)

# Persistir
resultado = pipeline.persistir_leads(leads)
print(f"✅ {resultado['sucesso']} empresas persistidas")
```

#### Opção B: Pipeline Completo (Recomendado)

```python
from orquestrador import PipelineAutonomoB2B

# Criar pipeline
pipeline = PipelineAutonomoB2B()

# Executar tudo (extração → validação → enriquecimento → pessoas → emails)
resultado = pipeline.executar_pipeline_completo(
    query="restaurantes",
    cidade="São Paulo",
    estado="SP",
    limite_leads=50,
    gerar_emails=True
)

# Acessar resultados
emails = resultado['etapas']['emails']['emails']
pessoas = resultado['etapas']['pessoas']['pessoas']
```

## 📊 Microsserviços Disponíveis

### MS1: Lead Extractor ✅
- Coleta empresas em tempo real
- Fontes: Google Maps API, Web Scrape, APIs customizadas
- **Arquivo**: `services/lead_extractor/main.py`

```python
pipeline.extrair_com_google_maps("restaurantes", "São Paulo", "SP")
pipeline.extrair_com_api_demo("lojas", "Rio de Janeiro", "RJ")
```

### MS2: Data Validator ✅
- Valida qualidade dos dados
- Remove duplicatas
- Gera score de qualidade (0-100)
- **Arquivo**: `services/lead_extractor/validator.py`

```python
validador = ValidadorLeads()
leads_validos, stats = validador.validar_lote(leads)
```

### MS3: Data Enricher ✅
- Coleta info adicionais (receita, funcionários, setor)
- Encontra URLs de social media
- **Arquivo**: `services/lead_extractor/enricher.py`

```python
enriquecedor = EnriquecedorDados()
dados = enriquecedor.enriquecer_empresa(empresa)
print(f"Receita: {dados.receita_anual}")
```

### MS4: Person Finder ✅
- Localiza CEOs, CTOs, Diretores
- Gera emails corporativos realistas
- **Arquivo**: `services/lead_extractor/person_finder.py`

```python
finder = LocalizadorPessoas()
decisores = finder.encontrar_decisores("TechCorp", "techcorp.com.br")
```

### MS6: Email Generator ✅
- Gera emails personalizados
- 2 modos: Template ou OpenAI GPT-4
- A/B testing automático
- **Arquivo**: `services/lead_extractor/email_generator.py`

```python
gerador = GeradorEmails(usar_openai=True)
email = gerador.gerar_email(contexto)
print(email.assunto, email.corpo)
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```bash
# Banco de dados
DATABASE_PATH=./data/leads.db

# APIs (opcional)
GOOGLE_API_KEY=seu_api_key
LINKEDIN_API_KEY=seu_api_key
OPENAI_API_KEY=seu_api_key

# Comportamento
DEBUG=true
LOG_LEVEL=INFO
REQUEST_TIMEOUT=30
MAX_RETRIES=3

# Execução
WORKERS=4
```

## 📈 Métricas e Relatórios

### Obter Estatísticas

```python
pipeline = PipelineExtracao()
stats = pipeline.obter_estatisticas()

print(f"Total de empresas: {stats['total_empresas']}")
print(f"Por status: {stats['por_status']}")
print(f"Top cidades: {stats['por_cidade']}")
print(f"Setores: {stats['por_ramo']}")
```

### Listar Leads Recentes

```python
leads = pipeline.listar_leads_recentes(limite=50)
for lead in leads:
    print(f"{lead['nome']} ({lead['cidade']}) - {lead['status']}")
```

## ⚡ Performance

| Métrica | Valor | Notas |
|---------|-------|-------|
| Leads/seg | ~5-10 | Dependente da API |
| Validação | 1000 leads/seg | In-memory |
| Enriquecimento | ~2 leads/seg | Rate limiting |
| Geração de emails | ~10 emails/sec | Template mode |
| Com OpenAI | ~1 email/sec | ~$0.02 por email |

## 🔐 Segurança

- ✅ Validação de input em todos os endpoints
- ✅ Prepared statements (SQL injection prevention)
- ✅ Rate limiting automático
- ✅ Retry com backoff exponencial
- ✅ Logging sem dados sensíveis
- ✅ GDPR compliant (opt-in/unsubscribe)

## 🐛 Debugging

### Ver Logs

```bash
# Logs em tempo real
tail -f logs/lead_extractor_*.log

# Logs com filtro
grep "ERROR" logs/lead_extractor_*.log
```

### Modo Debug

```bash
DEBUG=true LOG_LEVEL=DEBUG python orquestrador.py
```

## 📚 Exemplos Avançados

### 1. Web Scraping Customizado

```python
from services.lead_extractor.main import PipelineExtracao

pipeline = PipelineExtracao()

# Custom CSS selectors
seletores = {
    'elemento': '.company-item',
    'nome': '.company-name',
    'website': 'a.company-link',
    'email': '.contact-email'
}

empresas = pipeline.extrair_com_web_scraping(
    url_base="https://diretorio-local.com.br",
    ramo="Varejo",
    cidade="São Paulo",
    estado="SP",
    seletores=seletores
)
```

### 2. Pipeline com Customização

```python
from orquestrador import PipelineAutonomoB2B

pipeline = PipelineAutonomoB2B()

# Executar apenas até MS4 (sem emails)
resultado = pipeline.executar_pipeline_completo(
    query="consultoria",
    cidade="Belo Horizonte",
    estado="MG",
    gerar_emails=False  # Não gerar emails
)
```

### 3. Usar OpenAI para Email Generation

```python
from services.lead_extractor.email_generator import GeradorEmails, ContextoEmail

# Requer OPENAI_API_KEY nas variáveis de ambiente
gerador = GeradorEmails(usar_openai=True)

contexto = ContextoEmail(
    nome_pessoa="João Silva",
    cargo_pessoa="CEO",
    empresa_nome="TechCorp",
    setor_empresa="Technology",
    pain_points=["Reduzir custos", "Melhorar eficiência"],
    valor_proposto="aumentar produtividade em 40%"
)

# Gerar com IA
email = gerador.gerar_email(contexto, usar_ia=True)
```

## 🚧 Próximas Melhorias

- [ ] MS5: ICP Generator (AI scoring)
- [ ] MS7: Outreach Orchestrator (email scheduling)
- [ ] MS8: Analytics Dashboard (real-time metrics)
- [ ] Multi-channel (LinkedIn, WhatsApp)
- [ ] Intent detection (website tracking)
- [ ] API REST endpoint
- [ ] Webhook integration
- [ ] Telegram bot for notifications

## 💡 Dicas

1. **Para começar vindo do zero**: Use `python orquestrador.py`
2. **Rate limiting**: Aumentar `REQUEST_INTERVAL` em `.env`
3. **Batch processing**: Usar `*_lote()` methods
4. **Customização**: Edit templates em `email_generator.py`
5. **Production**: Usar PostgreSQL em vez de SQLite

## 🆘 Troubleshooting

### "No such table: empresas"
```bash
python -c "from services.lead_extractor.database import DatabaseConnection; db = DatabaseConnection(); db.criar_tabelas()"
```

### "Rate limit atingido"
Aumentar `REQUEST_INTERVAL`:
```bash
REQUEST_INTERVAL=2.0 python orquestrador.py
```

### Emails não sendo gerados
Verificar: `USE_OPENAI=false` para usar templates (padrão)

## 📞 Suporte

- 📖 [Documentação completa](./ARQUITETURA.md)
- 🐛 Logs: `./logs/`
- 📊 Dados: `./data/leads.db`
- 💬 Issues: Via GitHub

---

**Pronto para começar? Execute:**
```bash
python orquestrador.py
```

**Boa sorte! 🚀**
