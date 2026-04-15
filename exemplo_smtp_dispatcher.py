"""
Exemplo Completo: SMTP Dispatcher com Roteamento Dinâmico por Produto
Demonstra integração entre Product Matcher → Email Generator → SMTP Dispatcher
"""

from services.lead_extractor import (
    DispachadorSMTPProdutos,
    ConfiguracaoSMTP,
    MapeamentoAliases,
    match_cdkteck_product,
)
from services.lead_extractor.email_generator import GeradorEmails, ContextoEmail
import json
import os


# ============================================================================
# CONFIGURAÇÃO ZOHO SMTP - Em produção, usar variáveis de ambiente
# ============================================================================

def obter_config_zoho() -> ConfiguracaoSMTP:
    """Obtém configuração Zoho Mail a partir de variáveis de ambiente."""
    
    # Em produção, estas viriam de .env
    return ConfiguracaoSMTP(
        host="smtp.zoho.com",
        porta=int(os.getenv("ZOHO_SMTP_PORTA", "587")),  # 587 (TLS) ou 465 (SSL)
        usar_tls=os.getenv("ZOHO_USAR_TLS", "true").lower() == "true",
        email_admin=os.getenv("ZOHO_EMAIL_ADMIN", "admin@cdkteck.com.br"),
        senha_admin=os.getenv("ZOHO_SENHA_ADMIN", "sua_senha_aqui"),
        timeout_conexao=30,
        tentativas_reconexao=3,
    )


# ============================================================================
# EXEMPLO 1: Roter Email por Produto (Básico)
# ============================================================================

def exemplo_1_roteamento_basico():
    """
    Exemplo básico: Tomar produto e rotear para alias correto.
    """
    print("=" * 80)
    print("EXEMPLO 1: Roteamento Básico de Email por Produto")
    print("=" * 80)
    
    # Criar mapeamento de aliases
    aliases = MapeamentoAliases()
    
    # Testar cada produto
    produtos_teste = ["SenseiDB", "GestaoRPD", "PapoDados", "CaçaPreço", "BioCoach"]
    
    print("\n📧 Mapeamento de Produtos → Aliases:\n")
    for produto in produtos_teste:
        email_alias = aliases.obter_alias(produto)
        valido, msg = aliases.validar_alias(produto)
        emoji = "✅" if valido else "❌"
        print(f"{emoji} {produto:15} → {email_alias:30} | {msg}")
    
    # Testar fallback
    print(f"\nℹ️  Email padrão (fallback): {aliases.EMAIL_PADRAO}")


# ============================================================================
# EXEMPLO 2: Integração Completa (Product Match → Email → SMTP)
# ============================================================================

