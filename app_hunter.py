"""
CDKTECK Command Center - Módulo Hunter
Interface visual Streamlit para o pipeline de prospecção B2B.
Permite configuração dinâmica e execução sem hardcoding.
"""

import streamlit as st
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime
import sys

# Configurar imports do projeto
sys.path.insert(0, str(Path(__file__).parent))

from orquestrador import PipelineAutonomoB2B
from services.lead_extractor.database import DatabaseConnection
from services.lead_extractor.config import Config


# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# MAPEAMENTO DE CAMPANHAS
# ============================================================================

MAPEAMENTO_PRODUTOS = {
    "GestaoRPD": {
        "Clínicas Odontológicas": {"query": "clínicas odontológicas", "descricao": "Gestão e automação de agendamentos para consultórios odontológicos."},
        "Clínicas Médicas e Policlínicas": {"query": "clínicas médicas", "descricao": "Digitalização de prontuários e gestão de atendimento ao paciente."},
        "Clínicas de Psicologia": {"query": "clínicas de psicologia", "descricao": "Gestão de agendas e controle de pacotes de sessões."},
        "Clínicas de Fisioterapia": {"query": "clínicas de fisioterapia", "descricao": "Acompanhamento de evolução de pacientes e controle financeiro."},
        "Clínicas Veterinárias": {"query": "clínicas veterinárias", "descricao": "Gestão de histórico clínico animal e controle de estoque de medicamentos."},
        "Escritórios de Contabilidade": {"query": "escritórios de contabilidade", "descricao": "Automação de rotinas e gestão de documentos de clientes."},
        "Escritórios de Advocacia": {"query": "escritórios de advocacia", "descricao": "Gestão de prazos, processos e atendimento de clientes legais."},
        "Consultorias de RH": {"query": "consultorias de recursos humanos", "descricao": "Triagem de currículos e gestão de processos seletivos."},
        "Imobiliárias": {"query": "imobiliárias", "descricao": "Gestão de carteira de imóveis e automação de contratos."}
    },
    "SenseiDB": {
        "Escolas de Idiomas": {"query": "escolas de idiomas", "descricao": "Agentes IA para conversação e automação do suporte ao aluno."},
        "Cursos Preparatórios": {"query": "cursos preparatórios", "descricao": "Motor de busca inteligente (RAG) para apostilas e simulados."},
        "Treinamento Corporativo": {"query": "empresas de treinamento corporativo", "descricao": "Plataforma de capacitação automatizada para funcionários."},
        "Escolas Particulares (Ensino Básico)": {"query": "escolas particulares", "descricao": "Centralização da comunicação entre pais, alunos e secretaria."},
        "Faculdades e Universidades": {"query": "faculdades privadas", "descricao": "Atendimento automatizado para matrículas e suporte acadêmico."},
        "Autoescolas": {"query": "autoescolas", "descricao": "Automação de agendamentos de aulas práticas e teóricas."},
        "Cursos Técnicos e Profissionalizantes": {"query": "cursos técnicos", "descricao": "Gestão de trilhas de aprendizagem e certificações."}
    },
    "CaçaPreço": {
        "Varejo e Supermercados": {"query": "supermercados e mercados", "descricao": "Monitoramento de concorrência e precificação dinâmica."},
        "Farmácias e Drogarias": {"query": "farmácias e drogarias", "descricao": "Análise de preços de medicamentos e produtos de perfumaria."},
        "Lojas de Materiais de Construção": {"query": "lojas de materiais de construção", "descricao": "Inteligência de mercado para cotação de insumos e ferramentas."},
        "Lojas de Autopeças": {"query": "lojas de autopeças", "descricao": "Mapeamento de preços para reposição de peças automotivas."},
        "Lojas de Eletrônicos e Informática": {"query": "lojas de eletrônicos", "descricao": "Monitoramento de margens em equipamentos de alta depreciação."},
        "Distribuidoras de Bebidas e Alimentos": {"query": "distribuidoras de bebidas", "descricao": "Otimização de preços para compras em atacado e varejo."},
        "Pet Shops e Agropecuárias": {"query": "pet shops", "descricao": "Análise competitiva de rações e medicamentos veterinários."}
    },
    "PapoDados": {
        "Indústrias Offshore (Óleo e Gás)": {"query": "empresas offshore óleo e gás", "descricao": "Análise complexa de relatórios técnicos e dados de perfuração."},
        "Empresas de Logística e Transporte": {"query": "empresas de logística e transporte", "descricao": "Roteirização e análise preditiva de frotas e combustível."},
        "Empresas de Engenharia Civil": {"query": "construtoras e engenharia", "descricao": "Cruzamento de dados de plantas, orçamentos e cronogramas."},
        "Indústrias de Manufatura": {"query": "indústrias de manufatura", "descricao": "Monitoramento de OEE (Eficiência Global do Equipamento) e falhas."},
        "Operadores Portuários": {"query": "operadores portuários logísticos", "descricao": "Otimização de fluxo de carga e análise de manifestos alfandegários."},
        "Distribuidores de Insumos Industriais": {"query": "distribuidoras de insumos industriais", "descricao": "Previsão de demanda e gestão inteligente de grandes estoques."}
    },
    "BioCoach": {
        "Academias de Ginástica e Musculação": {"query": "academias de ginástica", "descricao": "Geração automatizada de treinos via IA e retenção de alunos."},
        "Nutricionistas e Clínicas de Nutrição": {"query": "clínicas de nutrição", "descricao": "Cálculo de macronutrientes via visão computacional e recordatório IA."},
        "Estúdios de Crossfit": {"query": "estúdios de crossfit", "descricao": "Monitoramento de carga de treino (WODs) e recuperação muscular."},
        "Clínicas de Estética e Spas": {"query": "clínicas de estética", "descricao": "Acompanhamento de protocolos estéticos e histórico do cliente."},
        "Empresas de Saúde Ocupacional": {"query": "empresas de saúde ocupacional", "descricao": "Mapeamento de ergonomia e prevenção de lesões no trabalho."},
        "Assessorias Esportivas": {"query": "assessorias esportivas", "descricao": "Análise de planilhas de corrida e periodização inteligente."}
    }
}


