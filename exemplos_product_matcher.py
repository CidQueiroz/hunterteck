"""
Exemplos de Uso do Product Matcher na Pipeline B2B
Demonstra como integrar o classificador de produtos no workflow
"""

import logging
from services.lead_extractor.product_matcher import match_cdkteck_product
from services.lead_extractor.models import Empresa, LeadSource, LeadStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def exemplo_1_classificacao_simples():
    """
    Exemplo 1: Classificação simples de um lead
    """
    print("\n" + "="*80)
    print("EXEMPLO 1: Classificação Simples")
    print("="*80 + "\n")
    
    # Dados do lead
    niche = "Clínica Odontológica"
    resumo = "Clínica com 30 pacientes, 3 dentistas. Agendamentos manuais, " \
             "prontuários em papel. Precisa otimizar gestão administrativa."
    
    # Classificar
    resultado = match_cdkteck_product(niche, resumo)
    
    print(f"Lead: {niche}")
    print(f"Resumo: {resumo}\n")
    print(f"✅ Produto Recomendado: {resultado['produto']}")
    print(f"📊 Score de Confiança: {resultado['score_confianca']}/100 ({resultado['confianca_nivel']})")
    print(f"💡 Proposta de Valor: {resultado['proposta_valor']}\n")
    print(f"🎯 Dores Resolvidas:")
    for i, dor in enumerate(resultado['dores_resolvidas'], 1):
        print(f"   {i}. {dor}")
    print(f"\n📋 Casos de Uso:")
    for i, caso in enumerate(resultado['casos_uso'], 1):
        print(f"   {i}. {caso}")
    print(f"\n➡️  Próximos Passos: {resultado['proximos_passos']}\n")
    
    return resultado


def exemplo_2_comparacao_scores():
    """
    Exemplo 2: Comparar scores de múltiplos produtos
    """
    print("\n" + "="*80)
    print("EXEMPLO 2: Análise de Scores Comparativos")
    print("="*80 + "\n")
    
    leads = [
        {
            "niche": "Academia de Fitness",
            "resumo": "Academia com 400 alunos, 20 PTs, 5 nutricionistas. "
                      "Churn de 35%, falta acompanhamento personalizado dos alunos."
        },
        {
            "niche": "Distribuidora de Alimentos",
            "resumo": "Distribuidora com 30 rotas, 150 entregas/dia. "
                      "Ineficiência em planejamento, custos logísticos altos."
        },
        {
            "niche": "Plataforma de Cursos Online",
            "resumo": "Platform com 5000 alunos, 100 cursos. "
                      "Base de conhecimento desorganizada, FAQ manual."
        }
    ]
    
    for lead in leads:
        resultado = match_cdkteck_product(lead['niche'], lead['resumo'])
        
        print(f"\n🔹 {lead['niche'].upper()}")
        print(f"   Produto: {resultado['produto']} "
              f"(Score: {resultado['score_confianca']}/100)")
        
        # Exibir top 3 scores
        top_3 = sorted(resultado['scores_todos_produtos'].items(),
                      key=lambda x: x[1], reverse=True)[:3]
        print(f"   Ranking:")
        for i, (prod, score) in enumerate(top_3, 1):
            marca = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            print(f"      {marca} {prod}: {score}/100")
        print()