def exemplo_2_integração_completa():
    """
    Exemplo completo simulado (sem enviar realmente):
    1. Classificar lead com match_cdkteck_product
    2. Gerar email com GeradorEmails
    3. Simular disparo com DispachadorSMTPProdutos
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 2: Integração Completa (Product Match → Email → SMTP)")
    print("=" * 80)
    
    # PASSO 1: Classificar lead
    print("\n[PASSO 1] Classificando lead com match_cdkteck_product...")
    
    lead_niche = "Clínica Odontológica com 50 pacientes"
    lead_summary = "Clínica na zona sul, próspera, prontuários em papel, agendamentos manuais"
    
    match_result = match_cdkteck_product(lead_niche, lead_summary)
    
    print(f"✅ Lead classificado para: {match_result['produto']}")
    print(f"   Score: {match_result['score_confianca']}/100")
    print(f"   Proposta de Valor: {match_result['proposta_valor']}")
    
    # PASSO 2: Gerar email
    print("\n[PASSO 2] Gerando email personalizado...")
    
    gerador = GeradorEmails(usar_openai=False)  # Usar template para exemplo
    
    contexto = ContextoEmail(
        nome_pessoa="Dra. Maria Silva",
        cargo_pessoa="Diretora Clínica",
        empresa_nome="Clínica Dental Silva",
        setor_empresa="Odontologia",
        website_empresa="clinicasilva.com.br",
        vendedor_nome="João SDR",
        vendedor_email="joao@cdkteck.com.br",
        product_match_result=match_result,
    )
    
    email = gerador.gerar_email_com_product_match(
        nome_pessoa=contexto.nome_pessoa,
        cargo_pessoa=contexto.cargo_pessoa,
        empresa_nome=contexto.empresa_nome,
        setor_empresa=contexto.setor_empresa,
        website_empresa=contexto.website_empresa,
        product_match_result=match_result,
        usar_ia=False,  # Template
    )
    
    print(f"✅ Email gerado!")
    print(f"   Assunto: {email.assunto}")
    print(f"   Tipo: {email.tipo.value}")
    print(f"   Gerado por: {email.gerado_por}")
    
    # PASSO 3: Simular disparo (sem realmente enviar)
    print("\n[PASSO 3] Simulando disparo com roteamento de produto...")
    
    # Obter alias para o produto
    aliases = MapeamentoAliases()
    remetente = aliases.obter_alias(match_result['produto'])
    
    print(f"✅ Roteamento determinado:")
    print(f"   Produto: {match_result['produto']}")
    print(f"   Remetente: {remetente}")
    print(f"   Destinatário: {contexto.nome_pessoa} <maria@clinicasilva.com.br>")
    
    print(f"\n[SIMULAÇÃO] Email seria enviado com headers:")
    print(f"   From: {remetente}")
    print(f"   To: maria@clinicasilva.com.br")
    print(f"   Subject: {email.assunto}")
    
    return {
        'produto': match_result['produto'],
        'remetente': remetente,
        'destinatario': 'maria@clinicasilva.com.br',
        'assunto': email.assunto,
        'email': email,
    }


# ============================================================================
# EXEMPLO 3: Batch Processing com Múltiplos Produtos
# ============================================================================

def exemplo_3_batch_processing():
    """
    Exemplo de processamento em lote com diferentes produtos.
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 3: Batch Processing - Múltiplos Leads com Diferentes Produtos")
    print("=" * 80)
    
    # Leads de teste (cada um de um setor diferente para ativar produtos diferentes)
    leads = [
        {
            "nome": "Dr. João",
            "cargo": "Diretor TCO",
            "empresa": "Hospital XYZ",
            "niche": "Hospital com 500 leitos",
            "summary": "Hospital em expansão, 200 médicos, sistema de RH inadequado",
            "email": "joao@hospitalxyz.com.br",
        },
        {
            "nome": "Maria",
            "cargo": "E-commerce Manager",
            "empresa": "FastShop Brasil",
            "niche": "E-commerce de Eletrônicos",
            "summary": "Loja com 2000 SKUs, concorrência acirrada, margens pressionadas",
            "email": "maria@fastshop.com.br",
        },
        {
            "nome": "Pedro",
            "cargo": "Gerente de Operações",
            "empresa": "Fábrica de Aços Silva",
            "niche": "Indústria de Aços",
            "summary": "Fábrica com 300 funcionários, logística complexa, fluxos de dados manuais",
            "email": "pedro@fabricasilva.com.br",
        },
    ]
    
    print(f"\n📧 Processando {len(leads)} leads...\n")
    
    aliases = MapeamentoAliases()
    resultados = []
    
    for idx, lead in enumerate(leads, 1):
        print(f"[{idx}/{len(leads)}] {lead['empresa']}")
        
        # Classificar
        match = match_cdkteck_product(lead['niche'], lead['summary'])
        
        # Obter alias
        remetente = aliases.obter_alias(match['produto'])
        
        resultado = {
            "empresa": lead['empresa'],
            "contato": lead['nome'],
            "produto": match['produto'],
            "score": match['score_confianca'],
            "remetente": remetente,
            "destinatario": lead['email'],
        }
        
        print(f"   ✅ {match['produto']} (score: {match['score_confianca']}/100)")
        print(f"   📧 Remetente: {remetente}")
        print(f"   📮 Para: {lead['email']}\n")
        
        resultados.append(resultado)
    
    # Resumo
    print("=" * 80)
    print("📊 RESUMO DO BATCH\n")
    
    for r in resultados:
        print(f"{r['empresa']:25} → {r['produto']:15} (via {r['remetente']})")
    
    return resultados


# ============================================================================
# EXEMPLO 4: Visualização de Estrutura SMTP (Educational)
# ============================================================================

