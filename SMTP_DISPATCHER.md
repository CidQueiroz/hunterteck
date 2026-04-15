# 📧 SMTP Dispatcher: Roteamento Dinâmico de Remetentes por Produto

## Visão Geral

O **SMTP Dispatcher** é um microsserviço que implementa disparo de emails com roteamento dinâmico de remetentes baseado em produtos identificados pelo `match_cdkteck_product`.

**Objetivo**: Garantir que cada email seja enviado com o alias de email correto, conforme o produto selecionado.

## 🎯 Funcionalidades Principais

### 1. **Roteamento Automático de Remetentes**

Mapeia automaticamente: `Produto → Email Alias`

```
SenseiDB  → senseidb@cdkteck.com.br
GestaoRPD → gestaorpd@cdkteck.com.br
PapoDados → papodados@cdkteck.com.br
CaçaPreço → cacapreco@cdkteck.com.br
BioCoach  → biocoach@cdkteck.com.br
```

### 2. **Integração Zoho Mail**

- ✅ Suporte SMTP via Zoho (smtp.zoho.com)
- ✅ Porta 587 (TLS) ou 465 (SSL)
- ✅ Autenticação segura
- ✅ Retry automático com backoff exponencial

### 3. **Type-Safe e Estruturado**

- ✅ Type hints completos (PEP 484)
- ✅ Dataclasses tipadas
- ✅ Enums para status e provedores
- ✅ Zero ambiguidade em tipos

### 4. **Logs Estruturados**

- ✅ Logs em múltiplos níveis (DEBUG, INFO, WARNING, ERROR)
- ✅ Rastreamento de remoção (auditoria)
- ✅ Timing de execução por email

### 5. **Tratamento Robusto de Exceções**

| Erro | Tipo | Causa | Ação | 
|------|------|-------|------|
| **ERRO_AUTENTICACAO** | SMTPAuthenticationError | Credenciais inválidas | Verificar ZOHO_EMAIL_ADMIN e ZOHO_SENHA_ADMIN |
| **ERRO_ALIAS** | SMTPRecipientsRefused (553) | Alias não configurado no Zoho | Cadast alias no Zoho Mail Admin |
| **ERRO_ROTEAMENTO** | KeyError | Produto desconhecido | Produto não reconhecido no catálogo |
| **ERRO_SMTP** | SMTPException / OSError | Falha geral de conexão | Retry automático (3x) |

## 🔧 Instalação e Configuração

### 1. Dependências

O módulo usa apenas bibliotecas built-in do Python:
- `smtplib` (SMTP)
- `email.mime` (mensagens MIME)
- `logging` (logging estruturado)
- `dataclasses` (tipagem)
- `enum` (status types)

✅ **Nenhuma dependência adicional necessária!**

### 2. Variáveis de Ambiente

```bash
# .env ou export
export ZOHO_SMTP_PORTA=587                    # 587 (TLS) ou 465 (SSL)
export ZOHO_USAR_TLS=true                     # true para TLS, false para SSL
export ZOHO_EMAIL_ADMIN=admin@cdkteck.com.br  # Email master no Zoho
export ZOHO_SENHA_ADMIN=sua_senha_aqui        # Senha do email master
```

### 3. Setup Zoho Mail

**Pré-requisito**: Você precisa ter aliases configurados no Zoho Mail Admin:

```
1. Login em mail.zoho.com (Admin)
2. Settings → Users and Aliases
3. Criar aliases:
   - senseidb@cdkteck.com.br
   - gestaorpd@cdkteck.com.br
   - papodados@cdkteck.com.br
   - cacapreco@cdkteck.com.br
   - biocoach@cdkteck.com.br
4. Each alias deve apontar para o email master ou caixa compartilhada
```

## 📚 API Reference

### ConfiguracaoSMTP

```python
@dataclass
class ConfiguracaoSMTP:
    host: str              # "smtp.zoho.com"
    porta: int             # 587 ou 465
    usar_tls: bool         # True → TLS, False → SSL
    email_admin: str       # Email do admin/master
    senha_admin: str       # Senha (nunca commitar!)
    timeout_conexao: int   # Segundos (default=30)
    tentativas_reconexao: int  # Quantas vezes tentar (default=3)
```

### MapeamentoAliases

