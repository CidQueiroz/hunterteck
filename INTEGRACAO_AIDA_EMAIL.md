# 📧 Integração: Product Matcher + Email Generator com Framework AIDA

## Visão Geral

A função de geração de emails foi atualizada para integrar o output do `match_cdkteck_product`, permitindo a criação de cold emails altamente personalizados usando o framework **AIDA** (Atenção, Interesse, Desejo, Ação).

## 🎯 Fluxo Integrado

```
Lead → match_cdkteck_product() → gerar_email_com_product_match() → Email Personalizado
                                                                       com AIDA
```

## ✨ Funcionalidades Implementadas

### 1. Novo Campo em `ContextoEmail`

```python
@dataclass
class ContextoEmail:
    # ... campos existentes ...
    product_match_result: Optional[Dict[str, Any]] = None  # Output do match_cdkteck_product
```

### 2. Função `gerar_email_com_product_match()`

Novo método recomendado para integração completa:

```python
def gerar_email_com_product_match(
    nome_pessoa: str,
    cargo_pessoa: str,
    empresa_nome: str,
    setor_empresa: str,
    website_empresa: str,
    product_match_result: Dict[str, Any],  # Output do match_cdkteck_product
    usar_ia: bool = True,
    vendedor_nome: str = "Time CDKTeck",
    vendedor_email: str = "sdr@cdkteck.com",
    **kwargs
) -> EmailGerado:
```

**Vantagens**:
- Integração direta com `match_cdkteck_product`
- Extrai automaticamente dores resolvidas
- Usa sistema_prompt otimizado com framework AIDA
- Simples de usar, sem necessidade de configurar contexto manual

### 3. System Prompt Otimizado com AIDA

O `system_prompt` foi configurado com as diretrizes exatas:

```
"Você é um executivo de vendas B2B da CDKTECK. Escreva um e-mail frio 
(cold email) curto e direto utilizando o framework AIDA (Atenção, Interesse, 
Desejo, Ação) para o decisor da {nome_empresa}. 

O foco central do e-mail é a dor operacional do setor de {nicho_empresa}. 

Apresente a aplicação {produto_selecionado} como a solução exata para essa dor, 
destacando a proposta de valor: {proposta_de_valor}. 

Regras de ouro: 
- Não mencione tecnologias (React, Python, etc)
- Fale apenas sobre otimização de tempo, redução de custos ou vantagem competitiva
- O Call to Action (Ação) final deve ser uma oferta simples: 
  perguntar se o decisor aceita receber um vídeo de 2 minutos 
  demonstrando a ferramenta em funcionamento."
```

### 4. Função `_construir_prompt_com_product_match()`

Cria prompt e system_prompt dinamicamente baseado no resultado do product_matcher:

```python
@staticmethod
def _construir_prompt_com_product_match(contexto: ContextoEmail) -> tuple:
    """Retorna (prompt, system_prompt) com dados do product_match"""
```

## 🚀 Como Usar

### Método Recomendado (Novo)

```python
from services.lead_extractor.product_matcher import match_cdkteck_product
from services.lead_extractor.email_generator import GeradorEmails

# 1. Classificar lead para produto
match_result = match_cdkteck_product(
    lead_niche="Clínica Multiprofissional",
    lead_summary="Clínica com 50 pacientes, prontuários em papel, agendamentos manuais"
)

# 2. Inicializar gerador
gerador = GeradorEmails(usar_openai=True)  # Com IA

# 3. Gerar email com AIDA + Product Match (MÉTODO NOVO)
email = gerador.gerar_email_com_product_match(
    nome_pessoa="Dra. Maria Silva",
    cargo_pessoa="Diretora Clínica",
    empresa_nome="Clínica Dental Silva",
    setor_empresa="Saúde - Odontologia",
    website_empresa="clinicasilva.com.br",
    product_match_result=match_result,  # Passa resultado do product matcher
    usar_ia=True,  # Usar IA (GPT-4)
    vendedor_nome="João SDR",
    vendedor_email="joao@cdkteck.com"
)

# 4. Email pronto para enviar
print(email.corpo)
```

