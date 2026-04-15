"""
Exemplo: Integração Completa
match_cdkteck_product + GeradorEmails com Framework AIDA

Fluxo:
1. Classificar lead para produto (match_cdkteck_product)
2. Gerar email cold outreach com AIDA (gerar_email_com_product_match)
3. Customizar com contexto adicional
"""

import logging
from services.lead_extractor.product_matcher import match_cdkteck_product
from services.lead_extractor.email_generator import GeradorEmails

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def exemplo_1_pipeline_completo():
    """
    Exemplo 1: Pipeline completo - Classificar + Gerar Email com AIDA
    """
    print("\n" + "="*80)
    print("EXEMPLO 1: Pipeline Completo (Product Match + Email AIDA)")
    print("="*80 + "\n")
    
    # PASSO 1: Classificar lead para produto
    print("📌 PASSO 1: Classificar lead para produto CDKTeck\n")
    
    match_result = match_cdkteck_product(
        lead_niche="Clínica Multiprofissional",
        lead_summary="Clínica com 50 pacientes, 5 profissionais. Prontuários em papel, "
                     "agendamentos manuais causam atrasos. RH with folha complexa. "
                     "Necessário sistema de gestão administrativo integrado."
    )
    
    print(f"✅ Lead classificado: {match_result['produto']}")
    print(f"   Score de Confiança: {match_result['score_confianca']}/100 ({match_result['confianca_nivel']})")
    print(f"   Proposta de Valor: {match_result['proposta_valor']}\n")
    
    # PASSO 2: Gerar email com framework AIDA usando product match
    print("📧 PASSO 2: Gerar email cold outreach com Framework AIDA\n")
    
    gerador = GeradorEmails(usar_openai=False)  # Usar False para teste (sem API key)
    
    # Método NOVO e RECOMENDADO - Com integração Product Match
    email = gerador.gerar_email_com_product_match(
        nome_pessoa="Dra. Maria Silva",
        cargo_pessoa="Diretora Clínica",
        empresa_nome="Clínica Dental Silva",
        setor_empresa="Saúde - Odontologia",
        website_empresa="clinicadental.silva.com.br",
        product_match_result=match_result,  # Passa o resultado do product matcher
        usar_ia=False,  # Para este teste, usar template
        tamanho_empresa="50-100",
        vendedor_nome="João SDR",
        vendedor_email="joao@cdkteck.com"
    )
    
    print(f"✅ Email gerado com sucesso!")
    print(f"   Assunto: {email.assunto}")
    print(f"   Produto: {email.contexto.get('produto')}")
    print(f"   Gerado por: {email.gerado_por}\n")
    
    # PASSO 3: Exibir email
    print("📝 CONTEÚDO DO EMAIL (com AIDA + Product Match):\n")
    print("─" * 80)
    print(f"Para: {email.destinatario_email}")
    print(f"Assunto: {email.assunto}\n")
    print(email.corpo)
    print("─" * 80 + "\n")
    
    return match_result, email


def exemplo_2_multiplos_leads():
    """
    Exemplo 2: Processar múltiplos leads em batch
    Classificar → Gerar Emails com AIDA automaticamente
    """
    print("\n" + "="*80)
    print("EXEMPLO 2: Batch Processing - Múltiplos Leads")
    print("="*80 + "\n")
    
    leads = [
        {
            "nome": "Dra. Silva",
            "cargo": "Diretora Clínica",
            "empresa": "Clínica Dental Silva",
            "niche": "Clínica Multiprofissional",
            "summary": "Clínica com 50 pacientes, prontuários manuais, agendamentos caóticos"
        },
        {
            "nome": "Gerente Fitness",
            "cargo": "Gerente de Operações",
            "empresa": "FitZone Academia",
            "niche": "Academia de Fitness",
            "summary": "Academia com 300 alunos, 20 PTs, churn de 35%, falta acompanhamento"
        },
        {
            "nome": "CEO Ecommerce",
            "cargo": "CEO",
            "empresa": "EcommerceFast",
            "niche": "E-commerce de Moda",
            "summary": "Loja online com 3000 SKUs, concorrência acirrada, margens baixas"
        }
    ]
    
    gerador = GeradorEmails(usar_openai=False)
    
    print(f"Processando {len(leads)} leads...\n")
    
    for i, lead in enumerate(leads, 1):
        print(f"Lead {i}: {lead['empresa']}")
        print("─" * 80)
        
        # Classificar
        match_result = match_cdkteck_product(
            lead_niche=lead['niche'],
            lead_summary=lead['summary']
        )
        
        # Gerar email com product match
        email = gerador.gerar_email_com_product_match(
            nome_pessoa=lead['nome'],
            cargo_pessoa=lead['cargo'],
            empresa_nome=lead['empresa'],
            setor_empresa=lead['niche'],
            website_empresa=lead['empresa'].lower().replace(' ', '') + ".com.br",
            product_match_result=match_result,
            usar_ia=False
        )
        
        print(f"✅ Produto: {match_result['produto']} (Score: {match_result['score_confianca']}/100)")
        print(f"   Email Assunto: {email.assunto}")
        print(f"   Confiança: {match_result['confianca_nivel']}")
        print()
    
    print("="*80)
    print(f"✅ {len(leads)} emails processados com sucesso!")
    print("="*80)