# ============================================================================
# FUNCIONALIDADES DE BANCO DE DADOS
# ============================================================================

def obter_ultimos_leads(limite) -> pd.DataFrame:
    """Recupera os últimos leads prospectados do banco de dados."""
    try:
        db = DatabaseConnection(Config.DATABASE_PATH)
        # Garantir que as tabelas existem
        db.criar_tabelas()
        
        empresas = db.listar_todas_empresas(limite=limite)
        
        if not empresas:
            return pd.DataFrame()
        
        # Converter para dataframe
        dados: List[Dict[str, Any]] = []
        for empresa in empresas:
            dados.append({
                "Nome da Empresa": empresa.nome,
                "Website": empresa.website,
                "Email": empresa.email or "—",
                "Telefone": empresa.telefone or "—",
                "Endereço": empresa.endereco,
                "Cidade": empresa.cidade,
                "Ramo": empresa.ramo,
                "Status": empresa.status.value,
                "Data Coleta": empresa.data_coleta.strftime("%d/%m/%Y %H:%M") 
                    if isinstance(empresa.data_coleta, datetime) else empresa.data_coleta,
            })
        
        return pd.DataFrame(dados)
    
    except Exception as e:
        logger.error(f"Erro ao recuperar leads: {e}")
        return pd.DataFrame()


def contar_leads_total() -> int:
    """Conta o número total de leads no banco de dados."""
    try:
        db = DatabaseConnection(Config.DATABASE_PATH)
        # Garantir que as tabelas existem
        db.criar_tabelas()
        
        todas = db.listar_todas_empresas(limite=999999)
        return len(todas)
    except Exception as e:
        logger.error(f"Erro ao contar leads: {e}")
        return 0


