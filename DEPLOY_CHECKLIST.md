# ✅ CHECKLIST DE DEPLOY: SMTP Dispatcher em Produção

## 🚀 Checklist de Implementação

Use este checklist para colocar o SMTP Dispatcher em produção.

### FASE 1: Preparação no Zoho Mail ☐

- [ ] Login em `mail.zoho.com` com conta Admin
- [ ] Navegar para: **Settings → Users & Aliases**
- [ ] Criar alias: **senseidb@cdkteck.com.br**
  - [ ] Definir inbox de destino (compartilhado ou master)
  - [ ] Ativar alias (enabled = true)
- [ ] Criar alias: **gestaorpd@cdkteck.com.br**
  - [ ] Definir inbox de destino
  - [ ] Ativar alias
- [ ] Criar alias: **papodados@cdkteck.com.br**
  - [ ] Definir inbox de destino
  - [ ] Ativar alias
- [ ] Criar alias: **cacapreco@cdkteck.com.br**
  - [ ] Definir inbox de destino
  - [ ] Ativar alias
- [ ] Criar alias: **biocoach@cdkteck.com.br**
  - [ ] Definir inbox de destino
  - [ ] Ativar alias
- [ ] **Verificar**: Todos 5 aliases aparecem em Settings
- [ ] **Teste**: Enviar email manualmente de cada alias para verificar

### FASE 2: Configuração de Secrets ☐

- [ ] Guardar arquivo `.env` em local seguro (home, não repo)
- [ ] Adicionar `.env` ao `.gitignore`
- [ ] Preencherncontents do `.env`:
  ```
  ZOHO_SMTP_PORTA=587
  ZOHO_USAR_TLS=true
  ZOHO_EMAIL_ADMIN=admin@cdkteck.com.br
  ZOHO_SENHA_ADMIN=sua_senha_segura
  ```
- [ ] **Segurança**: Usar secrets manager em produção (AWS Secrets, Azure KeyVault, etc)
- [ ] **Backup**: Fazer backup de credenciais em local seguro
- [ ] **Rotação**: Planejar rotação de senha (ex: a cada 90 dias)

### FASE 3: Integração de Código ☐

- [ ] Copiar `services/lead_extractor/smtp_dispatcher.py` para projeto
- [ ] Atualizar `services/lead_extractor/__init__.py` com imports
- [ ] Testar import:
  ```bash
  python3 -c "from services.lead_extractor import DispachadorSMTPProdutos; print('✅ Import OK')"
  ```
- [ ] Criar arquivo de configuração centralizado (ex: `config.py`)
  ```python
  from services.lead_extractor import ConfiguracaoSMTP, DispachadorSMTPProdutos
  import os
  
  SMTP_CONFIG = ConfiguracaoSMTP(
      host="smtp.zoho.com",
      porta=int(os.getenv("ZOHO_SMTP_PORTA", "587")),
      usar_tls=os.getenv("ZOHO_USAR_TLS", "true").lower() == "true",
      email_admin=os.getenv("ZOHO_EMAIL_ADMIN"),
      senha_admin=os.getenv("ZOHO_SENHA_ADMIN"),
  )
  
  DISPATCHER = DispachadorSMTPProdutos(SMTP_CONFIG)
  ```
- [ ] Integrar dispatcher no seu pipeline/orquestrador

### FASE 4: Testes em Staging ☐

#### Teste 1: Configuração
- [ ] Criar instância de ConfiguracaoSMTP
- [ ] Validar: `config.validar()` retorna `True`
- [ ] Verificar: `config.porta` é 587 ou 465
- [ ] Verificar: `config.usar_tls` é boolean

#### Teste 2: Dispatcher
- [ ] Criar instância de DispachadorSMTPProdutos
- [ ] Não gerar exceção ValueError
- [ ] Logs mostram inicialização bem-sucedida

#### Teste 3: Email Único
- [ ] Disparar 1 email para seu próprio email
- [ ] Produto selecionado: "GestaoRPD"
- [ ] Verificar resultado.sucesso == True
- [ ] Verificar resultado.remetente == "gestaorpd@cdkteck.com.br"
- [ ] Verificar email chegou em segundos

#### Teste 4: Todos os 5 Produtos
- [ ] Disparar 1 email para cada produto:
  - [ ] SenseiDB → senseidb@cdkteck.com.br
  - [ ] GestaoRPD → gestaorpd@cdkteck.com.br
  - [ ] PapoDados → papodados@cdkteck.com.br
  - [ ] CaçaPreço → cacapreco@cdkteck.com.br
  - [ ] BioCoach → biocoach@cdkteck.com.br
- [ ] Todos 5 emails recebidos?
- [ ] Headers "From:" corretos em cada um?

#### Teste 5: Batch Processing
- [ ] Processar 3-5 emails em lote
- [ ] Verificar: `results = dispatcher.disparar_lote(emails)`
- [ ] Verificar: len(results) == len(emails)
- [ ] Contar sucessos: `sucessos = sum(1 for r in results if r.sucesso)`
- [ ] Todos emails entregues?

#### Teste 6: Tratamento de Erro
- [ ] Testar com credenciais erradas
- [ ] Resultado deve ter status = "erro_autenticacao"
- [ ] Log deve mostrar erro
- [ ] Sistema não deve crash