```python
@dataclass
class MapeamentoAliases:
    PRODUTOS_EMAILS: Dict[str, str]  # Mapa produto → email
    EMAIL_PADRAO: str                 # Fallback se produto não encontrado
    
    def obter_alias(produto: str) -> str
    def validar_alias(produto: str) -> Tuple[bool, str]
```

### ResultadoDisparo

```python
@dataclass
class ResultadoDisparo:
    sucesso: bool                    # True se enviado
    status: StatusDisparo            # ENVIADO, ERRO_SMTP, etc
    destinatario: str                # Email de destino
    remetente: str                   # Email do remetente (alias)
    produto_selecionado: str         # Produto que determinou remetente
    mensagem: str                    # Mensagem descritiva
    data_disparo: datetime           # Quando foi enviado
    tempo_execucao_ms: Optional[float]  # Tempo em ms
    erro_detalhado: Optional[str]    # Stack trace se erro
    
    def to_dict() -> Dict[str, Any]  # Para logging/auditoria
```

### DispachadorSMTPProdutos

Classe principal que orquestra disparo de emails.

#### Inicializar

```python
from services.lead_extractor import DispachadorSMTPProdutos, ConfiguracaoSMTP

config = ConfiguracaoSMTP(
    host="smtp.zoho.com",
    porta=587,
    usar_tls=True,
    email_admin=os.getenv("ZOHO_EMAIL_ADMIN"),
    senha_admin=os.getenv("ZOHO_SENHA_ADMIN"),
)

dispatcher = DispachadorSMTPProdutos(config)
```

#### Método: disparar_email()

```python
resultado = dispatcher.disparar_email(
    destinatario="contato@empresa.com.br",          # Required
    assunto="Oportunidade especial para você",      # Required
    corpo_html="<h1>Olá!</h1><p>Texto aqui</p>",   # Required
    corpo_texto="Olá!\n\nTexto aqui",               # Optional
    produto_selecionado="GestaoRPD",                # Optional (roteamento)
    tentar_reconectar=True,                         # Default: True
) -> ResultadoDisparo
```

**Retorna**: `ResultadoDisparo` com sucesso/erro e detalhes

#### Método: disparar_lote()

```python
emails = [
    {
        "destinatario": "contato1@empresa.com",
        "assunto": "...",
        "corpo_html": "...",
        "corpo_texto": "...",  # Optional
        "produto_selecionado": "GestaoRPD",  # Optional
    },
    # ... mais emails
]

resultados = dispatcher.disparar_lote(
    emails=emails,
    parar_em_erro=False,  # If True, para em primeiro erro
) -> list[ResultadoDisparo]
```

**Retorna**: Lista de `ResultadoDisparo` para cada email

## 💡 Exemplos de Uso

### Uso Básico

```python
from services.lead_extractor import DispachadorSMTPProdutos, ConfiguracaoSMTP
import os

# 1. Configurar SMTP
config = ConfiguracaoSMTP(
    host="smtp.zoho.com",
    porta=587,
    usar_tls=True,
    email_admin=os.getenv("ZOHO_EMAIL_ADMIN"),
    senha_admin=os.getenv("ZOHO_SENHA_ADMIN"),
)

# 2. Inicializar dispatcher
dispatcher = DispachadorSMTPProdutos(config)

# 3. Enviar email com roteamento automático
resultado = dispatcher.disparar_email(
    destinatario="maria@clinicasilva.com.br",
    assunto="🎯 Oportunidade para Clínica Silva",
    corpo_html="<h2>Olá Dra. Maria!</h2>...",
    produto_selecionado="GestaoRPD",  # ← Determina remetente
)

if resultado.sucesso:
    print(f"✅ Email enviado via {resultado.remetente}")
else:
    print(f"❌ Erro: {resultado.mensagem}")
    print(f"   Detalhes: {resultado.erro_detalhado}")
```

### Integração com Product Matcher

```python
from services.lead_extractor import (
    match_cdkteck_product,
    DispachadorSMTPProdutos,
    ConfiguracaoSMTP
)

# 1. Classificar lead
match = match_cdkteck_product(
    "Clínica Odontológica",
    "50 pacientes, prontuários em papel"
)

# 2. Enviar email com produto identificado
config = ConfiguracaoSMTP(...)
dispatcher = DispachadorSMTPProdutos(config)

resultado = dispatcher.disparar_email(
    destinatario="maria@clinicasilva.com.br",
    assunto="Oportunidade para Clínica Silva",
    corpo_html=gerar_email_html(match),
    produto_selecionado=match['produto'],  # ← Seguro!
)
```

