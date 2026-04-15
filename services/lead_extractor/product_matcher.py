"""
Microsserviço de Classificação de Produtos CDKTeck
Mapeia perfis de leads para os 5 produtos principais.
Usa heurística de keywords com LLM integration pronta.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re


logger = logging.getLogger(__name__)


class ProdutoCDKTeck(str, Enum):
    """Produtos disponíveis no portfólio CDKTeck."""
    SENSEIDB = "SenseiDB"
    GESTAO_RPD = "GestaoRPD"
    PAPO_DADOS = "PapoDados"
    CACA_PRECO = "CaçaPreço"
    BIO_COACH = "BioCoach"


@dataclass
class ProdutoInfo:
    """Informações sobre um produto CDKTeck."""
    
    nome: str
    nichos_principais: List[str]
    palavras_chave: List[str]
    dores_resolvidas: Dict[str, str]
    propostas_valor: List[str]
    casos_uso: List[str]
    setores_verticais: List[str]


class CatalogoProdutos:
    """Catálogo com informações detalhadas dos 5 produtos CDKTeck."""
    
    PRODUTOS: Dict[str, ProdutoInfo] = {
        "SenseiDB": ProdutoInfo(
            nome="SenseiDB",
            nichos_principais=[
                "Educação",
                "Treinamento corporativo",
                "Atendimento ao cliente",
                "Call centers",
                "Plataformas educacionais"
            ],
            palavras_chave=[
                "educação", "ensino", "escola", "universidade", "curso",
                "treinamento", "capacitação", "learning", "lms", "educacional",
                "atendimento", "call center", "customer service", "suporte",
                "aluno", "estudante", "professor", "instrutor", "mentor",
                "plataforma de aprendizado", "e-learning", "educação online",
                "conhecimento", "formação", "desenvolvimento profissional"
            ],
            dores_resolvidas={
                "centralizar_conhecimento": "Centralizar todo conhecimento em uma plataforma única",
                "acessibilidade": "Tornar conteúdo acessível 24/7 para alunos e clientes",
                "personalização": "Personalizar experiência de aprendizado por perfil",
                "retenção": "Aumentar retenção de conhecimento com gamificação",
                "escalabilidade": "Escalar treinamentos sem aumentar custos"
            },
            propostas_valor=[
                "Banco de dados inteligente para conhecimento corporativo",
                "Plataforma centralizada de aprendizado e atendimento",
                "Respostas personalizadas baseadas em perfil do usuário",
                "Escalabilidade de treinamentos sem overhead operacional"
            ],
            casos_uso=[
                "Plataforma de e-learning para universidade",
                "Base de conhecimento para call center",
                "Sistema de onboarding para nova equipe",
                "Repositório de treinamentos corporativos"
            ],
            setores_verticais=[
                "Educação", "EdTech", "Call Centers", "Suporte Técnico",
                "Consultoria", "Treinamento", "Recursos Humanos"
            ]
        ),
        
        "GestaoRPD": ProdutoInfo(
            nome="GestaoRPD",
            nichos_principais=[
                "Clínicas",
                "Consultórios médicos",
                "Escritórios administrativos",
                "RH e Pessoas",
                "Administração"
            ],
            palavras_chave=[
                "clínica", "consultório", "médico", "odonto", "dentista",
                "saúde", "paciente", "prontuário", "agendamento",
                "crm administrativo", "gestão administrativo",
                "escritório", "administrativo", "burocracia",
                "gestão de pessoas", "rh", "recursos humanos",
                "folha de pagamento", "férias", "ponto",
                "prontuário eletrônico", "telemedicina",
                "padrao rpd", "regulamentação", "conformidade"
            ],
            dores_resolvidas={
                "gestao_pacientes": "Gerenciar pacientes e histórico médico centralizado",
                "agendamento": "Otimizar agendamento e reduzir no-shows",
                "conformidade": "Garantir conformidade com padrões técnicos (RPD)",
                "automacao_rh": "Automatizar processos de RH e folha de pagamento",
                "produtividade_admin": "Reduzir tempo em tarefas administrativas"
            },
            propostas_valor=[
                "Gestão completa de clínicas com prontuário eletrônico",
                "Automação de processos administrativos e RH",
                "Conformidade garantida com padrões técnicos",
                "Redução de 70% do tempo em tarefas administrativas"
            ],
            casos_uso=[
                "Sistema de gestão para clínica multiprofissional",
                "Automação de RH para empresa com 50-500 funcionários",
                "Gestão de consultório com agendamento online",
                "Controle de backoffice administrativo"
            ],
            setores_verticais=[
                "Saúde", "Clínicas", "Consultórios", "RH/Peopleware",
                "Administração", "Advocacia", "Contabilidade"
            ]
        ),
        
        "PapoDados": ProdutoInfo(
            nome="PapoDados",
            nichos_principais=[
                "Indústria",
                "Logística",
                "Operações",
                "Supply Chain",
                "Manufatura"
            ],
            palavras_chave=[
                "indústria", "manufatura", "fábrica", "produção",
                "logística", "supply chain", "distribuição",
                "operações", "operacional", "eficiência",
                "estoque", "inventário", "cadeia de suprimento",
                "otimização", "lean", "just-in-time",
                "armazém", "warehouse", "fulfillment",
                "planejamento", "otimizar custos", "reduzir desperdício",
                "rastreabilidade", "tracking", "visibilidade em tempo real",
                "analytics operacional", "data-driven decisions"
            ],
            dores_resolvidas={
                "visibilidade": "Obter visibilidade em tempo real de operações",
                "otimizacao": "Otimizar rotas e reduzir custos logísticos",
                "predicoes": "Fazer previsões de demanda mais precisas",
                "eficiencia": "Aumentar eficiência operacional em 40%+",
                "dados_insights": "Converter dados brutos em insights acionáveis"
            },
            propostas_valor=[
                "Plataforma de dados para operações complexas",
                "Analytics em tempo real para logística e supply chain",
                "Previsões baseadas em machine learning",
                "Redução de custos operacionais via otimização"
            ],
            casos_uso=[
                "Dashboard de logística para distribuidor",
                "Previsão de demanda para manufatura",
                "Otimização de rotas para entrega",
                "Análise de eficiência operacional"
            ],
            setores_verticais=[
                "Indústria", "Logística", "Supply Chain", "Manufatura",
                "Distribuição", "Retail (backoffice)", "Energia"
            ]
        ),
        
        "CaçaPreço": ProdutoInfo(
            nome="CaçaPreço",
            nichos_principais=[
                "Comércio",
                "Varejo",
                "E-commerce",
                "Retail local",
                "Marketplaces"
            ],
            palavras_chave=[
                "varejo", "retail", "loja", "comerciante",
                "e-commerce", "ecommerce", "online store",
                "preço", "pricing", "competitividade",
                "margem", "lucro", "rentabilidade",
                "marketplace", "site de vendas",
                "competidor", "concorrência", "inteligência competitiva",
                "produto", "sku", "categoria",
                "conversão", "taxa de vendas", "ticket médio",
                "dinamização de preços", "repricing",
                "desconto", "promoção", "campanha"
            ],
            dores_resolvidas={
                "competitividade": "Manter preços competitivos contra concorrentes",
                "margens": "Otimizar margens sem perder competitividade",
                "dinamica": "Ajustar preços dinamicamente conforme demanda",
                "volume": "Aumentar volume de vendas via pricing inteligente",
                "monitoramento": "Monitorar 100+ concorrentes automaticamente"
            },
            propostas_valor=[
                "Monitoramento inteligente de preços de concorrentes",
                "Otimização automática de preços para máxima margem",
                "Previsão de demanda para melhor pricing",
                "Aumentar conversão via preços estratégicos"
            ],
            casos_uso=[
                "Repricagem automática para marketplace",
                "Monitoramento de concorrentes para e-commerce",
                "Otimização de preços por sazonalidade",
                "Análise de elasticidade de demanda"
            ],
            setores_verticais=[
                "Varejo", "E-commerce", "Marketplaces", "Comércio eletrônico",
                "Dropshipping", "Franquias", "Lojas físicas com online"
            ]
        ),
        
        "BioCoach": ProdutoInfo(
            nome="BioCoach",
            nichos_principais=[
                "Academias",
                "Nutricionistas",
                "Treinadores",
                "Saúde ocupacional",
                "Wellness"
            ],
            palavras_chave=[
                "academia", "gym", "fitness", "musculação",
                "nutricionista", "nutrição", "dieta",
                "personal trainer", "coach", "treinador",
                "saúde", "bem-estar", "wellness",
                "saúde ocupacional", "corporate wellness",
                "treino", "exercício", "plano de treino",
                "bio", "biometria", "métricas de saúde",
                "acompanhamento", "consultoria", "coaching",
                "progresso", "resultado", "transformação",
                "avaliação física", "acompanhamento nutricional",
                "behavior change", "mudança de hábito"
            ],
            dores_resolvidas={
                "acompanhamento": "Acompanhar múltiplos clientes com precisão",
                "progresso": "Visualizar e manter motivação via progresso",
                "personalizar": "Criar planos personalizados por bio do cliente",
                "escalabilidade": "Escalar consultoria sem aumentar equipe",
                "retenção": "Aumentar retenção de clientes com engajamento"
            },
            propostas_valor=[
                "Plataforma de coaching para academias e profissionais",
                "Acompanhamento personalizado baseado em biometria",
                "Escalabilidade de consultoria de 1:1 para 1:N",
                "Aumentar retenção de clientes em 60%+"
            ],
            casos_uso=[
                "App de treino para academia com 500+ alunos",
                "Gestão de consultoria nutricional online",
                "Programa de wellness corporativo",
                "Plataforma de personal training remoto"
            ],
            setores_verticais=[
                "Fitness", "Nutrição", "Saúde ocupacional", "Wellness",
                "Esportes", "Medicina preventiva", "Corporate Health"
            ]
        )
    }


class ClassificadorProdutos:
    """Classificador heurístico de leads para produtos CDKTeck."""
    
    def __init__(self):
        """Inicializa o classificador."""
        self.catalogo = CatalogoProdutos()
        logger.info("Classificador de produtos inicializado")
    
    def _normalizar_texto(self, texto: str) -> str:
        """Normaliza texto para busca (minúsculas, sem acentos)."""
        if not texto:
            return ""
        
        # Minúsculas
        texto = texto.lower()
        
        # Remover acentos básicos
        acentos = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
            'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c',
        }
        for acento, sem_acento in acentos.items():
            texto = texto.replace(acento, sem_acento)
        
        return texto
    
    def _calcular_score_produto(
        self,
        niche_normalizado: str,
        summary_normalizado: str,
        produto_info: ProdutoInfo
    ) -> float:
        """
        Calcula score de matching para um produto.
        
        Args:
            niche_normalizado: Nicho normalizado
            summary_normalizado: Resumo normalizado
            produto_info: Informações do produto
            
        Returns:
            Score 0-100
        """
        score = 0.0
        matches_nicho = 0
        matches_keyword = 0
        matches_setor = 0
        
        texto_completo = f"{niche_normalizado} {summary_normalizado}"
        
        # 1. Verificar nichos principais (peso: 40 pontos por match)
        for nicho in produto_info.nichos_principais:
            nicho_norm = self._normalizar_texto(nicho)
            # Match exato ou substring
            if nicho_norm in niche_normalizado or niche_normalizado in nicho_norm:
                score += 40
                matches_nicho = 1
                logger.debug(f"  ✓ Nicho matching: '{nicho}'")
                break
        
        # 2. Verificar palavras-chave em nicho e resumo (peso: 1.5 por match)
        for palavra_chave in produto_info.palavras_chave:
            palavra_norm = self._normalizar_texto(palavra_chave)
            
            # Match exato de palavra (boundary)
            if re.search(rf'\b{re.escape(palavra_norm)}\b', texto_completo):
                score += 2
                matches_keyword += 1
                logger.debug(f"  ✓ Keyword matching: '{palavra_chave}'")
            # Match parcial (substring) - apenas palavras longas >= 5
            elif palavra_norm in texto_completo and len(palavra_norm) >= 5:
                score += 1
                matches_keyword += 1
                logger.debug(f"  ✓ Keyword parcial: '{palavra_chave}'")
        
        # Limitar contributição de keywords a máximo 35 pontos
        score = min(40 + matches_nicho * 40 + min(matches_keyword, 35), 100)
        
        # 3. Verificar setores verticais (peso: 10 pontos por match)
        for setor in produto_info.setores_verticais:
            setor_norm = self._normalizar_texto(setor)
            if setor_norm in niche_normalizado or setor_norm in texto_completo:
                score += 10
                matches_setor = 1
                logger.debug(f"  ✓ Setor matching: '{setor}'")
                break
        
        # 4. Boost por múltiplos matches (demonstra relevância)
        total_matches = matches_nicho + matches_keyword + matches_setor
        if total_matches >= 3:
            score = min(100, score + (total_matches - 2) * 5)
        
        return min(100.0, score)
    
    def _selecionar_proposta_valor(
        self,
        produto_info: ProdutoInfo,
        niche_normalizado: str,
        summary_normalizado: str
    ) -> str:
        """
        Seleciona a melhor proposta de valor baseada no nicho e resumo.
        
        Args:
            produto_info: Informações do produto
            niche_normalizado: Nicho normalizado
            summary_normalizado: Resumo normalizado
            
        Returns:
            Proposta de valor mais relevante
        """
        # Se houver dores resolvidas específicas mencionadas, usar essas
        texto_completo = f"{niche_normalizado} {summary_normalizado}"
        
        for chave_dor, dor_resolvida in produto_info.dores_resolvidas.items():
            # Extrair palavras-chave da chave da dor
            palavras_dor = chave_dor.split('_')
            for palavra in palavras_dor:
                if palavra in texto_completo:
                    # Retornar a proposta de valor correspondente
                    # Mapear a dor para proposta
                    idx = list(produto_info.dores_resolvidas.keys()).index(chave_dor)
                    if idx < len(produto_info.propostas_valor):
                        return produto_info.propostas_valor[idx]
        
        # Fallback: retornar primeira proposta de valor
        return produto_info.propostas_valor[0] if produto_info.propostas_valor else "Solução especializada"
    
    def match_cdkteck_product(
        self,
        lead_niche: str,
        lead_summary: str
    ) -> Dict[str, Any]:
        """
        Classifica um lead para um dos 5 produtos CDKTeck.
        
        Usa heurística baseada em keywords e nichos.
        Em produção, pode ser integrado com LLM (ex: GPT-4 mini, Llama2).
        
        Args:
            lead_niche: Nicho/setor do lead (ex: "Clínica Médica", "Academia de Fitness")
            lead_summary: Resumo do lead com descrição (ex: "Clínica com 50 pacientes...")
            
        Returns:
            Dict contendo:
            {
                'produto': str,                    # Nome do produto (ex: "SenseiDB")
                'proposta_valor': str,             # Proposta de valor específica
                'score_confianca': float,          # 0-100 (confiança da classificação)
                'dores_resolvidas': List[str],     # Problemas que o produto resolve
                'casos_uso': List[str],            # Exemplos de como usar para este lead
                'setores_aplicaveis': List[str],   # Setores verticais relevantes
                'proximos_passos': str             # Recomendação de próxima ação
            }
        """
        logger.info(f"Classificando lead: {lead_niche[:50]}...")
        
        # Normalizar inputs
        niche_norm = self._normalizar_texto(lead_niche)
        summary_norm = self._normalizar_texto(lead_summary)
        
        # Calcular score para cada produto
        scores: Dict[str, float] = {}
        
        for nome_produto, info_produto in self.catalogo.PRODUTOS.items():
            score = self._calcular_score_produto(niche_norm, summary_norm, info_produto)
            scores[nome_produto] = score
            logger.debug(f"{nome_produto}: score={score:.1f}")
        
        # Encontrar produto com maior score
        produto_selecionado = max(scores, key=scores.get)
        score_final = scores[produto_selecionado]
        
        # Obter informações do produto selecionado
        info_produto = self.catalogo.PRODUTOS[produto_selecionado]
        
        # Selecionar proposta de valor
        proposta = self._selecionar_proposta_valor(info_produto, niche_norm, summary_norm)
        
        # Determinar confiança da classificação
        # Se score for < 30, confiança médio-baixa
        # Se 30-60, médio
        # Se > 60, alta
        if score_final < 30:
            confianca_nivel = "baixa"
            proximos_passos = "Verificar manualmente o match do lead com o produto"
        elif score_final < 60:
            confianca_nivel = "média"
            proximos_passos = "Validar com consultor antes de enviar proposta"
        else:
            confianca_nivel = "alta"
            proximos_passos = "Preparar proposta de valor específica para este lead"
        
        logger.info(f"Lead classificado para {produto_selecionado} (score={score_final:.1f}, confiança={confianca_nivel})")
        
        return {
            'produto': produto_selecionado,
            'proposta_valor': proposta,
            'score_confianca': round(score_final, 2),
            'confianca_nivel': confianca_nivel,
            'dores_resolvidas': list(info_produto.dores_resolvidas.values())[:3],
            'casos_uso': info_produto.casos_uso[:3],
            'setores_aplicaveis': info_produto.setores_verticais[:5],
            'proximos_passos': proximos_passos,
            'scores_todos_produtos': {k: round(v, 2) for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True)},
        }


# Função exportada principal - a que o usuário vai usar
def match_cdkteck_product(lead_niche: str, lead_summary: str) -> Dict[str, Any]:
    """
    Mapeia um lead para um dos 5 produtos CDKTeck baseado em nicho e resumo.
    
    Função estaticamente tipada que atua como classificador heurístico.
    Pode ser estendida com integração de LLM para maior precisão.
    
    Args:
        lead_niche: Nicho/setor do lead (ex: "Clínica Multiprofissional")
                   ou nome da empresa/indústria
        lead_summary: Resumo descritivo do lead (ex: "Clínica com 50 pacientes,
                     gestión de prontuários, agendamentos automáticos necessários")
    
    Returns:
        Dict com estrutura:
        {
            'produto': str,                    # Um dos: SenseiDB, GestaoRPD, PapoDados, CaçaPreço, BioCoach
            'proposta_valor': str,             # Proposição específica para este nicho
            'score_confianca': float,          # 0-100 (confiança da classificação)
            'confianca_nivel': str,            # 'baixa', 'média', ou 'alta'
            'dores_resolvidas': List[str],     # Top 3 problemas resolvidos
            'casos_uso': List[str],            # Top 3 casos de uso
            'setores_aplicaveis': List[str],   # Setores verticais
            'proximos_passos': str,            # Recomendação de ação
            'scores_todos_produtos': Dict[str, float]  # Scores para todos os produtos
        }
    
    Examples:
        >>> # Exemplo 1: Clínica (deve mapear para GestaoRPD)
        >>> resultado = match_cdkteck_product(
        ...     lead_niche="Clínica Multiprofissional",
        ...     lead_summary="Clínica com 50 pacientes, gestão de prontuários eletrônicos, "
        ...                   "agendamentos manuais causam atrasos"
        ... )
        >>> print(resultado['produto'])  # Output: 'GestaoRPD'
        
        >>> # Exemplo 2: Academia (deve mapear para BioCoach)
        >>> resultado = match_cdkteck_product(
        ...     lead_niche="Academia de Fitness",
        ...     lead_summary="Academia com 300 alunos, personal trainers independentes, "
        ...                   "dificuldade em acompanhar progresso"
        ... )
        >>> print(resultado['produto'])  # Output: 'BioCoach'
        
        >>> # Exemplo 3: E-commerce (deve mapear para CaçaPreço)
        >>> resultado = match_cdkteck_product(
        ...     lead_niche="E-commerce de Eletrônicos",
        ...     lead_summary="Loja online com 1000+ SKUs, concorrência acirrada, "
        ...                   "margens pressionadas pela competição"
        ... )
        >>> print(resultado['produto'])  # Output: 'CaçaPreço'
    
    Notes:
        - A função é determinística: mesmos inputs sempre produzem mesmo output
        - Score de confiança reflete a força do match:
          * < 30: Baixa confiança (verificação manual recomendada)
          * 30-60: Média confiança (validação recomendada)
          * > 60: Alta confiança (processar automaticamente)
        - Para integração com LLM, veja integração_llm.py
    """
    classificador = ClassificadorProdutos()
    return classificador.match_cdkteck_product(lead_niche, lead_summary)


# Exemplos de teste
if __name__ == "__main__":
    import json
    
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*80)
    print("🧪 TESTE: CLASSIFICADOR DE PRODUTOS CDKTECK")
    print("="*80 + "\n")
    
    # Teste 1: Clínica → GestaoRPD
    print("TEST 1: Clínica Médica")
    print("-" * 80)
    result1 = match_cdkteck_product(
        lead_niche="Clínica Multiprofissional",
        lead_summary="Clínica com 50 pacientes, 5 profissionais. Gestão de prontuários "
                     "eletrônicos, agendamentos manuais causam atrasos. RH com folha de pagamento "
                     "complexa. Necessário sistema de gestão administrativo integrado."
    )
    print(f"✅ Produto: {result1['produto']}")
    print(f"   Confiança: {result1['score_confianca']}/100 ({result1['confianca_nivel']})")
    print(f"   Proposta: {result1['proposta_valor']}")
    print()
    
    # Teste 2: Academia → BioCoach
    print("TEST 2: Academia de Fitness")
    print("-" * 80)
    result2 = match_cdkteck_product(
        lead_niche="Academia de Musculação",
        lead_summary="Academia com 300 alunos, 15 Personal Trainers, 3 nutricionistas. "
                     "Dificuldade em acompanhar progresso individual, cliente churn de 30%. "
                     "Precisa de app para treino + nutrição + biometria para reter clientes."
    )
    print(f"✅ Produto: {result2['produto']}")
    print(f"   Confiança: {result2['score_confianca']}/100 ({result2['confianca_nivel']})")
    print(f"   Proposta: {result2['proposta_valor']}")
    print()
    
    # Teste 3: E-commerce → CaçaPreço
    print("TEST 3: Loja E-commerce")
    print("-" * 80)
    result3 = match_cdkteck_product(
        lead_niche="E-commerce de Eletrônicos",
        lead_summary="Loja online com 2000+ SKUs em 3 marketplaces. Concorrência acirrada "
                     "com 50+ competidores diretos. Margens reduzidas, precisa otimizar preços "
                     "dinamicamente. Monitorar preços de concorrentes em tempo real."
    )
    print(f"✅ Produto: {result3['produto']}")
    print(f"   Confiança: {result3['score_confianca']}/100 ({result3['confianca_nivel']})")
    print(f"   Proposta: {result3['proposta_valor']}")
    print()
    
    # Teste 4: Indústria → PapoDados
    print("TEST 4: Empresa de Logística")
    print("-" * 80)
    result4 = match_cdkteck_product(
        lead_niche="Logística e Distribuição",
        lead_summary="Empresa de logística com 50 rotas, 200 entregas/dia. Ineficiência "
                     "em rotas causa custos altos. Precisa de visibilidade em tempo real da "
                     "cadeia de suprimento e previsões de demanda para otimizar operações."
    )
    print(f"✅ Produto: {result4['produto']}")
    print(f"   Confiança: {result4['score_confianca']}/100 ({result4['confianca_nivel']})")
    print(f"   Proposta: {result4['proposta_valor']}")
    print()
    
    # Teste 5: Educação → SenseiDB
    print("TEST 5: Plataforma Educacional")
    print("-" * 80)
    result5 = match_cdkteck_product(
        lead_niche="EdTech - Cursos Online",
        lead_summary="Plataforma de cursos online com 10k alunos, 50 cursos. Necessário "
                     "centralizar conhecimento, personalizar experiência por perfil, gamificação "
                     "para aumentar retenção. Base de conhecimento para FAQ automático."
    )
    print(f"✅ Produto: {result5['produto']}")
    print(f"   Confiança: {result5['score_confianca']}/100 ({result5['confianca_nivel']})")
    print(f"   Proposta: {result5['proposta_valor']}")
    print()
    
    # Teste 6: Caso ambíguo (sem nicho claro)
    print("TEST 6: Lead Ambíguo (teste de fallback)")
    print("-" * 80)
    result6 = match_cdkteck_product(
        lead_niche="Consultoria Empresarial",
        lead_summary="Empresa de consultoria geral. Oferece serviços em múltiplas áreas. "
                     "Procurando soluções para melhorar operações."
    )
    print(f"✅ Produto: {result6['produto']}")
    print(f"   Confiança: {result6['score_confianca']}/100 ({result6['confianca_nivel']})")
    print(f"   Proposta: {result6['proposta_valor']}")
    print()
    
    print("="*80)
    print("📊 SCORES Todos os Produtos (TEST 1)")
    print("="*80)
    print(json.dumps(result1['scores_todos_produtos'], indent=2, ensure_ascii=False))
    print()
