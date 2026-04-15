"""
PIPELINE COMPLETO: Lead Classification → Email Generation → SMTP Dispatch
Demonstra a integração end-to-end através de todos os microsserviços.
"""

from services.lead_extractor import (
    match_cdkteck_product,
    GeradorEmails,
    DispachadorSMTPProdutos,
    ConfiguracaoSMTP,
    ContextoEmail,
)
import os
import logging
from datetime import datetime


# ============================================================================
# SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def obter_config_zoho_mock() -> ConfiguracaoSMTP:
    """Mock de configuração para demonstração (não envia realmente)."""
    return ConfiguracaoSMTP(
        host="smtp.zoho.com",
        porta=int(os.getenv("ZOHO_SMTP_PORTA", "587")),
        usar_tls=os.getenv("ZOHO_USAR_TLS", "true").lower() == "true",
        email_admin=os.getenv("ZOHO_EMAIL_ADMIN", "admin@cdkteck.com.br"),
        senha_admin=os.getenv("ZOHO_SENHA_ADMIN", "demo_senha_nao_enviar"),
        timeout_conexao=30,
        tentativas_reconexao=3,
    )


# ============================================================================
# PIPELINE PRINCIPAL
# ============================================================================

def processar_lead_completo(
    nome_contato: str,
    cargo_contato: str,
    empresa_nome: str,
    niche_empresa: str,
    resumo_empresa: str,
    email_contato: str,
    website_empresa: str,
) -> dict:
    """
    Pipeline completo:
    1. Classificar lead para produto
    2. Gerar email personalizado com AIDA
    3. Simular disparo com roteamento correto
    
    Returns:
        Dict com resultado completo
    """
    
    resultado = {
        'timestamp': datetime.now().isoformat(),
        'lead': {
            'nome': nome_contato,
            'cargo': cargo_contato,
            'empresa': empresa_nome,
            'email': email_contato,
        },
        'produto': None,
        'email_gerado': None,
        'roteamento': None,
        'status': 'INICIADO',
    }
    
    try:
        # =================================================================
        # ETAPA 1: Classificar Lead com Product Matcher
        # =================================================================
        print("\n" + "=" * 80)
        print(f"📌 LEAD: {nome_contato} ({cargo_contato}) na {empresa_nome}")
        print("=" * 80)
        
        print(f"\n[ETAPA 1] 🔍 Classificando lead para produto CDKTeck...")
        print(f"Nicho: {niche_empresa}")
        print(f"Resumo: {resumo_empresa}")
        
        match = match_cdkteck_product(niche_empresa, resumo_empresa)
        
        print(f"\n✅ CLASSIFICAÇÃO CONCLUÍDA")
        print(f"   Produto: {match['produto']}")
        print(f"   Score: {match['score_confianca']}/100")
        print(f"   Proposta: {match['proposta_valor']}")
        print(f"   Dores: {', '.join(match['dores_resolvidas'][:2])}")
        
        resultado['produto'] = {
            'nome': match['produto'],
            'score': match['score_confianca'],
            'proposta_valor': match['proposta_valor'],
        }
        
        # =================================================================
        # ETAPA 2: Gerar Email Personalizado com AIDA
        # =================================================================
        print(f"\n[ETAPA 2] 📧 Gerando email personalizado com AIDA...")
        
        gerador = GeradorEmails(usar_openai=False)  # Template para demo
        
        contexto = ContextoEmail(
            nome_pessoa=nome_contato,
            cargo_pessoa=cargo_contato,
            empresa_nome=empresa_nome,
            setor_empresa=niche_empresa,
            website_empresa=website_empresa,
            vendedor_nome="Time CDKTeck",
            vendedor_email="sdr@cdkteck.com.br",
            product_match_result=match,
        )
        
        email = gerador.gerar_email_com_product_match(
            nome_pessoa=nome_contato,
            cargo_pessoa=cargo_contato,
            empresa_nome=empresa_nome,
            setor_empresa=niche_empresa,
            website_empresa=website_empresa,
            product_match_result=match,
            usar_ia=False,  # Template
        )
        
        print(f"\n✅ EMAIL GERADO COM SUCESSO")
        print(f"   Assunto: {email.assunto}")
        print(f"   Tipo: {email.tipo.value}")
        print(f"   Gerado por: {email.gerado_por}")
        print(f"   Tamanho corpo: {len(email.corpo)} caracteres")
        
        resultado['email_gerado'] = {
            'assunto': email.assunto,
            'tipo': email.tipo.value,
            'corpus_length': len(email.corpo),
        }
        
        # =================================================================
        # ETAPA 3: Roteamento SMTP com Dispatcher
        # =================================================================
        print(f"\n[ETAPA 3] 🚀 Executando roteamento SMTP...")
        
        config = obter_config_zoho_mock()
        dispatcher = DispachadorSMTPProdutos(config)
        
        # Obter remetente baseado no produto
        from services.lead_extractor import MapeamentoAliases
        aliases = MapeamentoAliases()
        remetente = aliases.obter_alias(match['produto'])
        
        print(f"\n   ROTEAMENTO AUTOMÁTICO")
        print(f"   Produto Identificado: {match['produto']}")
        print(f"   Remetente Determinado: {remetente}")
        print(f"   Destinatário: {nome_contato} <{email_contato}>")
        
        # Simular envio (em produção, usar config real)
        print(f"\n   SIMULAÇÃO DE DISPARO (demo mode - não envia realmente)")
        print(f"   ───────────────────────────────────────────────────")
        print(f"   From: {remetente}")
        print(f"   To: {email_contato}")
        print(f"   Subject: {email.assunto}")
        print(f"   Body: {len(email.corpo)} chars")
        print(f"   Status: ✅ PRONTO PARA ENVIO")
        
        resultado['roteamento'] = {
            'produto': match['produto'],
            'remetente': remetente,
            'destinatario': email_contato,
            'status': 'pronto_para_envio',
        }
        
        # Em produção, descomentar:
        # resultado_smtp = dispatcher.disparar_email(
        #     destinatario=email_contato,
        #     assunto=email.assunto,
        #     corpo_html=email.corpo,
        #     produto_selecionado=match['produto'],
        # )
        # resultado['smtp'] = resultado_smtp.to_dict()
        
        resultado['status'] = 'SUCESSO'
        
    except Exception as e:
        logger.error(f"Erro no pipeline: {str(e)}", exc_info=True)
        resultado['status'] = f'ERRO: {str(e)}'
    
    return resultado


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def processar_lote_leads(leads: list) -> list:
    """Processa múltiplos leads através do pipeline."""
    
    print("\n" + "🔄 " * 20)
    print(f"PROCESSANDO LOTE DE {len(leads)} LEADS")
    print("🔄 " * 20)
    
    resultados = []
    
    for idx, lead in enumerate(leads, 1):
        print(f"\n\n{'─' * 80}")
        print(f"LEAD {idx}/{len(leads)}")
        print(f"{'─' * 80}")
        
        resultado = processar_lead_completo(
            nome_contato=lead['nome'],
            cargo_contato=lead['cargo'],
            empresa_nome=lead['empresa'],
            niche_empresa=lead['niche'],
            resumo_empresa=lead['resumo'],
            email_contato=lead['email'],
            website_empresa=lead.get('website', lead['empresa'].lower() + '.com.br'),
        )
        
        resultados.append(resultado)
    
    # Resumo
    print("\n\n" + "=" * 80)
    print("📊 RESUMO DO PROCESSAMENTO EM LOTE")
    print("=" * 80)
    
    sucessos = sum(1 for r in resultados if r['status'] == 'SUCESSO')
    erros = len(resultados) - sucessos
    
    print(f"\n✅ Processados com sucesso: {sucessos}/{len(resultados)}")
    print(f"❌ Erros: {erros}/{len(resultados)}")
    
    print(f"\n📋 Detalhes por Lead:\n")
    for idx, r in enumerate(resultados, 1):
        emoji = "✅" if r['status'] == 'SUCESSO' else "❌"
        print(f"{emoji} {idx}. {r['lead']['empresa']}")
        if r['produto']:
            print(f"   → Produto: {r['produto']['nome']} (score: {r['produto']['score']}/100)")
        if r['roteamento']:
            print(f"   → Remetente: {r['roteamento']['remetente']}")
        print()
    
    return resultados


