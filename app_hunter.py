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

MAPEAMENTO_CAMPANHAS: Dict[str, Dict[str, str]] = {
    "Clínicas Odontológicas em Macaé, RJ": {
        "query": "clínicas odontológicas",
        "produto": "GestaoRPD",
        "cidade": "Macaé",
        "estado": "RJ",
        "descricao": "Gestão de consultórios e clínicas odontológicas"
    },
    "Escolas de Idiomas em Macaé, RJ": {
        "query": "escolas de idiomas",
        "produto": "SenseiDB",
        "cidade": "Macaé",
        "estado": "RJ",
        "descricao": "Plataforma educacional para escolas de idiomas"
    },
    "Cursos Preparatórios em Macaé, RJ": {
        "query": "cursos preparatórios",
        "produto": "SenseiDB",
        "cidade": "Macaé",
        "estado": "RJ",
        "descricao": "Gestão de cursos preparatórios e educacionais"
    },
    "Treinamento Corporativo no Rio de Janeiro": {
        "query": "treinamento corporativo",
        "produto": "SenseiDB",
        "cidade": "Rio de Janeiro",
        "estado": "RJ",
        "descricao": "Programas de treinamento corporativo"
    },
    "Varejo e Supermercados em Macaé, RJ": {
        "query": "varejo supermercados",
        "produto": "CaçaPreço",
        "cidade": "Macaé",
        "estado": "RJ",
        "descricao": "Inteligência de preços para varejo"
    },
    "Indústrias Offshore em Macaé, RJ": {
        "query": "indústrias offshore",
        "produto": "PapoDados",
        "cidade": "Macaé",
        "estado": "RJ",
        "descricao": "Análise de dados para indústria offshore"
    },
    "Academias e Nutricionistas em Macaé, RJ": {
        "query": "academias nutricionistas",
        "produto": "BioCoach",
        "cidade": "Macaé",
        "estado": "RJ",
        "descricao": "Plataforma de wellness e nutrição"
    },
}


# ============================================================================
# FUNCIONALIDADES DE BANCO DE DADOS
# ============================================================================

def obter_ultimos_leads(limite: int = 20) -> pd.DataFrame:
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
        page_title="CDKTECK Command Center - Hunter",
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
        "<h1 style='text-align: center;'>🚀 CDKTECK Command Center - Módulo Hunter</h1>",
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
        
        # Seleção de alvo da campanha
        alvo_campanha: str = st.selectbox(
            label="🎯 Selecione o Alvo da Campanha",
            options=list(MAPEAMENTO_CAMPANHAS.keys()),
            help="Escolha qual segmento de mercado será prospeccionado"
        )
        
        # Recuperar configurações da campanha
        config_campanha = MAPEAMENTO_CAMPANHAS[alvo_campanha]
        
        st.markdown("---")
        
        # Volume de leads em batch
        volume_leads: int = st.slider(
            label="📊 Volume de Leads (Batch)",
            min_value=5,
            max_value=50,
            value=20,
            step=5,
            help="Número de leads a prospeccionar neste batch"
        )
        
        st.markdown("---")
        
        # Exibir informações da campanha selecionada
        st.subheader("📋 Detalhes da Campanha")
        st.info(f"**Produto:** {config_campanha['produto']}\n\n"
                f"**Query:** {config_campanha['query']}\n\n"
                f"**Localização:** {config_campanha['cidade']}, {config_campanha['estado']}")
    
    # ========================================================================
    # ÁREA PRINCIPAL
    # ========================================================================
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_leads = contar_leads_total()
        st.metric(label="📈 Total de Leads no BD", value=total_leads)
    
    with col2:
        st.metric(label="🎯 Alvo desta Execução", value=config_campanha['produto'])
    
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
            with st.spinner("⏳ Extraindo e enviando e-mails..."):
                logger.info(
                    f"Iniciando pipeline | "
                    f"Campanha: {alvo_campanha} | "
                    f"Produto: {config_campanha['produto']} | "
                    f"Volume: {volume_leads}"
                )
                
                # Instanciar e executar pipeline
                pipeline = PipelineAutonomoB2B()
                
                resultado = pipeline.executar_pipeline_completo(
                    query=config_campanha['query'],
                    cidade=config_campanha['cidade'],
                    estado=config_campanha['estado'],
                    limite_leads=volume_leads,
                    gerar_emails=True
                )
                
                # Extrair métricas de sucesso
                etapa_extracao = resultado.get('etapas', {}).get('extracao', {})
                total_enviados = etapa_extracao.get('total_leads', 0)
                
                # Exibir sucesso
                st.divider()
                
                if total_enviados > 0:
                    st.success(
                        f"✅ Prospecção concluída com sucesso!\n\n"
                        f"📧 **{total_enviados}** e-mails disparados"
                    )
                    
                    # Exibir tabela de leads prospectados
                    st.subheader("📊 Últimas Empresas Prospectadas")
                    
                    df_leads = obter_ultimos_leads(limite=volume_leads + 10)
                    
                    if not df_leads.empty:
                        st.dataframe(
                            df_leads,
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Opção de download
                        csv_data = df_leads.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="📥 Baixar Leads (CSV)",
                            data=csv_data,
                            file_name=f"leads_{alvo_campanha.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("⚠️ Nenhum lead foi prospectado nesta execução.")
                else:
                    st.warning(
                        "⚠️ Nenhum lead foi prospectado. "
                        "Verifique os logs para mais informações."
                    )
                
                # Exibir resumo detalhado
                st.subheader("📋 Resumo Detalhado da Execução")
                
                col_resumo1, col_resumo2 = st.columns(2)
                
                with col_resumo1:
                    etapa_validacao = resultado.get('etapas', {}).get('validacao', {})
                    st.metric(
                        "Leads Validados",
                        len(etapa_validacao.get('leads_validos', []))
                    )
                
                with col_resumo2:
                    etapa_pessoas = resultado.get('etapas', {}).get('pessoas', {})
                    st.metric(
                        "Pessoas Encontradas",
                        len(etapa_pessoas.get('pessoas', []))
                    )
                
                logger.info(f"Pipeline finalizado com sucesso. Total: {total_enviados} leads")
        
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
        ### CDKTECK Command Center - Módulo Hunter
        
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
