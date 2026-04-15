"""
Exemplo de Integração: Product Matcher + Orchestrador
Mostra como adicionar classificação de produtos ao pipeline completo.
"""

from services.lead_extractor.product_matcher import match_cdkteck_product
from services.lead_extractor.models import Empresa, LeadSource, LeadStatus
from services.lead_extractor.email_generator import GeradorEmails, ContextoEmail, TipoEmail
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class PessoaSimples:
    """Dados simples de uma pessoa para envio de email."""
    nome: str = "Gerente de Projetos"
    email: str = "gerente@company.com.br"
    titulo: str = "Project Manager"
    linkedin_url: Optional[str] = None
    confianca: float = 0.85


def pipeline_com_product_matching():
    """
    Pipeline B2B com classificação inteligente de produtos.
    
    Fluxo:
    1. Empresa coletada do lead extractor
    2. Classificar para produto CDKTeck
    3. Enriquecer contexto com proposta de valor do produto
    4. Gerar email personalizado com produto recomendado
    """
    
    # PASSO 1: Simular lead extraído do pipeline
    print("="*80)
    print("PIPELINE COM PRODUCT MATCHING")
    print("="*80 + "\n")
    
    empresa = Empresa(
        nome="TechVision Consultoria",
        website="www.techvision.com.br",
        email="contato@techvision.com.br",
        telefone="(21) 3456-7890",
        ramo="Consultoria de TI",
        endereco="Av. Paulista, 1000",
        cidade="São Paulo",
        estado="SP",
        fonte=LeadSource.LINKEDIN,
        status=LeadStatus.NOVO
    )
    
    descricao_lead = """
    Consultoria de TI especializada em transformação digital. 
    Atua em múltiplas indústrias. Tem clientes em educação, varejo e manufacturing.
    Busca soluções escaláveis para seus clientes.
    """
    
    print(f"📌 LEAD COLETADO")
    print(f"   Empresa: {empresa.nome}")
    print(f"   Setor: {empresa.ramo}")
    print(f"   URL: {empresa.website}")
    print(f"   Descrição: {descricao_lead.strip()}\n")
    
    # PASSO 2: Classificar para produto CDKTeck
    print("🔍 ANALISANDO PRODUTO IDEAL...\n")
    
    match_result = match_cdkteck_product(
        lead_niche=empresa.ramo,
        lead_summary=descricao_lead
    )
    
    print(f"✅ CLASSIFICAÇÃO REALIZADA")
    print(f"   Produto: {match_result['produto']}")
    print(f"   Score de Confiança: {match_result['score_confianca']}/100 ({match_result['confianca_nivel']})")
    print(f"   Proposta de Valor: {match_result['proposta_valor']}\n")
    
    print(f"🎯 DORES RESOLVIDAS:")
    for i, dor in enumerate(match_result['dores_resolvidas'], 1):
        print(f"   {i}. {dor}")
    print()
    
    print(f"📋 RANKING DE TODOS OS PRODUTOS:")
    for produto, score in sorted(match_result['scores_todos_produtos'].items(),
                                 key=lambda x: x[1], reverse=True):
        marca = "🥇" if score == max(match_result['scores_todos_produtos'].values()) else "  "
        print(f"   {marca} {produto}: {score}/100")
    print()
    
    # PASSO 3: Preparar contexto para email com produto
    print("📧 PREPARANDO EMAIL PERSONALIZADO COM PRODUTO...\n")
    
    # Simular dados de pessoa para envio
    pessoa = PessoaSimples(
        nome="Gerente de Projetos TechVision",
        email="gerente@techvision.com.br",
        titulo="Project Manager"
    )
    
    # PASSO 4: Gerar email contextualizado
    print(f"📝 EMAIL PERSONALIZADO")
    print("─" * 80)
    print(f"Para: {pessoa.email}")
    print(f"Assunto: {match_result['proposta_valor']}\n")
    print("""Olá Gerente de Projetos,

Somos a CDKTeck. Após analisar a TechVision Consultoria, identificamos que vocês 
poderiam se beneficiar muito do nosso ${}, que é especializado em:
""".replace("${}", match_result['produto']))
    
    for i, dor in enumerate(match_result['dores_resolvidas'][:3], 1):
        print(f"{i}. {dor}")
    
    print("""
Vemos vocês trabalhando em indústrias variadas (educação, varejo, manufacturing).
Cada uma dessas indústrias tem desafios únicos que o {} resolve perfeitamente.
""".replace("{}", match_result['produto']))
    
    print("Exemplos de como estamos ajudando:")
    for i, caso in enumerate(match_result['casos_uso'][:2], 1):
        print(f"  • {caso}")
    
    if match_result['confianca_nivel'] == 'alta':
        print("\nGostaria de uma demo personalizada mostrando como isso funciona para seu caso?")
    else:
        print("\nVale conversar para entender melhor seu contexto e como podemos ajudar.")
    
    print("\nAbraços,")
    print("Time CDKTeck")
    print("─" * 80)
    print()
    
    # PASSO 5: Decisões automáticas baseadas em confiança
    print("⚙️  DECISÕES AUTOMÁTICAS\n")
    
    if match_result['confianca_nivel'] == 'alta':
        print("✅ Confiança ALTA - Automação segura:")
        print("   • Enviar email imediatamente")
        print("   • Agendar follow-up em 3 dias")
        print("   • Não requer revisão manual")
        print("   • Ação: ENVIAR_AUTOMATICAMENTE")
    
    elif match_result['confianca_nivel'] == 'média':
        print("⚠️  Confiança MÉDIA - Validação recomendada:")
        print("   • Preparar email (não enviar ainda)")
        print("   • Aguardar revisão do consultor")
        print("   • Possível ajuste de messaging")
        print("   • Ação: ENVIAR_PARA_REVISAO")
    
    else:
        print("❌ Confiança BAIXA - Revisão obrigatória:")
        print("   • Classificação incerta")
        print("   • Requer análise manual")
        print("   • Possível reclassificação")
        print("   • Ação: ESCALACAO_PARA_CONSULTOR")
    
    print("\n" + "="*80)
    print("✅ PIPELINE COM PRODUCT MATCHING CONCLUÍDO")
    print("="*80 + "\n")
    
    return match_result