#### Teste 7: Logging
- [ ] Verificar logs em `logs/lead-extractor.log`
- [ ] Deve conter:
  - ✅ Logs INFO de envios bem-sucedidos
  - ⚠️ Logs WARNING de retries
  - ❌ Logs ERROR de falhas
- [ ] Timing em ms presente em cada log

### FASE 5: Performance ☐

- [ ] Endpoint disparar 1 email < 500ms
- [ ] Batch 10 emails < 5s
- [ ] CPU usage < 10%
- [ ] Memory footprint < 50MB
- [ ] Sem memory leaks após 100+ emails

### FASE 6: Monitoramento e Alertas ☐

- [ ] Setup logging centralizado (Stackdriver, LogRocket, etc)
- [ ] Criar alertas para:
  - [ ] ERRO_AUTENTICACAO (credenciais inválidas)
  - [ ] ERRO_ALIAS (alias rejeitado)
  - [ ] Taxa de erro > 5%
  - [ ] Latência > 1s por email
- [ ] Criar dashboard com:
  - [ ] Total emails enviados por hora
  - [ ] Taxa de sucesso por produto
  - [ ] Tempo médio de envio
  - [ ] Erros por tipo

### FASE 7: Segurança ☐

- [ ] .env NÃO está versionado no git
  - [ ] Verificar: `git ls-files | grep .env` (deve ser vazio)
- [ ] Senhas rotacionadas periodicamente (a cada 90 dias)
- [ ] Auditoria habilitada:
  - [ ] Todos envios logados
  - [ ] ResultadoDisparo armazenado em database
  - [ ] Conformidade GDPR/LGPD verificada
- [ ] Rate limiting implementado (não > 10 emails/segundo)
- [ ] Validação de destinatário antes de enviar
- [ ] Nenhuma senha em logs (redacted = True)

### FASE 8: Backup & Disaster Recovery ☐

- [ ] Backup de configuração SMTP
- [ ] Backup de logs
- [ ] Plano de contingência se Zoho Mail cair
  - [ ] [ ] Multi-provider fallback (SendGrid?)
  - [ ] [ ] Queue de retry em database
- [ ] Tested recovery procedure

### FASE 9: Documentação ☐

- [ ] Documentação interna atualizada
- [ ] Runbook de troubleshooting criado
- [ ] Treinamento da equipe concluído
- [ ] Diagrama de arquitetura desenhado
- [ ] README.md atualizado

### FASE 10: Deploy ☐

#### Staging
- [ ] Todos testes passaram
- [ ] Performance satisfatória
- [ ] Logs limpos
- [ ] Monitoramento funciona

#### Produção
- [ ] Backup de production realizado
- [ ] Janela de manutenção agendada (se necessário)
- [ ] Deploy código
- [ ] Ativar dispatcher em production
- [ ] Monitorar primeiras 24 horas
- [ ] Alertas funcionando
- [ ] Rollback plan preparado (se der problema)

---

## 📊 Métricas de Sucesso

Após deploy, medir:

| Métrica | Target | Ação se falhar |
|---------|--------|---------------|
| Taxa de sucesso | > 99% | Investigar STATUS em ResultadoDisparo |
| Latência média | < 300ms | Verificar Zoho load, retry config |
| Taxa de erro | < 1% | Verificar logs para tipo de erro |
| Uptime | > 99.9% | Setup alertas + escalation |
| Auditoria | 100% logged | Verificar logging configurado |

---

## 🔧 Troubleshooting Rápido

| Problema | Verificação | Solução |
|----------|-----------|---------|
| Erro AUTENTICACAO | ZOHO_EMAIL_ADMIN e ZOHO_SENHA_ADMIN | Verificar credenciais no Zoho |
| Erro ALIAS | Alias criado no Zoho? | Criar alias em Settings → Aliases |
| Timeout SMTP | Conexão à internet OK? | Aumentar timeout_conexao em ConfiguracaoSMTP |
| Memory leak | Muitos emails simultâneos? | Usar queue system (async) |
| Emails não chegam | Spam folder? DKIM/SPF? | Verificar Zoho Mail security settings |

---

## 📚 Documentação de Referência

- **SMTP_DISPATCHER.md** - API completa
- **SMTP_QUICK_REFERENCE.md** - Quick start
- **SMTP_ARQUITETURA_COMPLETA.md** - Decisões arquiteturais
- **exemplo_smtp_dispatcher.py** - Exemplos runáveis
- **exemplo_pipeline_completo.py** - Pipeline end-to-end

---

## ✅ Assinatura de Conclusão

- [ ] Responsável pelos testes: ___________________
- [ ] Responsável pelo deploy: ___________________
- [ ] Responsável pelo monitoramento: ___________________
- [ ] Data do deploy: ___________________
- [ ] Observações:

```
Para utilizar todos os 5 aliases, certifique-se de ter os 5 criados no Zoho.
Se adicionar novos produtos no futuro, também criar novos aliases.
Manter este checklist atualizado para próximos deploys.
```

---

**Versão**: 1.0.0  
**Última Atualização**: 14/04/2026  
**Status**: ✅ Production Ready