def exemplo_3_pipeline_com_match():
    """
    Exemplo 3: Integração com lead da empresa
    """
    print("\n" + "="*80)
    print("EXEMPLO 3: Integração com Objeto Empresa")
    print("="*80 + "\n")
    
    # Criar empresa fictícia
    empresa = Empresa(
        nome="TechStartup de Nutrição",
        website="www.nutritechapp.com.br",
        email="contato@nutritechapp.com.br",
        telefone="(11) 98765-4321",
        ramo="Saúde e Nutrição",
        endereco="Rua das Flores, 123",
        cidade="São Paulo",
        estado="SP",
        fonte=LeadSource.LINKEDIN,
    )
    
    descricao = "Startup de saúde digital focada em nutrição personalizada. " \
                "Oferecem plataforma de acompanhamento nutricional com IA. " \
                "Crescimento rápido, 5000 usuários ativos."
    
    # Classificar para produto
    resultado = match_cdkteck_product(
        lead_niche=empresa.ramo,
        lead_summary=descricao
    )
    
    # Exibir resultado
    print(f"Empresa: {empresa.nome}")
    print(f"Website: {empresa.website}")
    print(f"Ramo: {empresa.ramo}")
    print(f"Descrição: {descricao}\n")
    
    print(f"🎯 ANÁLISE DE PRODUTO")
    print(f"   Produto Recomendado: {resultado['produto']}")
    print(f"   Confiança: {resultado['confianca_nivel'].upper()}")
    print(f"   Score: {resultado['score_confianca']}/100")
    print(f"   Proposta de Valor: {resultado['proposta_valor']}\n")
    
    # Sugerir proposição personalizada
    if resultado['score_confianca'] >= 70:
        print(f"✨ PROPOSIÇÃO PERSONALIZADA:")
        print(f"   Olá, somos a CDKTeck. Notamos que vocês oferecem serviço de")
        print(f"   nutrição personalizada. Com {resultado['produto']}, vocês conseguem:")
        for i, dor in enumerate(resultado['dores_resolvidas'][:2], 1):
            print(f"      {i}. {dor}")
        print()
    elif resultado['score_confianca'] >= 50:
        print(f"✨ PROPOSIÇÃO PERSONALIZADA:")
        print(f"   Olá, somos a CDKTeck. Vemos potencial em usar {resultado['produto']} para:")
        for i, dor in enumerate(resultado['dores_resolvidas'][:2], 1):
            print(f"      {i}. {dor}")
        print()
    else:
        print(f"✨ Manter contato para verificar melhor encaixe do produto\n")


def exemplo_4_filtragem_por_confianca():
    """
    Exemplo 4: Filtrar leads por nível de confiança
    """
    print("\n" + "="*80)
    print("EXEMPLO 4: Filtragem por Nível de Confiança")
    print("="*80 + "\n")
    
    leads_teste = [
        ("Clínica Odontológica", "Clínica com 30 pacientes"),
        ("Academia de Ginástica", "Academia com 200 alunos, personal trainers"),
        ("Consultoria Geral", "Empresa de consultoria em negócios"),
        ("E-commerce de Eletrônicos", "Loja online com 2000 SKUs, concorrência acirrada"),
        ("Escola de Idiomas", "Escola de inglês com 150 alunos, aulas presenciais e online"),
    ]
    
    resultados = []
    for niche, resumo in leads_teste:
        resultado = match_cdkteck_product(niche, resumo)
        resultados.append((niche, resultado))
    
    # Separar por confiança
    altos = [r for r in resultados if r[1]['confianca_nivel'] == 'alta']
    medios = [r for r in resultados if r[1]['confianca_nivel'] == 'média']
    baixos = [r for r in resultados if r[1]['confianca_nivel'] == 'baixa']
    
    print(f"📊 CONFIANÇA ALTA ({len(altos)}):")
    for niche, res in altos:
        print(f"   ✅ {niche} → {res['produto']} ({res['score_confianca']}/100)")
    
    print(f"\n📊 CONFIANÇA MÉDIA ({len(medios)}):")
    for niche, res in medios:
        print(f"   ⚠️  {niche} → {res['produto']} ({res['score_confianca']}/100)")
    
    print(f"\n📊 CONFIANÇA BAIXA ({len(baixos)}):")
    for niche, res in baixos:
        print(f"   ❌ {niche} → {res['produto']} ({res['score_confianca']}/100)")
    
    print()


def exemplo_5_recomendacoes_personalizadas():
    """
    Exemplo 5: Gerar recomendações personalizadas por produto
    """
    print("\n" + "="*80)
    print("EXEMPLO 5: Recomendações Personalizadas por Email")
    print("="*80 + "\n")
    
    leads = [
        {
            "nome_empresa": "VitalClínica",
            "niche": "Clínica Multiprofissional",
            "resumo": "Clínica com 50 pacientes, gestão manual de prontuários",
            "contato": "dra.silva@vitalclinica.com.br"
        },
        {
            "nome_empresa": "FitMax",
            "niche": "Academia de Fitness",
            "resumo": "Academia com 300 alunos, dificuldade em retenção",
            "contato": "gerente@fitmaxacademia.com"
        }
    ]
    
    for lead in leads:
        resultado = match_cdkteck_product(lead['niche'], lead['resumo'])
        
        print(f"\n📧 EMAIL PERSONALIZADO para {lead['nome_empresa']}")
        print("─" * 80)
        print(f"Para: {lead['contato']}")
        print(f"Assunto: {resultado['proposta_valor']}\n")
        
        print(f"Olá,\n")
        print(f"Vimos que vocês trabalham com {lead['niche'].lower()}. "
              f"Com {resultado['produto']}, vocês conseguem:\n")
        
        for i, dor in enumerate(resultado['dores_resolvidas'], 1):
            print(f"{i}. {dor}")
        
        print(f"\nCasos de sucesso similares:")
        for i, caso in enumerate(resultado['casos_uso'], 1):
            print(f"  • {caso}")
        
        if resultado['score_confianca'] >= 80:
            print(f"\nGostaria de uma demo personalizada?\n")
        elif resultado['score_confianca'] >= 50:
            print(f"\nPodemos conversar sobre como isso se aplica ao seu caso.\n")
        else:
            print(f"\nVale conversar; vemos potencial na sua operação.\n")
        
        print("Abraços,")
        print("Time CDKTeck")
        print("─" * 80)


