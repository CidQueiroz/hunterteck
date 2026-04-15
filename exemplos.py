"""
Script de teste e demonstração do microsserviço de extração de leads.
Exemplos práticos de uso para diferentes cenários.
"""

import sys
from pathlib import Path

# Adicionar o diretório do módulo ao path
sys.path.insert(0, str(Path(__file__).parent))

from services.lead_extractor.main import PipelineExtracao
from services.lead_extractor.models import LeadStatus
from services.lead_extractor.database import DatabaseConnection
import json
from datetime import datetime


def exemplo_1_extracao_basica():
    """Exemplo 1: Extração básica com API demo (sem custos)."""
    print("\n" + "="*80)
    print("EXEMPLO 1: EXTRAÇÃO BÁSICA COM API DEMO")
    print("="*80)
    
    pipeline = PipelineExtracao()
    
    # Extrair dados de restaurantes
    print("\n📍 Buscando restaurantes em São Paulo...")
    restaurantes = pipeline.extrair_com_api_demo(
        ramo="restaurantes",
        cidade="São Paulo",
        estado="SP"
    )
    
    print(f"✅ {len(restaurantes)} restaurantes encontrados\n")
    
    for i, restaurante in enumerate(restaurantes[:3], 1):
        print(f"{i}. {restaurante.nome}")
        print(f"   🌐 {restaurante.website}")
        print(f"   📧 {restaurante.email}")
        print(f"   📱 {restaurante.telefone}\n")
    
    # Persistir dados
    print("💾 Persistindo dados no SQLite...")
    resultado = pipeline.persistir_leads(restaurantes)
    print(f"✅ {resultado['mensagem']}\n")
    
    return restaurantes


def exemplo_2_multiplas_extraçoes():
    """Exemplo 2: Múltiplas extrações sequenciais com agregação."""
    print("\n" + "="*80)
    print("EXEMPLO 2: MÚLTIPLAS EXTRAÇÕES E AGREGAÇÃO")
    print("="*80)
    
    pipeline = PipelineExtracao()
    
    # Extrair de múltiplas cidades e ramos
    buscas = [
        ("restaurantes", "Rio de Janeiro", "RJ"),
        ("lojas", "Belo Horizonte", "MG"),
        ("lojas", "São Paulo", "SP"),
    ]
    
    total_leads = 0
    
    for ramo, cidade, estado in buscas:
        print(f"\n📍 {ramo.upper()} em {cidade}, {estado}")
        leads = pipeline.extrair_com_api_demo(ramo, cidade, estado)
        resultado = pipeline.persistir_leads(leads)
        total_leads += resultado['sucesso']
        print(f"   ✅ {len(leads)} leads processados")
    
    print(f"\n📊 TOTAL AGREGADO: {total_leads} leads persistidos")


def exemplo_3_web_scraping_simulado():
    """Exemplo 3: Web scraping com seletores customizados."""
    print("\n" + "="*80)
    print("EXEMPLO 3: WEB SCRAPING (ESTRUTURA PREPARADA)")
    print("="*80)
    
    print("\nEste exemplo mostra como configurar Web Scraping customizado:")
    print("(Aguardando URL e seletores válidos para executar)\n")
    
    seletores_exemplo = {
        'elemento': '.business-card',           # Container principal
        'nome': '.business-name',               # Nome da empresa
        'website': 'a.business-website',        # Link
        'email': '.business-email',             # Email
        'telefone': '.business-phone',          # Telefone
        'endereco': '.business-address'         # Endereço
    }
    
    print("Estrutura de seletores CSS:")
    print(json.dumps(seletores_exemplo, indent=2))
    print("\n💡 Próximos passos:")
    print("   1. Identificar URL com dados de empresas")
    print("   2. Usar inspector do navegador para encontrar os seletores CSS")
    print("   3. Chamar pipeline.extrair_com_web_scraping() com seletores")