def exemplo_4_estrutura_smtp():
    """
    Mostra a estrutura e validações da configuração SMTP.
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 4: Estrutura e Validações SMTP")
    print("=" * 80)
    
    print("\n📋 Configuração SMTP Zoho:\n")
    
    config = ConfiguracaoSMTP(
        host="smtp.zoho.com",
        porta=587,  # TLS
        usar_tls=True,
        email_admin="admin@cdkteck.com.br",
        senha_admin="***redacted***",
        timeout_conexao=30,
        tentativas_reconexao=3,
    )
    
    print(f"Host: {config.host}")
    print(f"Porta: {config.porta} ({'TLS' if config.usar_tls else 'SSL'})")
    print(f"Email Admin: {config.email_admin}")
    print(f"Timeout: {config.timeout_conexao}s")
    print(f"Tentativas de Reconexão: {config.tentativas_reconexao}")
    
    # Validar
    valido = config.validar()
    print(f"\n✅ Configuração válida: {valido}")
    
    # Mostrar statuses possíveis
    print("\n📌 Status de Disparo Possíveis:\n")
    from services.lead_extractor import StatusDisparo
    
    for status in StatusDisparo:
        print(f"   • {status.value:20} - {status.name}")
    
    print("\n💡 Dica: Em caso de erro, verifique:")
    print("   • ZOHO_EMAIL_ADMIN tem permissão para usar alias?")
    print("   • Alias está cadastrado no Zoho Mail Admin?")
    print("   • Status ERRO_ALIAS indica problema com o remetente")


# ============================================================================
# EXEMPLO 5: Fluxo de Auditoria (Logs + JSON)
# ============================================================================

def exemplo_5_auditoria():
    """
    Mostra como ResultadoDisparo pode ser usado para auditoria.
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 5: Auditoria - Convertendo ResultadoDisparo para JSON")
    print("=" * 80)
    
    from services.lead_extractor import ResultadoDisparo, StatusDisparo
    from datetime import datetime
    
    # Simular um resultado positivo
    resultado_sucesso = ResultadoDisparo(
        sucesso=True,
        status=StatusDisparo.ENVIADO,
        destinatario="maria@clinicasilva.com.br",
        remetente="gestaorpd@cdkteck.com.br",
        produto_selecionado="GestaoRPD",
        mensagem="Email enviado com sucesso via alias 'gestaorpd@cdkteck.com.br'",
        tempo_execucao_ms=245.3,
    )
    
    # Simular um resultado com erro
    resultado_erro = ResultadoDisparo(
        sucesso=False,
        status=StatusDisparo.ERRO_ALIAS,
        destinatario="joao@hospitalxyz.com.br",
        remetente="desconhecido@cdkteck.com.br",
        produto_selecionado="ProdutoInexistente",
        mensagem="Alias 'desconhecido@cdkteck.com.br' não está mapeado",
        tempo_execucao_ms=150.2,
        erro_detalhado="Produto não reconhecido no catálogo",
    )
    
    print("\n✅ Resultado com Sucesso:\n")
    print(json.dumps(resultado_sucesso.to_dict(), indent=2, ensure_ascii=False))
    
    print("\n❌ Resultado com Erro:\n")
    print(json.dumps(resultado_erro.to_dict(), indent=2, ensure_ascii=False))
    
    print("\n💾 Estes JSONs podem ser armazenados para:")
    print("   • Auditoria de envios")
    print("   • Análise de problemas")
    print("   • Integração com analytics")
    print("   • Conformidade GDPR/LGPD")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("🚀 " * 20)
    print("EXEMPLOS: SMTP Dispatcher com Roteamento Dinâmico por Produto")
    print("🚀 " * 20)
    
    # Executar exemplos
    exemplo_1_roteamento_basico()
    exemplo_2_integração_completa()
    exemplo_3_batch_processing()
    exemplo_4_estrutura_smtp()
    exemplo_5_auditoria()
    
    print("\n" + "=" * 80)
    print("✅ TODOS OS EXEMPLOS CONCLUÍDOS")
    print("=" * 80)
    
    print("\n📚 Próximos Passos:")
    print("   1. Configure ZOHO_* variáveis de ambiente")
    print("   2. Use DispachadorSMTPProdutos em seu pipeline")
    print("   3. Monitore StatusDisparo para erros")
    print("   4. Implemente retry logic para ERRO_SMTP")
    print("   5. Archive ResultadoDisparo para auditoria")
    
    print("\n📖 Documentação:") 
    print("   • SMTP_DISPATCHER.md (criar)")
    print("   • Integração com email_generator.py")
    print("   • Configuração Zoho Mail Admin")
    print("\n")