# ============================================================================
# EXEMPLOS DE LEADS
# ============================================================================

EXEMPLO_LEADS = [
    {
        'nome': 'Dra. Maria Silva',
        'cargo': 'Diretora Clínica',
        'empresa': 'Clínica Dental Silva',
        'niche': 'Clínica Odontológica',
        'resumo': 'Clínica com 50 pacientes, prontuários em papel, agendamentos manuais',
        'email': 'maria@clinicasilva.com.br',
        'website': 'clinicasilva.com.br',
    },
    {
        'nome': 'João Pedro Santos',
        'cargo': 'E-commerce Manager',
        'empresa': 'FastShop Brasil',
        'niche': 'E-commerce de Eletrônicos',
        'resumo': 'Loja com 2000 SKUs, concorrência acirrada, margens pressionadas',
        'email': 'joao@fastshop.com.br',
        'website': 'fastshop.com.br',
    },
    {
        'nome': 'Prof. Dr. Carlos Silva',
        'cargo': 'Reitor',
        'empresa': 'Universidade Federal do Brasil',
        'niche': 'Instituição Educacional Superior',
        'resumo': 'Universidade com 4000 alunos, processos administrativos complexos',
        'email': 'carlos@ufb.edu.br',
        'website': 'ufb.edu.br',
    },
    {
        'nome': 'Ana Costa',
        'cargo': 'Gerente de Operações',
        'empresa': 'Fábrica de Aços Silva',
        'niche': 'Indústria de Aços',
        'resumo': 'Fábrica com 300 funcionários, logística complexa, fluxos de dados manuais',
        'email': 'ana@fabricasilva.com.br',
        'website': 'fabricasilva.com.br',
    },
    {
        'nome': 'Lucas Marques',
        'cargo': 'Personal Trainer',
        'empresa': 'FitZone Academia',
        'niche': 'Academia de Fitness e Musculação',
        'resumo': 'Academia com 500 alunos, necessidade de gestão de nutrição e treino',
        'email': 'lucas@fitzone.com.br',
        'website': 'fitzone.com.br',
    },
]


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    
    print("\n\n")
    print("🚀 " * 25)
    print("\nPIPELINE COMPLETO: Lead Classification → Email Generation → SMTP Dispatch")
    print("\n" + "🚀 " * 25)
    
    print("\n\n📊 Demonstração com 5 leads de diferentes setores:\n")
    
    # Processar lote
    resultados = processar_lote_leads(EXEMPLO_LEADS)
    
    # Análise final
    print("\n\n" + "=" * 80)
    print("🎓 ANÁLISE FINAL DO PIPELINE")
    print("=" * 80)
    
    print(f"\n✅ Fluxo Integrado:")
    print(f"   1. Lead → Product Matcher (classificação automática)")
    print(f"   2. Match Result → Email Generator (geração com AIDA)")
    print(f"   3. Produto → SMTP Dispatcher (roteamento automático)")
    print(f"   4. Email enviado via alias correto (SenseiDB, GestaoRPD, etc)")
    
    print(f"\n📈 Estatísticas:")
    
    por_produto = {}
    for r in resultados:
        if r['produto']:
            produto = r['produto']['nome']
            if produto not in por_produto:
                por_produto[produto] = 0
            por_produto[produto] += 1
    
    print(f"\n   Leads por Produto:")
    for produto, count in sorted(por_produto.items()):
        print(f"   • {produto}: {count} lead(s)")
    
    print(f"\n🔄 Próximos Steps em Produção:")
    print(f"   1. Ativar credenciais reais de Zoho Mail")
    print(f"   2. Descomentar dispatcher.disparar_email() para envio real")
    print(f"   3. Implementar retry logic para ERRO_SMTP")
    print(f"   4. Armazenar ResultadoDisparo para auditoria")
    print(f"   5. Adicionar rate limiting (não sobrecarregar Zoho)")
    print(f"   6. Integrar com queue system (async/celery)")
    
    print(f"\n📚 Documentação:")
    print(f"   • INTEGRACAO_AIDA_EMAIL.md - Email com AIDA")
    print(f"   • SMTP_DISPATCHER.md - Roteamento SMTP")
    print(f"   • PRODUCT_MATCHER.md - Classificação de produtos")
    
    print("\n\n✅ DEMO CONCLUÍDA COM SUCESSO!")
    print("=" * 80 + "\n")
