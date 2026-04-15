# ⚡ Quick Reference: Email Generator com AIDA + Product Match

## 1️⃣ Usar em 3 Linhas

```python
from services.lead_extractor.product_matcher import match_cdkteck_product
from services.lead_extractor.email_generator import GeradorEmails

# 1. Classificar lead
match = match_cdkteck_product("Clínica Odontológica", "50 pacientes com prontuários em papel")

# 2. Gerar email (nova função)
gerador = GeradorEmails(usar_openai=True)
email = gerador.gerar_email_com_product_match(
    nome_pessoa="Dra. Maria", 
    cargo_pessoa="Diretora",
    empresa_nome="Clínica Silva",
    setor_empresa="Odontologia",
    website_empresa="clinicasilva.com.br",
    product_match_result=match,
    usar_ia=True  # Usa GPT-4
)

# 3. Email pronto!
print(email.corpo)
```

## 2️⃣ Output do Product Matcher

```python
match_result = {
    'produto': 'GestaoRPD',                          # Produto identificado
    'score_confianca': 72,                           # Score 0-100
    'proposta_valor': 'Gestão completa com prontuário eletrônico',
    'dores_resolvidas': [
        'Prontuários em papel desorganizados',
        'Agendamentos manuais cansativos',
        'Falta de integração com outros sistemas'
    ],
    'nichos_match': ['Clínicas', 'Consultórios', 'RH'],
}
```

## 3️⃣ O que o Email Gerado Contém (AIDA)

```
Subject: 🎯 Oportunidade para Clínica Silva - Diretora Clínica

Body:
┌─────────────────────────────────────────────────┐
│ ATENÇÃO                                         │
│ "Dra. Maria, vimos que vocês operam em uma      │
│ das áreas mais desafiadoras da saúde..."        │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ INTERESSE                                       │
│ "As clínicas hoje enfrentam..."                 │
│ • Prontuários em papel desorganizados           │
│ • Agendamentos manuais cansativos               │
│ • Falta de integração com outros sistemas       │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ DESEJO                                          │
│ "GestaoRPD é exatamente para isso:"             │
│ Gestão completa com prontuário eletrônico       │
│ ✅ Economia de tempo em 80%                      │
│ ✅ Redução de custo operacional                  │
│ ✅ Vantagem competitiva sobre concorrentes       │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ AÇÃO                                            │
│ "Você teria 5 min para um vídeo de 2 min        │
│ mostrando como funciona em ação?"                │
└─────────────────────────────────────────────────┘
```

## 4️⃣ Formas de Usar

### Com IA (GPT-4) - RECOMENDADO
```python
gerador = GeradorEmails(usar_openai=True)
email = gerador.gerar_email_com_product_match(
    # ... args ...
    usar_ia=True,  # ← Ativa GPT-4
    openai_api_key="sk-..."  # OPENAI_API_KEY
)
```

### Sem IA (Template) - FALLBACK
```python
gerador = GeradorEmails(usar_openai=False)
email = gerador.gerar_email_com_product_match(
    # ... args ...
    usar_ia=False,  # ← Usa template pré-definido
)
```

## 5️⃣ Batch Processing

```python
leads = [
    {"nome": "Dr. João", "empresa": "Hospital XYZ", "niche": "Saúde"},
    {"nome": "Maria", "empresa": "Fábrica ABC", "niche": "Manufatura"},
]

for lead in leads:
    # 1. Classificar
    match = match_cdkteck_product(lead['niche'], lead['empresa'])
    
    # 2. Gerar email
    email = gerador.gerar_email_com_product_match(
        nome_pessoa=lead['nome'],
        empresa_nome=lead['empresa'],
        setor_empresa=lead['niche'],
        product_match_result=match,
        usar_ia=True
    )
```

## 6️⃣ Produtos Suportados

| Produto | Nichos | Score Alto |
|---------|--------|-----------|
| **SenseiDB** | Educação, Knowledge Management | Universidades, Consultoria |
| **GestaoRPD** | Clínicas, RH, Administração | Clínicas, Hospitais |
| **PapoDados** | Indústria, Logística, Operações | Manufatura, Logística |
| **CaçaPreço** | E-commerce, Varejo | Loja Online, Marketplace |
| **BioCoach** | Fitness, Nutrição, Saúde | Academia, Nutricionista |

## 7️⃣ Dicas Importantes

### ✅ Faça
- Use com `usar_ia=True` para melhor qualidade
- Configure `OPENAI_API_KEY` para ativar GPT-4
- Processe em batch para melhor performance
- Valide `score_confianca >= 60` antes de enviar

### ❌ Não Faça
- Não mencione tecnologias no CTA (React, Python, etc)
- Não peça reunião de 1h (pede apenas vídeo de 2 min)
- Não ignore o `score_confianca` (< 30 = risco)
- Não customize o system_prompt (já está otimizado)

## 8️⃣ Framework AIDA Explicado

```
ATENÇÃO   = Hook que captura atenção
            (não spam, algo relevante ao setor)

INTERESSE = Demonstra entendimento da dor
            (lista problemas reais que ele enfrenta)

DESEJO    = Apresenta solução
            (produto + benefícios + valor)

AÇÃO      = CTA claro e simples
            ("Vídeo de 2 minutos?" é melhor que "Reunião 1h?")
```

## 9️⃣ Arquivos Relacionados

- **[INTEGRACAO_AIDA_EMAIL.md](./INTEGRACAO_AIDA_EMAIL.md)** - Documentação completa
- **[exemplo_integracao_aida.py](./exemplo_integracao_aida.py)** - 4 exemplos executáveis
- **[services/lead_extractor/email_generator.py](./services/lead_extractor/email_generator.py)** - Código
- **[services/lead_extractor/product_matcher.py](./services/lead_extractor/product_matcher.py)** - Classificador

## 🔟 Executar Exemplos

```bash
# Ver 4 exemplos funcionando
python3 exemplo_integracao_aida.py

# Output esperado:
# ✅ Lead classificado: GestaoRPD (72/100)
# ✅ Email gerado com sucesso!
# ✅ 3 emails processados em batch
# ✅ AIDA framework validado
```

## 1️⃣1️⃣ Troubleshooting

**Erro**: `ModuleNotFoundError: No module named 'openai'`
- Solução: `pip install openai` ou set `usar_openai=False`

**Erro**: `contexto.product_match_result is None`
- Solução: Passe `product_match_result=match` em gerar_email_com_product_match()

**Email genérico sem produto**
- Causa: Usando `gerar_email()` ao invés de `gerar_email_com_product_match()`
- Solução: Use a nova função com product_match_result

**Score baixo (< 30)**
- Aviso: É suspeito, produto pode estar errado
- Ação: Verifique o nicho + summary do lead

## 📊 Checklist de Uso

```
□ Importou product_matcher e email_generator?
□ Rodou match_cdkteck_product()?
□ Validou score_confianca >= 60?
□ Passou product_match_result em gerar_email_com_product_match()?
□ Configurou OPENAI_API_KEY (se usar_ia=True)?
□ Email contém ATENÇÃO + INTERESSE + DESEJO + AÇÃO?
□ Email NÃO mencionou tecnologias?
□ CTA é "vídeo de 2 minutos"?
□ Pronto para enviar!
```

---

**Versão**: 2.0.0
**Status**: ✅ Pronto para Produção
**Última Atualização**: Hoje

Ver também: [INTEGRACAO_AIDA_EMAIL.md](./INTEGRACAO_AIDA_EMAIL.md) para a versão completa.
