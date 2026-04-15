# 🤖 Migração para Groq - Gerador de Emails

## Visão Geral

Substituímos o motor de geração de emails **OpenAI GPT-4** (pago) pela API **gratuita do Groq** (modelo llama3-70b-8192).

### Benefícios

✅ **Custo Zero**: Free Tier do Groq sem limites por mês  
✅ **Performance**: llama3-70b muito rápido (~1-2s por email)  
✅ **Qualidade**: Modelo 70B comparável a GPT-4 para copy de vendas  
✅ **Resiliência**: Retry automático com backoff exponencial contra rate limits  
✅ **Tipo Safety**: Mantém totalmente os type hints e contrato de dados  
✅ **Fallback**: Usa templates em caso de falha - **orquestrador NUNCA quebra**

---

## Instalação

### 1. Instalar dependências do Groq

```bash
pip install -r requirements_groq.txt
```

Ou instalar manualmente:
```bash
pip install groq==0.4.1
```

### 2. Configurar API Key do Groq

#### Opção A: Variável de Environment (Recomendado)

```bash
export GROQ_API_KEY="gsk_YOUR_API_KEY_HERE"
```

No `.env`:
```
GROQ_API_KEY=gsk_YOUR_API_KEY_HERE
```

#### Opção B: Passar ao inicializar

```python
from services.lead_extractor.email_generator import GeradorEmails

gerador = GeradorEmails(
    usar_groq=True,
    groq_api_key="gsk_YOUR_API_KEY_HERE"
)
```

### 3. Obter sua API Key do Groq