### Integração com Email Generator

```python
from services.lead_extractor import (
    GeradorEmails,
    DispachadorSMTPProdutos,
    match_cdkteck_product,
)

# 1. Classificar produto
match = match_cdkteck_product("Clínica", "...")

# 2. Gerar email personalizado
gerador = GeradorEmails()
email = gerador.gerar_email_com_product_match(
    nome_pessoa="Maria",
    cargo_pessoa="Diretora",
    empresa_nome="Clínica Silva",
    setor_empresa="Odontologia",
    website_empresa="clinicasilva.com.br",
    product_match_result=match,
    usar_ia=True,
)

# 3. Enviar email com roteamento automático
dispatcher = DispachadorSMTPProdutos(config)

resultado = dispatcher.disparar_email(
    destinatario="maria@clinicasilva.com.br",
    assunto=email.assunto,
    corpo_html=email.corpo,
    produto_selecionado=match['produto'],
)
```

### Batch Processing

```python
leads = [
    {
        "destinatario": "maria@clinicasilva.com.br",
        "assunto": "...",
        "corpo_html": "...",
        "produto_selecionado": "GestaoRPD",
    },
    {
        "destinatario": "joao@hospital.com.br",
        "assunto": "...",
        "corpo_html": "...",
        "produto_selecionado": "GestaoRPD",
    },
    # ... mais
]

resultados = dispatcher.disparar_lote(
    emails=leads,
    parar_em_erro=False,
)

# Análise de resultados
sucessos = [r for r in resultados if r.sucesso]
erros = [r for r in resultados if not r.sucesso]

print(f"✅ Enviados: {len(sucessos)}")
print(f"❌ Erros: {len(erros)}")

for erro in erros:
    print(f"   • {erro.destinatario}: {erro.status.value}")
```

## 🔍 Monitoramento e Auditoria

### Logging Estruturado

```python
import logging
import json

# Todos os eventos são logados automaticamente
# DEBUG: Conexões e detalhes
# INFO: Emails enviados com sucesso
# WARNING: Retries e reconexões
# ERROR: Falhas críticas

# Exemplo de log:
# INFO - ✅ Email enviado com sucesso | 
#        Destinatário: maria@clinicasilva.com.br | 
#        Remetente: gestaorpd@cdkteck.com.br | 
#        Produto: GestaoRPD | 
#        Tempo: 245.32ms
```

### Armazenar Resultados para Auditoria

```python
import json
from datetime import datetime

resultado = dispatcher.disparar_email(...)

# Converter para JSON para armazenamento
auditoria = {
    "timestamp": datetime.now().isoformat(),
    "resultado": resultado.to_dict(),
}

# Salvar em arquivo
with open("auditoria_emails.jsonl", "a") as f:
    f.write(json.dumps(auditoria, ensure_ascii=False) + "\n")

# Ou em banco de dados
db.auditorias.insert_one(auditoria)
```

### Status para Análise

```python
from services.lead_extractor import StatusDisparo

resultados = dispatcher.disparar_lote(emails)

# Agrupar por status
por_status = {}
for r in resultados:
    status = r.status.value
    if status not in por_status:
        por_status[status] = []
    por_status[status].append(r)

# Análise
print(f"Enviados: {len(por_status.get('enviado', []))}")
print(f"Erro SMTP: {len(por_status.get('erro_smtp', []))}")
print(f"Erro Autenticação: {len(por_status.get('erro_autenticacao', []))}")
print(f"Erro Alias: {len(por_status.get('erro_alias', []))}")
```

## ⚠️ Troubleshooting

### Erro: "Falha na autenticação SMTP"

**Causa**: Credenciais inválidas  
**Solução**:
1. Verificar `ZOHO_EMAIL_ADMIN` está correto
2. Verificar `ZOHO_SENHA_ADMIN` está correto
3. Se mudou senha no Zoho, atualizar .env
4. Verificar se email master está ativo no Zoho

### Erro: "Alias rejeitado pelo servidor"

**Causa**: Alias não cadastrado no Zoho ou sem permissão  
**Solução**:
1. Ir a mail.zoho.com → Admin
2. Verificar se alias existe em Users & Aliases
3. Verificar se email master tem permissão de envio
4. Verificar se alias está ativo (enabled)

### Erro: "Timeout de conexão"