### Método Antigo (Compatível)

O método antigo continua funcionando:

```python
# Criar contexto manualmente
contexto = ContextoEmail(
    nome_pessoa="Dra. Maria",
    cargo_pessoa="Diretora",
    empresa_nome="Clínica Silva",
    setor_empresa="Odontologia",
    website_empresa="clinicasilva.com.br",
    valor_proposto="aumentar eficiência"
)

# Gerar email
email = gerador.gerar_email(contexto, usar_ia=True)
```

## 📊 Exemplo Completo

```python
from services.lead_extractor.product_matcher import match_cdkteck_product
from services.lead_extractor.email_generator import GeradorEmails
import os

# PASSO 1: Classificar lead
match_result = match_cdkteck_product(
    lead_niche="E-commerce de Eletrônicos",
    lead_summary="Loja online com 2000 SKUs, concorrência acirrada, margens pressionadas"
)

# Resultado: {
#   'produto': 'CaçaPreço',
#   'score_confianca': 100,
#   'proposta_valor': 'Otimização automática de preços para máxima margem',
#   'dores_resolvidas': ['Margens pressionadas', 'Concorrência acirrada', ...],
#   ...
# }

# PASSO 2: Gerar email com AIDA
gerador = GeradorEmails(
    usar_openai=True,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

email = gerador.gerar_email_com_product_match(
    nome_pessoa="João Silva",
    cargo_pessoa="CEO",
    empresa_nome="EcommerceFast",
    setor_empresa="E-commerce",
    website_empresa="ecommercefast.com.br",
    product_match_result=match_result,
    usar_ia=True  # Usar GPT-4
)

# PASSO 3: Email pronto
print("Assunto:", email.assunto)
print("Corpo:", email.corpo)

# Email irá conter:
# • ATENÇÃO: Hook que captura atenção
# • INTERESSE: Demonstra entendimento da dor do setor
# • DESEJO: Apresenta CaçaPreço como solução
# • AÇÃO: CTA simples (vídeo de 2 minutos)
```

## 🎨 Componentes AIDA no Email

### 1. **ATENÇÃO** (Linha de Abertura)
- Gancho que captura atenção do leitor
- Não menciona tecnologia
- Foca em observação sobre o setor
- **Exemplo**: "Vimos que vocês operam em um dos setores mais competitivos do e-commerce..."

### 2. **INTERESSE** (Corpo - Problema)
- Demonstra profundo entendimento da dor específica
- Referencia desafios reais do setor
- **Exemplo**: "Empresas em e-commerce enfrentam pressão constante de margens..."

### 3. **DESEJO** (Corpo - Solução)
- Apresenta o produto (identificado pelo product_matcher)
- Foca em **resultados**, não em tecnologia
- Highlights: tempo economizado, custos reduzidos, vantagem competitiva
- **Exemplo**: "CaçaPreço otimiza seus preços automaticamente..."

### 4. **AÇÃO** (Fechamento - CTA)
- Oferta simples e clara
- Reduz fricção (não pede reunião de 1h)
- **Padrão**: "Você teria 5 minutos para um vídeo de 2 minutos demonstrando isso em ação?"

## 🔧 Configuração para Produção

### Com IA (GPT-4) - RECOMENDADO

```python
import os

# Configurar OpenAI API
os.environ['OPENAI_API_KEY'] = 'sua-chave-aqui'

# Inicializar gerador COM IA
gerador = GeradorEmails(
    usar_openai=True,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Gerar email com AIDA
email = gerador.gerar_email_com_product_match(
    # ... args ...
    usar_ia=True  # Usar GPT-4 para melhor qualidade
)
```

### Sem IA (Template) - FALLBACK

```python
# Inicializar gerador OHNE IA
gerador = GeradorEmails(usar_openai=False)

# Gerar email com template
email = gerador.gerar_email_com_product_match(
    # ... args ...
    usar_ia=False  # Usar template pré-definido
)
```

