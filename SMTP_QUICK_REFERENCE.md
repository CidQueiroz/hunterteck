# ⚡ Quick Reference: SMTP Dispatcher com Roteamento por Produto

## 1️⃣ Setup em 3 Passos

### Passo 1: Configurar Variáveis de Ambiente

```bash
# .env
export ZOHO_SMTP_PORTA=587                    # TLS
export ZOHO_USAR_TLS=true
export ZOHO_EMAIL_ADMIN=admin@cdkteck.com.br  # Email master no Zoho
export ZOHO_SENHA_ADMIN=sua_senha_aqui        # Nunca commitar isso!
```

### Passo 2: Setup Zoho Mail Admin

1. Login em `mail.zoho.com` (Admin)
2. Settings → Users & Aliases
3. Criar 5 aliases:
   - senseidb@cdkteck.com.br
   - gestaorpd@cdkteck.com.br
   - papodados@cdkteck.com.br
   - cacapreco@cdkteck.com.br
   - biocoach@cdkteck.com.br

### Passo 3: Usar em 5 Linhas

```python
from services.lead_extractor import DispachadorSMTPProdutos, ConfiguracaoSMTP
import os

config = ConfiguracaoSMTP(
    host="smtp.zoho.com", porta=587, usar_tls=True,
    email_admin=os.getenv("ZOHO_EMAIL_ADMIN"),
    senha_admin=os.getenv("ZOHO_SENHA_ADMIN"),
)

dispatcher = DispachadorSMTPProdutos(config)

resultado = dispatcher.disparar_email(
    destinatario="maria@clinicasilva.com.br",
    assunto="Oportunidade para você",
    corpo_html="<h2>Olá!</h2>...",
    produto_selecionado="GestaoRPD",  # ← Reteamento automático!
)

print("✅ Email enviado!" if resultado.sucesso else f"❌ {resultado.mensagem}")
```

## 2️⃣ Roteamento: Produto → Email

| Produto | Email de Envio |
|---------|----------------|
| **SenseiDB** | senseidb@cdkteck.com.br |
| **GestaoRPD** | gestaorpd@cdkteck.com.br |
| **PapoDados** | papodados@cdkteck.com.br |
| **CaçaPreço** | cacapreco@cdkteck.com.br |
| **BioCoach** | biocoach@cdkteck.com.br |
| *(Desconhecido)* | sdr@cdkteck.com.br *(fallback)* |

## 3️⃣ Integração Completa (Product Match → Email → SMTP)

```python
from services.lead_extractor import (
    match_cdkteck_product,
    GeradorEmails,
    DispachadorSMTPProdutos,
    ConfiguracaoSMTP,
)
import os

# 1️⃣ Classificar lead
match = match_cdkteck_product("Clínica", "50 pacientes, prontuários em papel")

# 2️⃣ Gerar email personalizado
gerador = GeradorEmails()
email = gerador.gerar_email_com_product_match(
    nome_pessoa="Dra. Maria",
    cargo_pessoa="Diretora",
    empresa_nome="Clínica Silva",
    setor_empresa="Odontologia",
    website_empresa="clinicasilva.com.br",
    product_match_result=match,
    usar_ia=True,
)

# 3️⃣ Enviar pelo alias correto
config = ConfiguracaoSMTP(...)
dispatcher = DispachadorSMTPProdutos(config)

resultado = dispatcher.disparar_email(
    destinatario="maria@clinicasilva.com.br",
    assunto=email.assunto,
    corpo_html=email.corpo,
    produto_selecionado=match['produto'],  # ← Rateamento automático!
)

print(f"✅ Email enviado via: {resultado.remetente}")
```

## 4️⃣ Estrutura de Retorno

```python
# ResultadoDisparo
{
    'sucesso': True,
    'status': 'enviado',  # Ou: erro_smtp, erro_alias, erro_autenticacao
    'destinatario': 'maria@clinicasilva.com.br',
    'remetente': 'gestaorpd@cdkteck.com.br',  # ← Alias usado
    'produto_selecionado': 'GestaoRPD',
    'mensagem': 'Email enviado com sucesso via alias gestaorpd@cdkteck.com.br',
    'data_disparo': '2024-04-14T10:30:45.123456',
    'tempo_execucao_ms': 245.3,
    'erro_detalhado': None,
}
```

## 5️⃣ Batch Processing

```python
leads = [
    {
        "destinatario": "maria@clinicasilva.com.br",
        "assunto": "Oportunidade para Clínica",
        "corpo_html": "<h2>Olá Maria!</h2>...",
        "produto_selecionado": "GestaoRPD",
    },
    {
        "destinatario": "joao@ecommerce.com.br",
        "assunto": "Oportunidade para E-commerce",
        "corpo_html": "<h2>Olá João!</h2>...",
        "produto_selecionado": "CaçaPreço",
    },
    # ... mais leads
]

resultados = dispatcher.disparar_lote(
    emails=leads,
    parar_em_erro=False,  # Continua mesmo se um falhar
)

sucessos = sum(1 for r in resultados if r.sucesso)
erros = len(resultados) - sucessos

print(f"✅ Enviados: {sucessos}")
print(f"❌ Erros: {erros}")
```