**Causa**: Problema de rede ou Zoho indisponível  
**Solução**:
1. Aumentar `timeout_conexao` em ConfiguracaoSMTP (default 30s)
2. Verificar conectividade SMTP: `telnet smtp.zoho.com 587`
3. Implementar circuit breaker no pipeline
4. Usar fila (queue) com retry assíncrono

### Produto "desconhecido" sempre usa fallback

**Causa**: Produto não reconhecido ou typo  
**Solução**:
1. Verificar nome exato do produto (case-sensitive)
2. Usar ProdutoCDKTeck Enum para evitar typos
3. Log mostrará produto + alias realizado

```python
# ✅ Correto - Casa com Enum
from services.lead_extractor import ProdutoCDKTeck
produto = ProdutoCDKTeck.GESTAO_RPD.value  # "GestaoRPD"

# ❌ Evitar - String rígida
produto = "GestaoRPD"  # Pode ter typo
```

## 📊 Performance

| Operação | Tempo Médio | Notas |
|----------|------------|-------|
| Conexão SMTP | 100-200ms | Inclui TLS handshake |
| Construir MIME | 5-10ms | Muito rápido |
| Enviar 1 email | 200-500ms | Depende Zoho |
| Batch 100 emails | 20-50s | ~250ms/email |
| Retry (1x) | +5s | Backoff exponencial |

**Dica**: Para batch grande (100+), considere:
- Processar em paralelo com ThreadPoolExecutor
- Usar fila assíncrona (Celery/RQ)
- Rate limiting para não sobrecarregar Zoho

## 🔐 Segurança

### ✅ Boas Práticas Implementadas

- ✅ Nunca log senhas (redacted em output)
- ✅ Type hints previne injections
- ✅ Validação de configuração startup
- ✅ Headers MIME construídos corretamente
- ✅ Try/except em todas operações críticas

### 🔒 Antes de Produção

- [ ] Guardar `ZOHO_SENHA_ADMIN` em secrets manager (AWS/Vault)
- [ ] Nunca commitar .env com credenciais
- [ ] Auditar acesso aos aliases
- [ ] Implementar rate limiting
- [ ] Monitorar erros de autenticação (possível ataque)
- [ ] Usar TLS 1.2+ (Zoho mantém automático)
- [ ] Rotacionar senhas regularmente

## 📈 Roadmap

### v2.1 (Próximo)
- [ ] Suporte a attachments
- [ ] Custom headers (headers SMTP customizados)
- [ ] Rastreamento de delivery (tracking pixel)
- [ ] Integração com Bouncer API (validação pré-envio)

### v2.2
- [ ] Async/await com aiosmtplib
- [ ] Queue system (Redis/RabbitMQ)
- [ ] Multi-provider fallback (SendGrid se Zoho falhar)
- [ ] Analytics dashboard

### v2.3
- [ ] Machine learning para optimal send time
- [ ] A/B testing framework
- [ ] Template engine avançado

## 📞 Suporte

Para problemas:

1. **Verificar logs**: `tail -f logs/lead-extractor.log | grep ERRO`
2. **Consultar REFERENCIA_DADOS.md**: Schemas e tipos
3. **Rodar exemplo**: `python3 exemplo_smtp_dispatcher.py`
4. **Status codes**: Verificar enum `StatusDisparo`

## 📄 Integração com Pipeline

```python
# orquestrador.py ou pipeline completo

from services.lead_extractor import (
    match_cdkteck_product,
    GeradorEmails,
    DispachadorSMTPProdutos,
    ConfiguracaoSMTP,
)

# Pipeline: Extract → Match → Generate → Send
def pipeline_completo(empresa_nome: str, resumo: str, email_contato: str):
    # 1. Match
    match = match_cdkteck_product("seu niche", resumo)
    
    # 2. Generate
    gerador = GeradorEmails()
    email = gerador.gerar_email_com_product_match(...)
    
    # 3. Send
    config = ConfiguracaoSMTP(...)
    dispatcher = DispachadorSMTPProdutos(config)
    
    resultado = dispatcher.disparar_email(
        destinatario=email_contato,
        assunto=email.assunto,
        corpo_html=email.corpo,
        produto_selecionado=match['produto'],
    )
    
    return resultado
```

---

**Versão**: 1.0.0  
**Status**: ✅ Production Ready  
**Última Atualização**: Hoje  

**Stack**: Python 3.10+, Zoho Mail SMTP, Type Hints, Structured Logging