## 📈 Batch Processing

```python
from services.lead_extractor.product_matcher import match_cdkteck_product
from services.lead_extractor.email_generator import GeradorEmails

leads = [
    {"nome": "Dr. João", "cargo": "CEO", "empresa": "HospitalXYZ", "niche": "Saúde"},
    {"nome": "Maria", "cargo": "CFO", "empresa": "FabricaABC", "niche": "Manufatura"},
    # ...
]

gerador = GeradorEmails(usar_openai=True)

emails = []
for lead in leads:
    # Classificar
    match = match_cdkteck_product(lead['niche'], lead['empresa'])
    
    # Gerar email
    email = gerador.gerar_email_com_product_match(
        nome_pessoa=lead['nome'],
        cargo_pessoa=lead['cargo'],
        empresa_nome=lead['empresa'],
        setor_empresa=lead['niche'],
        website_empresa=lead['empresa'].lower() + ".com.br",
        product_match_result=match,
        usar_ia=True
    )
    
    emails.append(email)

print(f"Gerados {len(emails)} emails com AIDA + Product Match")
```

## 🧪 Arquivo de Exemplos

Veja exemplos práticos executáveis em:

- **[exemplo_integracao_aida.py](../exemplo_integracao_aida.py)** (4 exemplos completos)
  - Exemplo 1: Pipeline completo
  - Exemplo 2: Batch processing
  - Exemplo 3: Fluxo com IA
  - Exemplo 4: Análise AIDA

**Executar**:
```bash
python3 exemplo_integracao_aida.py
```

## 🔄 Mudanças no Código

### Modificações em `email_generator.py`

1. ✅ Adicionado campo `product_match_result` em `ContextoEmail`
2. ✅ Nova função `gerar_email_com_product_match()`
3. ✅ Nova função `_construir_prompt_com_product_match()`
4. ✅ Atualizado `_gerar_com_openai()` para suportar product_match
5. ✅ System prompt otimizado com AIDA

### Compatibilidade

- ✅ Totalmente backward compatible
- ✅ Código antigo continua funcionando
- ✅ Novo método é adicional, não substitui

## 📊 Comparação: Antes vs Depois

### Antes (Manualmente)

```python
contexto = ContextoEmail(...)  # Configurar tudo manualmente
email = gerador.gerar_email(contexto)
# Sem integração com product_matcher
# System prompt genérico
```

### Depois (Com Product Match)

```python
match = match_cdkteck_product(niche, summary)  # 1. Classificar
email = gerador.gerar_email_com_product_match(  # 2. Gerar
    # ... simples!
    product_match_result=match
)
# Totalmente personalizado com AIDA
# System prompt otimizado para cada produto
# Dores extraídas automaticamente
```

## ⚡ Performance

- **Com Template**: < 50ms
- **Com IA (OpenAI)**: ~1-2s (aguardando API)

## 🎓 Framework AIDA Explicado

| Componente | O que é | Exemplo |
|-----------|---------|---------|
| **ATENÇÃO** | Hook inicial | "Detectamos que você..." |
| **INTERESSE** | Demonstrar entendimento | Dores específicas do setor |
| **DESEJO** | Apresentar solução | Produto + resultados |
| **AÇÃO** | CTA claro | Vídeo de 2 minutos |

## 🚀 Próximos Steps

- [ ] A/B testing de assuntos
- [ ] Análise de open rate por produto
- [ ] Otimização de CTA
- [ ] Integração com deliverability checker

## 📞 Suporte

Para dúvidas, consulte:
1. [exemplo_integracao_aida.py](../exemplo_integracao_aida.py) - Exemplos
2. [product_matcher.py](./product_matcher.py) - Classificador
3. [email_generator.py](./email_generator.py) - Gerador (agora com AIDA)

---

**Versão**: 2.0.0 (com AIDA + Product Match)

**Status**: ✅ Pronto para Produção