1. Acesse [console.groq.com](https://console.groq.com)
2. Crie conta (gratuita)
3. Gere uma API Key em "API Keys"
4. Use a key começa com `gsk_`

---

## Arquitetura de Resiliência

### GroqRetryHandler

Implementa retry automático com backoff exponencial:

```
Tentativa 1: Imediato
Tentativa 2: Aguarda 1s
Tentativa 3: Aguarda 2s
Tentativa 4: Aguarda 4s
Tentativa 5: Aguarda 8s (máx)
```

**O que é tratado:**
- ✅ Rate limits (429 / `rate_limited` error)
- ✅ Retry automático sem notificação
- ✅ Logging detalhado de tentativas
- ✅ Fallback para template se todas falharem

### Fluxo de Geração

```
1. Groq disponível? Tenta Groq com retry
         ↓
   Sucesso? → Retorna EmailGerado com gerado_por='groq'
         ↓
   Rate limit? → Retry com backoff automático
         ↓
   Persistente? → Retorna None
         ↓
2. OpenAI disponível? Tenta OpenAI (fallback)
         ↓
3. Ninguém funcionou? Usa template
         ↓
   Retorna EmailGerado com gerado_por='template'
```

### Em Batch

Para evitar rate limits em batch (`gerar_lote`):

```python
emails = gerador.gerar_lote(
    contextos=contextos,
    usar_ia=True,
    delay_entre_requisicoes=0.5  # 500ms entre requisições
)
```

**Comportamento:**
- ✅ Delay automático entre requisições (evita rate limit)
- ✅ Continua processando mesmo com erro em um email
- ✅ Logging de cada email gerado

---

## Uso

### Básico - Gerar um Email

```python
from services.lead_extractor.email_generator import (
    GeradorEmails, 
    ContextoEmail, 
    TipoEmail
)

# Inicializar gerador (Groq automático)
gerador = GeradorEmails()

# Preparar contexto
contexto = ContextoEmail(
    nome_pessoa="João Silva",
    cargo_pessoa="CEO",
    empresa_nome="TechCorp Brasil",
    setor_empresa="Educação",
    website_empresa="techcorp.com.br",
    pain_points=["Custos altos de treinamento", "Escalabilidade"],
    valor_proposto="reduzir custos de treinamento em 70%",
    tipo_email=TipoEmail.PRIMEIRO_CONTATO
)

# Gerar com IA (Groq)
email = gerador.gerar_email(contexto, usar_ia=True)

print(f"Assunto: {email.assunto}")
print(f"Corpo:\n{email.corpo}")
print(f"Gerado por: {email.gerado_por}")  # 'groq' ou 'template'
```

### Com Product Match (AIDA + Groq)

```python
from services.lead_extractor.product_matcher import match_cdkteck_product

# 1. Classificar lead para produto
match_result = match_cdkteck_product(
    lead_niche="Clínica Odontológica",
    lead_summary="30 pacientes, prontuários manuais, agenda em papel..."
)

# 2. Preparar contexto
contexto = ContextoEmail(
    nome_pessoa="Dra. Maria",
    cargo_pessoa="Proprietária",
    empresa_nome="Clínica Dental Maria",
    setor_empresa="Saúde - Odontologia",
    website_empresa="clinicadental-maria.com.br",
    product_match_result=match_result  # Essencial para usar AIDA
)

# 3. Gerar email personalizado com AIDA framework
email = gerador.gerar_email(contexto, usar_ia=True)

print(f"Produto: {email.contexto['produto']}")
print(f"Email: {email.assunto}\n{email.corpo}")
```

### Lote com Resiliência

```python
# Gerar 20 emails com resiliência a rate limits
emails = gerador.gerar_lote(
    contextos=contextos_list,
    usar_ia=True,  # Usa Groq
    versao_ab=True,  # 33% recebem variante B
    delay_entre_requisicoes=0.8  # 800ms entre requisições
)

# Continua mesmo com erros em alguns emails!
# Retorna lista com os que funcionaram + templates dos com erro
```

### Método Recomendado (AIDA + Product Match)

```python
# O método gerar_email_com_product_match já está pronto!
email = gerador.gerar_email_com_product_match(
    nome_pessoa="João",
    cargo_pessoa="Gerente",
    empresa_nome="Empresa X",
    setor_empresa="Varejo",
    website_empresa="empresax.com.br",
    product_match_result=match_result,
    usar_ia=True  # Usa Groq automaticamente
)
```

---

## Type Safety Garantido

Todos os type hints do projeto foram mantidos:

```python
# Assinatura do método
def gerar_lote(
    self,
    contextos: List[ContextoEmail],  # Type checked
    usar_ia: bool = False,  # Type checked
    versao_ab: bool = False,  # Type checked
    delay_entre_requisicoes: float = 0.5  # Type checked
) -> List[EmailGerado]:  # Retorno garantido
    ...

# Retorno é sempre EmailGerado
# Nunca muta a estrutura de dados
# SMTP Dispatcher consome exatamente o mesmo contrato
```

---

## Monitoramento e Logs

### Logs de Sucesso

```
INFO:services.lead_extractor.email_generator:Groq inicializado para geração de emails (modelo: llama3-70b-8192)
INFO:services.lead_extractor.email_generator:Gerando email para João Silva em TechCorp Brasil
DEBUG:services.lead_extractor.email_generator:Email gerado com sucesso via Groq para João Silva
```

### Logs de Rate Limit (Retry Automático)

```
WARNING:services.lead_extractor.email_generator.retry:⚠️ Rate limit atingido (tentativa 1/5). Aguardando 1.0s antes de retry...
WARNING:services.lead_extractor.email_generator.retry:⚠️ Rate limit atingido (tentativa 2/5). Aguardando 2.0s antes de retry...
INFO:services.lead_extractor.email_generator.retry:Tentativa 3/5 de chamada Groq
DEBUG:services.lead_extractor.email_generator:Email gerado com sucesso via Groq para João Silva
```

### Logs de Fallback (Rate Limit Persistente)

```
WARNING:services.lead_extractor.email_generator.retry:Rate limit persistente no Groq. Usando template para João Silva
INFO:services.lead_extractor.email_generator:Gerando email para João Silva em TechCorp Brasil
INFO:services.lead_extractor.email_generator:✅ Fallback para template funcionou
```

---

## Limite de Rate Limit (Free Tier Groq)

📊 **Groq Free Tier Limits:**
- 30 requisições por minuto
- 10.000 tokens por minuto
- Modelo: llama3-70b-8192

### Para Batch Seguro

```python
# Para 50 emails em lote
# Com delay de 0.5s = 2 emails/seg = ~100 seg = 1:40 min
# DENTRO do limite de 30 requesições/min? Não!

# Recomendado:
delay_entre_requisicoes = 1.2  # 1 email a cada 1.2s = ~50 emails em 1 min
```

**Ou use templates para lotes grandes:**

```python
# Modo template (nenhum limite)
emails = gerador.gerar_lote(
    contextos=contextos_list,
    usar_ia=False  # Sem IA, sem rate limit
)
```

---

## Migração de Código Existente

### Antes (OpenAI)

```python
gerador = GeradorEmails(usar_openai=True, openai_api_key="sk-...")
email = gerador.gerar_email(contexto, usar_ia=True)
```

### Depois (Groq - Automático)

```python
# Nem precisa especificar - Groq é o padrão agora!
gerador = GeradorEmails()  # Groq automático
email = gerador.gerar_email(contexto, usar_ia=True)

# OpenAI ainda funciona como fallback se Groq falhar
```

---

## Troubleshooting

### Problema: "GROQ_API_KEY não encontrada"

**Solução:**
```bash
# Verificar se a variável está setada
echo $GROQ_API_KEY

# Se vazio, setar
export GROQ_API_KEY="gsk_YOUR_KEY"

# Ou criar .env
echo "GROQ_API_KEY=gsk_YOUR_KEY" >> .env
python -m dotenv load  # Carregar .env
```

### Problema: "Groq não disponível... Usando templates"

**Causas possíveis:**
1. `groq` não instalado

**Solução:**
```bash
pip install groq==0.4.1
```

2. API Key inválida

**Solução:**
```bash
# Verificar key em console.groq.com
export GROQ_API_KEY="gsk_YOUR_VALID_KEY"
```

### Problema: Rate limits persistentes

**Solução:**
- Aumentar `delay_entre_requisicoes` em `gerar_lote()`
- Usar modo template para lotes grandes
- Distribuir requisições ao longo do tempo

---

## Próximos Passos

1. **Configurar GROQ_API_KEY** em sua environment
2. **Testar localmente**: 
   ```bash
   python -c "from services.lead_extractor.email_generator import GeradorEmails; g = GeradorEmails()"
   ```
3. **Usar em orquestrador**: Já está automático
4. **Monitorar logs**: Verificar `logs/` para performance
5. **(Opcional) A/B Testing**: Habilitar `versao_ab=True` nos lotes

---

## Referências

- 🔗 [Groq Console](https://console.groq.com)
- 🔗 [Groq API Docs](https://console.groq.com/docs)
- 🔗 [llama3-70b Specs](https://huggingface.co/meta-llama/Llama-2-70b)
- 📄 [email_generator.py](email_generator.py)
- 📄 [product_matcher.py](product_matcher.py)

---

**Última Atualização**: Abril de 2026  
**Versão**: 1.0 (Groq Stable)  
**Status**: ✅ Produção Pronto