# ============================================================================
# CONFIGURAÇÃO DE INTERFACE STREAMLIT
# ============================================================================

def configurar_interface():
    """Configura a interface visual da aplicação."""
    st.set_page_config(
        page_title="HunterTeck",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Estilo CSS personalizado
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .campaign-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .success-metric {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Função principal da aplicação."""
    configurar_interface()
    
    # Título principal
    st.markdown(
        "<h1 style='text-align: center;'>🚀 HunterTeck </h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; color: gray;'>Interface de Prospecção B2B Inteligente</p>",
        unsafe_allow_html=True
    )
    
    st.divider()
    
    # ========================================================================
    # SIDEBAR - Configurações
    # ========================================================================
    
    with st.sidebar:
        st.header("⚙️ Configuração da Campanha")
        
        # Seleção de Produto
        produto_alvo: str = st.selectbox(
            label="🎯 Selecione a Aplicação",
            options=list(MAPEAMENTO_PRODUTOS.keys()),
            help="Escolha qual aplicação será o alvo da prospecção"
        )
        
        # Recuperar campanhas do produto e exibir seleção
        campanhas_do_produto = MAPEAMENTO_PRODUTOS[produto_alvo]
        
        # Localidade Dinâmica (livre para qualquer parte do mundo)
        col_cid, col_est = st.columns([2, 1])
        with col_cid:
            alvo_cidade = st.text_input(
                label="📍 Cidade Alvo",
                value="Macaé",
                placeholder="Qualquer cidade"
            )
        with col_est:
            alvo_estado = st.text_input(
                label="🗺️ Estado",
                value="RJ",
                placeholder="Ex: RJ"
            )
        
        executar_todas = st.checkbox("Executar TODAS as campanhas deste produto")
        
        if not executar_todas:
            alvo_campanha: str = st.selectbox(
                label="🎯 Selecione a Campanha Específica",
                options=list(campanhas_do_produto.keys()),
                help="Escolha qual segmento de mercado será prospeccionado"
            )
            config_campanha = campanhas_do_produto[alvo_campanha]
        else:
            alvo_campanha = "Todas as Campanhas"
            
        alvo_localidade = f"{alvo_cidade}, {alvo_estado}"
        
        st.markdown("---")
        
        # Volume de leads em batch
        volume_leads: int = st.slider(
            label="📊 Volume de Leads por Batch",
            min_value=5,
            max_value=50,
            value=20,
            step=5,
            help="Número de leads a prospeccionar neste batch"
        )
        
        st.markdown("---")
        
        # Validação Rascunho / Disparo Automático
        enviar_emails_automaticamente = st.checkbox(
            "🚀 Disparar E-mails Automaticamente (MS7)",
            value=False,
            help="Se desmarcado, os e-mails serão apenas gerados para validação (Rascunho) e exibidos no painel."
        )
        
        st.markdown("---")
        
        # Exibir informações da campanha selecionada
        st.subheader("📋 Detalhes da Execução")
        if executar_todas:
            st.info(f"**Produto:** {produto_alvo}\n\n"
                    f"**Modo:** TODAS as campanhas ({len(campanhas_do_produto)} segmentos)\n\n"
                    f"**Localização Foco:** {alvo_localidade}")
        else:
            st.info(f"**Produto:** {produto_alvo}\n\n"
                    f"**Query:** {config_campanha['query']}\n\n"
                    f"**Localização Foco:** {alvo_localidade}")
    
    # ========================================================================
    # MODO ESTADO (DISPARO DE RASCUNHOS ATRASADO)
    # ========================================================================
    if "rascunhos_aprovados" not in st.session_state:
        st.session_state["rascunhos_aprovados"] = []
        
    if st.session_state["rascunhos_aprovados"]:
        st.warning("⚠️ Você possui e-mails em rascunho aguardando disparo!")
        if st.button("🚀 CLIQUE AQUI PARA DISPARAR OS RASCUNHOS AGORA", type="primary"):
            with st.spinner("Enviando rascunhos para o SMTP Zoho..."):
                try:
                    pipeline = PipelineAutonomoB2B()
                    resultado_smtp = pipeline._executar_disparo_emails(st.session_state["rascunhos_aprovados"])
                    st.success(f"Disparo concluído: {resultado_smtp.get('enviados', 0)} enviados, {resultado_smtp.get('falhas', 0)} falhas.")
                    st.session_state["rascunhos_aprovados"] = []  # Limpa os rascunhos
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao disparar rascunhos: {str(e)}")
        st.divider()

    # ========================================================================
    # ÁREA PRINCIPAL
    # ========================================================================
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_leads = contar_leads_total()
        st.metric(label="📈 Total de Leads no BD", value=total_leads)
    
    with col2:
        st.metric(label="🎯 Produto Alvo", value=produto_alvo)
    
    with col3:
        st.metric(label="📦 Volume de Batch", value=volume_leads)
    
    st.divider()
    
    # Botão de disparo do pipeline
    col_button, col_spacer = st.columns([1, 3])
    
    with col_button:
        botao_iniciar = st.button(
            label="🚀 Iniciar Prospecção",
            use_container_width=True,
            type="primary"
        )
    
    # ========================================================================
    # EXECUÇÃO DO PIPELINE
    # ========================================================================
    
    if botao_iniciar:
        try:
            with st.spinner("⏳ Processando fila de extração e disparo..."):
                logger.info(f"Iniciando pipeline | Produto: {produto_alvo} | Volume: {volume_leads}")
                
                pipeline = PipelineAutonomoB2B()
                
                # Montar lista de execuções
                combinacoes = []
                if executar_todas:
                    for nome_camp, conf in campanhas_do_produto.items():
                        combinacoes.append((nome_camp, conf, alvo_cidade, alvo_estado))
                else:
                    combinacoes.append((alvo_campanha, config_campanha, alvo_cidade, alvo_estado))
                
                total_enviados_global = 0
                resultados_globais = []
                
                # Executar fila
                for nome_campanha_atual, config_atual, cid_atual, est_atual in combinacoes:
                    st.toast(f"Prospecção: {nome_campanha_atual} em {cid_atual}...")
                    logger.info(f"Executando -> {nome_campanha_atual} em {cid_atual}")
                    
                    resultado = pipeline.executar_pipeline_completo(
                        query=config_atual['query'],
                        cidade=cid_atual,
                        estado=est_atual,
                        limite_leads=volume_leads,
                        gerar_emails=True,
                        disparar_emails=enviar_emails_automaticamente
                    )
                    
                    etapa_extracao = resultado.get('etapas', {}).get('extracao', {})
                    enviados_agora = etapa_extracao.get('total_leads', 0)
                    total_enviados_global += enviados_agora
                    resultados_globais.append(resultado)
                
                # Exibir sucesso e dashboard
                st.divider()
                
                if total_enviados_global > 0:
                    st.success(
                        f"✅ Prospecção em lote concluída com sucesso!\n\n"
                        f"📧 **{total_enviados_global}** contatos abordados"
                    )
                    
                    # Exibir tabela de leads prospectados
                    st.subheader("📊 Últimas Empresas Prospectadas")
                    
                    # Mostrar e-mails gerados em rascunho se disparar_emails foi falso
                    if not enviar_emails_automaticamente:
                        st.warning("📥 MODO RASCUNHO ATIVO: Os e-mails abaixo foram gerados, mas NÃO foram enviados pelo SMTP.")
                        st.subheader("📝 Rascunhos Gerados (Validação)")
                        import streamlit.components.v1 as components
                        
                        todos_rascunhos = []
                        
                        for idx, res in enumerate(resultados_globais):
                            emails_do_lote = res.get('etapas', {}).get('emails', {}).get('emails', [])
                            for email in emails_do_lote:
                                if email.get('destinatario_email'):
                                    todos_rascunhos.append(email)
                                    with st.expander(f"📧 E-mail para: {email.get('destinatario_nome', 'Desconhecido')} ({email.get('destinatario_email', '')})"):
                                        st.write(f"**Assunto:** {email.get('assunto', '')}")
                                        components.html(email.get('corpo', ''), height=300, scrolling=True)
                        
                        if todos_rascunhos:
                            st.session_state["rascunhos_aprovados"] = todos_rascunhos
                            st.info("⬆️ Role para o topo da página para disparar esses rascunhos!")
                            
                        st.divider()

                    # Para obter leads, pedimos (volume_leads * num_combinacoes) do banco
                    df_leads = obter_ultimos_leads(limite=(volume_leads * len(combinacoes)) + 10)
                    
                    if not df_leads.empty:
                        st.dataframe(
                            df_leads,
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Opção de download
                        csv_data = df_leads.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="📥 Baixar Leads Abordados (CSV)",
                            data=csv_data,
                            file_name=f"leads_{produto_alvo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("⚠️ Nenhum lead foi prospectado nesta execução.")
                else:
                    st.warning(
                        "⚠️ Nenhum lead foi prospectado. "
                        "Verifique os logs ou os limites de API."
                    )
                
                # Exibir resumo detalhado acumulado
                st.subheader("📋 Métricas Acumuladas da Execução")
                
                col_resumo1, col_resumo2 = st.columns(2)
                
                total_validados = 0
                total_pessoas = 0
                for res in resultados_globais:
                    etapas = res.get('etapas', {})
                    total_validados += len(etapas.get('validacao', {}).get('leads_validos', []))
                    total_pessoas += len(etapas.get('pessoas', {}).get('pessoas', []))
                
                with col_resumo1:
                    st.metric("Total de Leads Validados", total_validados)
                
                with col_resumo2:
                    st.metric("Total de Executivos Encontrados", total_pessoas)
                
                logger.info(f"Pipeline batch finalizado com sucesso.")
        
        except Exception as e:
            logger.error(f"Erro durante execução do pipeline: {e}")
            st.error(
                f"❌ Erro durante a execução:\n\n```\n{str(e)}\n```\n\n"
                f"Verifique os logs para mais detalhes."
            )
    
    # ========================================================================
    # RODAPÉ E INFORMAÇÕES
    # ========================================================================
    
    st.divider()
    
    with st.expander("ℹ️ Sobre o Command Center"):
        st.markdown("""
        ### HunterTeck
        
        Este painel foi desenvolvido para facilitar a execução do pipeline de prospecção B2B
        sem necessidade de hardcoding ou manipulação de código.
        
        **Funcionalidades:**
        - ✅ Seleção dinâmica de campanhas por segmento
        - ✅ Controle de volume de prospecção
        - ✅ Execução automática do pipeline
        - ✅ Visualização de resultados em tempo real
        - ✅ Exportação de dados em CSV
        
        **Produtos Suportados:**
        - 🏥 GestaoRPD: Gestão de consultórios e clínicas
        - 📚 SenseiDB: Plataforma educacional
        - 💹 CaçaPreço: Inteligência de preços
        - 📊 PapoDados: Análise de dados corporativos
        - 💪 BioCoach: Plataforma de wellness
        """)
    
    with st.expander("🛠️ Configurações Técnicas"):
        st.markdown(f"""
        **Banco de Dados:** {Config.DATABASE_PATH}
        
        **Diretório de Logs:** {Config.LOGS_DIR}
        
        **Timeout de Requisição:** {Config.REQUEST_TIMEOUT}s
        
        **Máximo de Tentativas:** {Config.MAX_RETRIES}
        """)


if __name__ == "__main__":
    main()