def exemplo_4_consultas_database():
    """Exemplo 4: Consultas e relatórios do banco de dados."""
    print("\n" + "="*80)
    print("EXEMPLO 4: CONSULTAS E RELATÓRIOS")
    print("="*80)
    
    pipeline = PipelineExtracao()
    
    # Primeiro, inserir alguns dados
    print("\n📝 Populando base com dados de exemplo...")
    for i in range(1, 4):
        leads = pipeline.extrair_com_api_demo(
            ramo="lojas" if i % 2 == 0 else "restaurantes",
            cidade="São Paulo" if i == 1 else "Rio de Janeiro",
            estado="SP" if i == 1 else "RJ"
        )
        pipeline.persistir_leads(leads)
    
    # Obter estatísticas
    print("\n📊 ESTATÍSTICAS GERAIS:")
    print("-" * 80)
    stats = pipeline.obter_estatisticas()
    
    print(f"\n🏢 Total de Empresas: {stats['total_empresas']}")
    
    print(f"\n📈 Por Status:")
    for status, count in stats['por_status'].items():
        print(f"   - {status}: {count}")
    
    print(f"\n🌍 Top Cidades:")
    for cidade, count in sorted(stats['por_cidade'].items(), key=lambda x: x[1], reverse=True):
        print(f"   - {cidade}: {count} leads")
    
    print(f"\n🏷️ Por Setor:")
    for ramo, count in sorted(stats['por_ramo'].items(), key=lambda x: x[1], reverse=True):
        print(f"   - {ramo}: {count} leads")
    
    # Listar leads recentes
    print(f"\n📅 LEADS RECENTES (últimas 5):")
    print("-" * 80)
    leads_recentes = pipeline.listar_leads_recentes(limite=5)
    
    for i, lead in enumerate(leads_recentes, 1):
        print(f"\n{i}. {lead['nome']}")
        print(f"   📧 {lead['email'] or 'N/A'}")
        print(f"   📱 {lead['telefone'] or 'N/A'}")
        print(f"   📍 {lead['cidade']}, {lead['estado']}")
        print(f"   🏷️ {lead['ramo']} | Status: {lead['status']} | Fonte: {lead['fonte']}")
        print(f"   📅 Coletado em: {lead['data_coleta']}")


def exemplo_5_tratamento_erros():
    """Exemplo 5: Demonstração de tratamento de erros."""
    print("\n" + "="*80)
    print("EXEMPLO 5: TRATAMENTO DE ERROS")
    print("="*80)
    
    from services.lead_extractor.models import Empresa, LeadSource
    from services.lead_extractor.database import DatabaseError
    
    # Erro 1: Validação de dados
    print("\n1️⃣ Validação de Dados")
    print("-" * 80)
    try:
        empresa_invalida = Empresa(
            nome="",  # Nome vazio - erro!
            website="https://exemplo.com",
            endereco="Rua X",
            cidade="SP",
            estado="SP",
            ramo="Varejo",
            fonte=LeadSource.API
        )
    except ValueError as e:
        print(f"❌ Erro capturado: {e}")
        print(f"   Tipo: ValueError")
        print(f"   Mensagem: Nome da empresa deve ser uma string não vazia")
    
    # Erro 2: Website duplicado
    print("\n2️⃣ Website Duplicado no Banco")
    print("-" * 80)
    pipeline = PipelineExtracao()
    
    empresa = Empresa(
        nome="Empresa Teste",
        website="https://empresa-unica.com",
        endereco="Endereço",
        cidade="São Paulo",
        estado="SP",
        ramo="Serviços",
        fonte=LeadSource.API
    )
    
    # Primeira inserção - sucesso
    resultado1 = pipeline.persistir_leads([empresa])
    print(f"✅ Primeira inserção: {resultado1['mensagem']}")
    
    # Segunda inserção - website duplicate
    try:
        resultado2 = pipeline.persistir_leads([empresa])
        if resultado2['status'] == 'erro':
            print(f"❌ Segunda inserção falhou: {resultado2['mensagem']}")
    except DatabaseError as e:
        print(f"❌ Erro de banco: {e}")
    
    print("\n3️⃣ Configuração de Retry Automático")
    print("-" * 80)
    print("O microsserviço implementa retry automático para:")
    print("   • Timeouts de conexão")
    print("   • Erros de servidor (5xx)")
    print("   • Rate limiting (429)")
    print("   • Erros temporários de rede")
    print("\nAxponential backoff: tenta 3 vezes com intervalo progressivo")