## 6️⃣ Status de Disparo (Enum)

```python
from services.lead_extractor import StatusDisparo

# StatusDisparo possui:
StatusDisparo.PENDENTE          # Aguardando
StatusDisparo.ENVIADO           # ✅ Sucesso
StatusDisparo.ERRO_SMTP         # Falha SMTP genérica
StatusDisparo.ERRO_ROTEAMENTO   # Produto não reconhecido
StatusDisparo.ERRO_AUTENTICACAO # Credenciais inválidas
StatusDisparo.ERRO_ALIAS        # Alias rejeitado por Zoho
StatusDisparo.CANCELADO         # Cancelado manualmente
```

## 7️⃣ Auditoria e Logging

```python
import json
from datetime import datetime

resultado = dispatcher.disparar_email(...)

# Converter para JSON para armazenar
auditoria = {
    "timestamp": datetime.now().isoformat(),
    "resultado": resultado.to_dict(),
}

# Salvar em arquivo JSONL
with open("auditoria_emails.jsonl", "a") as f:
    f.write(json.dumps(auditoria, ensure_ascii=False) + "\n")

# Logs automáticos (check logs/lead-extractor.log):
# INFO - ✅ Email enviado com sucesso | 
#        Destinatário: maria@clinicasilva.com.br | 
#        Remetente: gestaorpd@cdkteck.com.br | 
#        Tempo: 245.32ms
```

## 8️⃣ Troubleshooting Rápido

| Erro | Solução |
|------|---------|
| **ERRO_AUTENTICACAO** | Verifique ZOHO_EMAIL_ADMIN e ZOHO_SENHA_ADMIN |
| **ERRO_ALIAS** | Alias não criado no Zoho Mail Admin |
| **ERRO_ROTEAMENTO** | Produto com typo ou não reconhecido |
| **ERRO_SMTP** | Retry automático (max 3x com backoff) |
| **Timeout** | Aumentar `timeout_conexao` em ConfiguracaoSMTP |

## 9️⃣ Configurações Avançadas

```python
config = ConfiguracaoSMTP(
    host="smtp.zoho.com",
    porta=587,                    # 587 = TLS, 465 = SSL
    usar_tls=True,                # True para TLS, False para SSL
    email_admin="admin@...",
    senha_admin="...",
    timeout_conexao=30,           # Aumentar se lento
    tentativas_reconexao=3,       # Quantas vezes retry?
)
```

## 🔟 Exemplo Real do Email Enviado

```
From: gestaorpd@cdkteck.com.br           ← Alias automático por produto!
To: maria@clinicasilva.com.br
Subject: 🎯 Oportunidade para Clínica Silva - Diretora Clínica

Body:
┌─────────────────────────────────┐
│ ATENÇÃO                         │
│ "Dra. Maria, vimos que vocês... │
└─────────────────────────────────┘
...
[AIDA framework email aqui]
...
```

## 1️⃣1️⃣ Para Usar em Produção

```
✅ Checklist:

□ Configurou ZOHO_SMTP_PORTA (587 ou 465)?
□ Criou todos 5 aliases no Zoho Mail?
□ .env com ZOHO_EMAIL_ADMIN e ZOHO_SENHA_ADMIN?
□ Testou config.validar() retorna True?
□ Monitorando logs para erros?
□ Implementou retry logic para ERRO_SMTP?
□ Armazenando ResultadoDisparo para auditoria?
□ Implementou rate limiting/throttling?
□ Backup de email master funciona?
□ Pronto para produção! 🚀
```

## 1️⃣2️⃣ Arquivos Relacionados

- **[SMTP_DISPATCHER.md](./SMTP_DISPATCHER.md)** - Documentação completa
- **[exemplo_smtp_dispatcher.py](./exemplo_smtp_dispatcher.py)** - 5 exemplos executáveis
- **[INTEGRACAO_AIDA_EMAIL.md](./INTEGRACAO_AIDA_EMAIL.md)** - Integração com Email Generator
- **[services/lead_extractor/smtp_dispatcher.py](./services/lead_extractor/smtp_dispatcher.py)** - Código-fonte

## 1️⃣3️⃣ Executar Exemplos

```bash
# Ver 5 exemplos funcionando
python3 exemplo_smtp_dispatcher.py
```

---

**Versão**: 1.0.0  
**Status**: ✅ Production Ready  
**Última Atualização**: Hoje  

Ver documentação completa: [SMTP_DISPATCHER.md](./SMTP_DISPATCHER.md)