def exemplo_6_metricas_batch():
    """
    Exemplo 6: Processar lote e gerar métricas
    """
    print("\n" + "="*80)
    print("EXEMPLO 6: Batch Processing e Análise de Métricas")
    print("="*80 + "\n")
    
    # 20 leads fictícios
    batch_leads = [
        ("Clínica Médica", "Clínica com 50 pacientes, problemas com prontuários"),
        ("Academia", "Academia com 300 alunos, churn alto"),
        ("E-commerce", "Loja online com 2000 SKUs, concorrência alta"),
        ("Logística", "Distribuidora com 50 rotas, ineficiência operacional"),
        ("EdTech", "Plataforma com 5000 alunos, necessário base de conhecimento"),
        ("Consultoria Geral", "Consultoria em negócios gerais"),
        ("Dentista", "Consultório odontológico, 3 dentistas"),
        ("Nutricionista", "Consultório de nutrição, dietas personalizadas"),
        ("Varejo Online", "Loja online de roupas, 500+ SKUs"),
        ("Fabricante", "Indústria de componentes eletrônicos"),
        ("Call Center", "Centro de atendimento com 100 operadores"),
        ("Fitness Coach", "Personal trainer oferecendo serviços online"),
        ("Marketplace", "Marketplace de segunda mão, 100+ vendedores"),
        ("Hospital", "Pequeno hospital privado"),
        ("Startup RH", "Software de gestão de RH"),
        ("Cursos Corporativos", "Plataforma de treinamento corporativo"),
        ("Supply Chain", "Empresa de otimização de logística"),
        ("Gym Digital", "App de treino e nutrição"),
        ("Precificação Dinâmica", "Empresa que precisa otimizar preços dinamicamente"),
        ("Clínica Veterinária", "Clínica vet com 30 pacientes"),
    ]
    
    resultados = []
    produtos_count = {}
    total_score = 0
    
    print("Processando 20 leads...")
    for niche, resumo in batch_leads:
        resultado = match_cdkteck_product(niche, resumo)
        resultados.append(resultado)
        
        # Contar produto
        prod = resultado['produto']
        produtos_count[prod] = produtos_count.get(prod, 0) + 1
        total_score += resultado['score_confianca']
    
    altos = sum(1 for r in resultados if r['confianca_nivel'] == 'alta')
    medios = sum(1 for r in resultados if r['confianca_nivel'] == 'média')
    baixos = sum(1 for r in resultados if r['confianca_nivel'] == 'baixa')
    
    print("\n📊 MÉTRICAS DO BATCH:")
    print(f"   ✅ Confiança Alta: {altos} ({altos/len(resultados)*100:.1f}%)")
    print(f"   ⚠️  Confiança Média: {medios} ({medios/len(resultados)*100:.1f}%)")
    print(f"   ❌ Confiança Baixa: {baixos} ({baixos/len(resultados)*100:.1f}%)")
    print(f"   📈 Score Médio: {total_score/len(resultados):.1f}/100\n")
    
    print("📦 DISTRIBUIÇÃO POR PRODUTO:")
    for prod, count in sorted(produtos_count.items(), key=lambda x: x[1], reverse=True):
        print(f"   {prod}: {count} leads ({count/len(resultados)*100:.1f}%)")
    
    print()


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎯 EXEMPLOS DE USO: PRODUCT MATCHER CDKTECK")
    print("="*80)
    
    # Executar exemplos
    exemplo_1_classificacao_simples()
    exemplo_2_comparacao_scores()
    exemplo_3_pipeline_com_match()
    exemplo_4_filtragem_por_confianca()
    exemplo_5_recomendacoes_personalizadas()
    exemplo_6_metricas_batch()
    
    print("\n" + "="*80)
    print("✅ EXEMPLOS CONCLUÍDOS")
    print("="*80 + "\n")