def pipeline_batch_com_matching():
    """
    Exemplo de batch processing com product matching.
    Processa múltiplos leads e agrupa por confiança.
    """
    print("\n" + "="*80)
    print("BATCH PROCESSING COM PRODUCT MATCHING")
    print("="*80 + "\n")
    
    # Dados fictícios de 10 leads
    leads = [
        {
            "nome": "CliniBem",
            "ramo": "Clínica Dentária",
            "desc": "Clínica com 8 dentistas, agendamentos manuais, prontuários em papel"
        },
        {
            "nome": "FitZone Academia",
            "ramo": "Academia de Fitness",
            "desc": "Academia com 500 alunos, dificuldade em acompanhamento individual"
        },
        {
            "nome": "EcommerceFast",
            "ramo": "E-commerce de Moda",
            "desc": "Loja online com 3000 SKUs, concorrência acirrada, margens baixas"
        },
        {
            "nome": "IndustriaXYZ",
            "ramo": "Manufatura",
            "desc": "Fábrica de componentes, 100+ rotas de distribuição, custos altos"
        },
        {
            "nome": "EdPlatform",
            "ramo": "Educação Online",
            "desc": "Plataforma com 20k alunos, necessário base de conhecimento centralizada"
        },
        {
            "nome": "Consultoria ABC",
            "ramo": "Consultoria",
            "desc": "Consultoria geral, oferece serviços em múltiplas áreas"
        },
    ]
    
    print("Processando {} leads...\n".format(len(leads)))
    
    resultados = []
    for lead in leads:
        resultado = match_cdkteck_product(lead['ramo'], lead['desc'])
        resultados.append({
            'empresa': lead['nome'],
            'ramo': lead['ramo'],
            'resultado': resultado
        })
    
    # Agrupar por confiança
    altos = [r for r in resultados if r['resultado']['confianca_nivel'] == 'alta']
    medios = [r for r in resultados if r['resultado']['confianca_nivel'] == 'média']
    baixos = [r for r in resultados if r['resultado']['confianca_nivel'] == 'baixa']
    
    print("📊 RESUMO DO PROCESSAMENTO\n")
    print(f"✅ Confiança ALTA ({len(altos)}):")
    for r in altos:
        print(f"   {r['empresa']:25} → {r['resultado']['produto']:12} ({r['resultado']['score_confianca']:.0f}/100)")
    
    print(f"\n⚠️  Confiança MÉDIA ({len(medios)}):")
    for r in medios:
        print(f"   {r['empresa']:25} → {r['resultado']['produto']:12} ({r['resultado']['score_confianca']:.0f}/100)")
    
    print(f"\n❌ Confiança BAIXA ({len(baixos)}):")
    for r in baixos:
        print(f"   {r['empresa']:25} → {r['resultado']['produto']:12} ({r['resultado']['score_confianca']:.0f}/100)")
    
    # Análise de produtos
    print(f"\n📦 DISTRIBUIÇÃO POR PRODUTO:")
    produtos_count = {}
    for r in resultados:
        prod = r['resultado']['produto']
        produtos_count[prod] = produtos_count.get(prod, 0) + 1
    
    for prod, count in sorted(produtos_count.items(), key=lambda x: x[1], reverse=True):
        print(f"   {prod:15} {count} leads ({count/len(resultados)*100:.0f}%)")
    
    # Score médio
    score_medio = sum(r['resultado']['score_confianca'] for r in resultados) / len(resultados)
    print(f"\n📈 Score Médio de Confiança: {score_medio:.1f}/100")
    
    print("\n" + "="*80)
    print("✅ BATCH PROCESSING CONCLUÍDO")
    print("="*80 + "\n")
    
    return resultados


if __name__ == "__main__":
    # Executar pipeline com product matching
    resultado1 = pipeline_com_product_matching()
    
    # Executar batch processing
    resultado2 = pipeline_batch_com_matching()
    
    print("\n🎯 INTEGRAÇÃO COMPLETA COM SUCESSO!")