def exemplo_3_fluxo_com_ia():
    """
    Exemplo 3: Fluxo COMPLETO com IA (requer OpenAI API key)
    
    Este é o fluxo ideal em produção:
    1. Product Matcher identifica melhor fit
    2. Email Generator cria cold email com AIDA + proposta específica
    3. Output é um email pronto para enviar
    """
    print("\n" + "="*80)
    print("EXEMPLO 3: Fluxo com IA (GPT-4)")
    print("="*80 + "\n")
    
    print("ℹ️  Este exemplo mostra o fluxo com IA habilitada.")
    print("   Em produção, passe a OpenAI API key:\n")
    
    print("```python")
    print("from services.lead_extractor.product_matcher import match_cdkteck_product")
    print("from services.lead_extractor.email_generator import GeradorEmails")
    print("import os\n")
    
    print("# Classificar lead")
    print('match_result = match_cdkteck_product(')
    print('    lead_niche="Clínica",')
    print('    lead_summary="50 pacientes, prontuários manuais..."')
    print(')\n')
    
    print("# Inicializar gerador COM IA")
    print('gerador = GeradorEmails(')
    print('    usar_openai=True,')
    print('    openai_api_key=os.getenv("OPENAI_API_KEY")')
    print(')\n')
    
    print("# Gerar email com framework AIDA + Product Match")
    print('email = gerador.gerar_email_com_product_match(')
    print('    nome_pessoa="Dra. Maria",')
    print('    cargo_pessoa="Diretora Clínica",')
    print('    empresa_nome="Clínica Silva",')
    print('    setor_empresa="Saúde - Odontologia",')
    print('    website_empresa="clinicasilva.com.br",')
    print('    product_match_result=match_result,')
    print('    usar_ia=True  # Usar GPT-4!')
    print(')\n')
    
    print("# Email pronto para enviar com:")
    print("# • Framework AIDA bem estruturado")
    print("# • Dor específica do setor abordada")
    print("# • Produto certo (do product matcher)")
    print("# • Proposta de valor customizada")
    print("# • CTA simples (vídeo de 2 minutos)")
    print("print(email.corpo)")
    print("```\n")
    
    print("="*80)
    print("Para ativar IA em produção, configure:")
    print("  export OPENAI_API_KEY='sua-chave-aqui'")
    print("="*80)


def exemplo_4_analise_aida():
    """
    Exemplo 4: Mostrar os componentes AIDA do email gerado
    """
    print("\n" + "="*80)
    print("EXEMPLO 4: Análise Framework AIDA")
    print("="*80 + "\n")
    
    # Classificar
    match_result = match_cdkteck_product(
        lead_niche="Clínica Odontológica",
        lead_summary="Clínica com 30 pacientes, prontuários em papel"
    )
    
    # Gerar email
    gerador = GeradorEmails(usar_openai=False)
    email = gerador.gerar_email_com_product_match(
        nome_pessoa="Dr. João",
        cargo_pessoa="Diretor",
        empresa_nome="Clínica DentalPro",
        setor_empresa="Odontologia",
        website_empresa="dentalpro.com.br",
        product_match_result=match_result,
        usar_ia=False
    )
    
    # Análise
    print("📧 COMPONENTES DO EMAIL COM FRAMEWORK AIDA:\n")
    
    print("1️⃣  ATENÇÃO (Hook inicial)")
    print("   └─ Deve captar atenção sem mencionar tecnologia")
    print("   └─ Pode usar: estatística, pergunta instigante, observação sobre setor\n")
    
    print("2️⃣  INTERESSE (Demonstrar entendimento)")
    print("   └─ Mostrar que entendo o PROBLEMA do setor")
    print("   └─ Referências específicas a desafios do negócio\n")
    
    print("3️⃣  DESEJO (Apresentar solução)")
    print("   └─ Mostrar RESULTADO, não tecnologia")
    print("   └─ Foco em: tempo economizado, custos reduzidos, vantagem competitiva")
    print("   └─ Produto específico: GestaoRPD")
    print("   └─ Proposta: Gestão completa de clínicas com prontuário eletrônico\n")
    
    print("4️⃣  AÇÃO (CTA simples)")
    print("   └─ Oferta clara e direto: vídeo de 2 minutos")
    print("   └─ Reduz fricção (não pede reunião, pede apenas assistir vídeo)\n")
    
    print("─" * 80)
    print("📊 EMAIL GERADO:")
    print("─" * 80)
    print(f"Assunto: {email.assunto}\n")
    print(email.corpo)
    print("─" * 80 + "\n")
    
    print("✅ O email segue o framework AIDA perfeitamente integrado com:")
    print(f"   • Produto identificado: {match_result['produto']}")
    print(f"   • Score de fit: {match_result['score_confianca']}/100")
    print(f"   • Proposta específica: {match_result['proposta_valor']}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎯 INTEGRAÇÃO COMPLETA: Product Matcher + Email Generator com AIDA")
    print("="*80)
    
    # Executar exemplos
    exemplo_1_pipeline_completo()
    exemplo_2_multiplos_leads()
    exemplo_3_fluxo_com_ia()
    exemplo_4_analise_aida()
    
    print("\n" + "="*80)
    print("✅ EXEMPLOS CONCLUÍDOS!")
    print("="*80)
    print("\n🚀 Para usar em PRODUÇÃO com IA habilitada:")
    print("   1. Configure OPENAI_API_KEY")
    print("   2. Use usar_openai=True no GeradorEmails")
    print("   3. Use usar_ia=True em gerar_email_com_product_match()\n")
