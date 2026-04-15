# 🚀 CDKTECK Command Center - Guia de Uso

## Visão Geral

O **Command Center** é uma interface visual Streamlit que permite executar o pipeline de prospecção B2B do HunterTeck **sem hardcoding** nem manipulação de código.

## Instalação

### 1. Instalar dependências

```bash
pip install -r requirements_app.txt
```

Ou, se já tiver as dependências do projeto:

```bash
pip install streamlit pandas
```

### 2. Verificar instalação

```bash
streamlit --version
```

## Como Executar

### Opção 1: Execução Local (Recomendado)

```bash
streamlit run app_hunter.py
```

A interface abrirá automaticamente em:
```
http://localhost:8501
```

### Opção 2: Especificar Host/Porta

```bash
streamlit run app_hunter.py --server.port 8502 --server.address 0.0.0.0
```

## Interface do Command Center

### 📋 Seções Principais

#### 1. **Sidebar (Painel Lateral)**
   - **Alvo da Campanha**: Dropdown com 7 opções pré-configuradas
   - **Volume de Leads (Batch)**: Slider de 5 a 50 leads
   - **Detalhes da Campanha**: Visualização automática do produto e configurações

#### 2. **Área Principal**
   - **Métricas**: Total de leads, produto alvo, volume
   - **Botão "🚀 Iniciar Prospecção"**: Dispara o pipeline
   - **Resultados**: Tabela com empresas prospectadas
   - **Download**: Exportar resultados em CSV

#### 3. **Informações Adicionais**
   - Abas expansíveis ("Sobre" e "Configurações Técnicas")

## Campanhas Disponíveis

| Campanha | Produto | Localização |
|----------|---------|-------------|
| Clínicas Odontológicas | GestaoRPD | Macaé, RJ |
| Escolas de Idiomas | SenseiDB | Macaé, RJ |
| Cursos Preparatórios | SenseiDB | Macaé, RJ |
| Treinamento Corporativo | SenseiDB | Rio de Janeiro, RJ |
| Varejo e Supermercados | CaçaPreço | Macaé, RJ |
| Indústrias Offshore | PapoDados | Macaé, RJ |
| Academias e Nutricionistas | BioCoach | Macaé, RJ |

## Fluxo de Execução

```
1. Selecionar Campanha no Sidebar
   ↓
2. Ajustar Volume de Leads (slider)
   ↓
3. Clicar em "🚀 Iniciar Prospecção"
   ↓
4. Aguardar Spinner: "Extraindo e enviando e-mails..."
   ↓
5. Ver Resultado: Success message + Tabela de empresas
   ↓
6. (Opcional) Download CSV dos resultados
```

## Funcionalidades Implementadas

✅ **Seleção Dinâmica de Campanhas**
- Mapeamento automático query → produto
- Sem necessidade de editar código

✅ **Controle de Volume**
- Slider interativo (5-50 leads)
- Validação automática

✅ **Execução do Pipeline**
- Chamada transparente ao `PipelineAutonomoB2B`
- Spinner durante execução
- Tratamento robusto de erros

✅ **Visualização de Resultados**
- Tabela formatada com dados das empresas
- Últimos leads prospectados em ordem cronológica inversa

✅ **Exportação de Dados**
- Download em CSV com timestamp

✅ **Type Safety**
- Mantém tipagem estática do projeto
- Nenhuma alteração nos microsserviços existentes

## Tipagem Estática

O arquivo `app_hunter.py` mantém:
- Type hints em todas as funções
- Dicionário `MAPEAMENTO_CAMPANHAS` com tipagem `Dict[str, Dict[str, str]]`
- Retorno tipado de dataframes: `pd.DataFrame`
- Contadores tipados: `int`

## Estrutura de Dados

### Mapeamento de Campanhas

```python
MAPEAMENTO_CAMPANHAS: Dict[str, Dict[str, str]] = {
    "Campanha": {
        "query": "termo_busca",
        "produto": "NomeProduto",
        "cidade": "Cidade",
        "estado": "UF",
        "descricao": "Descrição"
    },
    ...
}
```

### Retorno do Pipeline

```python
{
    'timestamp': str,
    'query': str,
    'cidade': str,
    'estado': str,
    'etapas': {
        'extracao': {...},
        'validacao': {...},
        'enriquecimento': {...},
        'pessoas': {...},
        'emails': {...}
    }
}
```

## Resolução de Problemas

### Problema: Módulos não encontrados

**Solução:**
```bash
# Garantir que está no diretório correto
cd /home/cidquei/Projetos/hunterteck

# Executar o app
streamlit run app_hunter.py
```

### Problema: Erro de banco de dados

**Solução:**
- Verificar se existe o arquivo `data/leads.db`
- Se não existir, o pipeline o criará automaticamente na primeira execução

### Problema: Porta já em uso

**Solução:**
```bash
streamlit run app_hunter.py --server.port 8503
```

## Logs

Os logs são salvos em:
```
logs/lead_extractor_YYYYMMDD_HHMMSS.log
```

E também exibidos no console durante execução.

## Próximos Passos

1. **Adicionar Autenticação**: Proteja o acesso com senha/API key
2. **Dashboard de Histórico**: Veja campanhas executadas anteriormente
3. **Agendamento**: Agende prospecções periódicas
4. **Webhooks**: Integre com sistemas externos
5. **Analytics**: Visualize métricas de sucesso das campanhas

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs em `logs/`
2. Consulte o `QUICK_START.md` do projeto principal
3. Revise o código em `app_hunter.py` para entender o fluxo

---

**Última Atualização**: Abril de 2026
**Versão**: 1.0