def exemplo_6_tipagem_estatica():
    """Exemplo 6: Demonstração de tipagem estática."""
    print("\n" + "="*80)
    print("EXEMPLO 6: TIPAGEM ESTÁTICA")
    print("="*80)
    
    print("\n✅ TIPAGEM ESTÁTICA IMPLEMENTADA:")
    print("-" * 80)
    
    exemplos_tipagem = [
        ("models.py", "Empresa", "@dataclass com type hints completos"),
        ("models.py", "LeadSource", "Enum tipado para fontes de coleta"),
        ("models.py", "LeadStatus", "Enum tipado para status de leads"),
        ("database.py", "inserir_empresa()", "Returns int com tipo explícito"),
        ("database.py", "listar_empresas_por_cidade()", "Returns List[Empresa]"),
        ("extractors.py", "ExtratorBase", "ABC com abstractmethod typado"),
        ("extractors.py", "_fazer_requisicao()", "Optional[requests.Response]"),
        ("main.py", "PipelineExtracao", "Classe com métodos totalmente tipados"),
    ]
    
    for arquivo, elemento, descricao in exemplos_tipagem:
        print(f"✓ {arquivo:15} | {elemento:30} | {descricao}")
    
    print("\n💡 BENEFÍCIOS:")
    print("   • Detecção de bugs em tempo de desenvolvimento (mypy)")
    print("   • Autocompletar superior no editor")
    print("   • Documentação automática do código")
    print("   • Refatoração segura")
    print("   • Redução de testes de tipo em runtime")


def menu_principal():
    """Menu interativo com exemplos."""
    print("\n" + "="*80)
    print("🚀 MICROSSERVIÇO DE EXTRAÇÃO DE LEADS - DEMONSTRAÇÃO")
    print("="*80)
    print("\nExemplos Disponíveis:")
    print("  1. Extração Básica (API Demo)")
    print("  2. Múltiplas Extrações e Agregação")
    print("  3. Web Scraping (Configuração)")
    print("  4. Consultas e Relatórios")
    print("  5. Tratamento de Erros")
    print("  6. Tipagem Estática")
    print("  7. Executar Todos")
    print("  0. Sair")
    
    return input("\nEscolha uma opção (0-7): ").strip()


if __name__ == "__main__":
    try:
        while True:
            opcao = menu_principal()
            
            if opcao == "1":
                exemplo_1_extracao_basica()
            elif opcao == "2":
                exemplo_2_multiplas_extraçoes()
            elif opcao == "3":
                exemplo_3_web_scraping_simulado()
            elif opcao == "4":
                exemplo_4_consultas_database()
            elif opcao == "5":
                exemplo_5_tratamento_erros()
            elif opcao == "6":
                exemplo_6_tipagem_estatica()
            elif opcao == "7":
                exemplo_1_extracao_basica()
                exemplo_2_multiplas_extraçoes()
                exemplo_3_web_scraping_simulado()
                exemplo_4_consultas_database()
                exemplo_5_tratamento_erros()
                exemplo_6_tipagem_estatica()
            elif opcao == "0":
                print("\n👋 Encerrando...\n")
                break
            else:
                print("❌ Opção inválida. Tente novamente.")
            
            input("\n[Pressione ENTER para continuar...]")
    
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}\n")
        sys.exit(1)
