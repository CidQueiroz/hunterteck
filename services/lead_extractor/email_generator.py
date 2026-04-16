"""
Microsserviço 6: Gerador de Emails Inteligente
Gera emails personalizados com IA usando templates adaptativos.
Suporta integração com Groq (llama3-70b-8192) com resiliência a rate limits.
"""

import logging
import json
import time
import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


# ============================================================================
# CLASSE DE RETRY COM BACKOFF EXPONENCIAL
# ============================================================================

class GroqRetryHandler:
    """
    Handler para retry de chamadas Groq com backoff exponencial.
    Implementa resiliência contra rate limits do Free Tier.
    """
    
    def __init__(
        self,
        max_tentativas: int = 5,
        delay_inicial: float = 1.0,
        delay_maximo: float = 60.0,
        fator_exponencial: float = 2.0
    ):
        """
        Inicializa o handler de retry.
        
        Args:
            max_tentativas: Máximo de tentativas
            delay_inicial: Delay inicial em segundos
            delay_maximo: Delay máximo em segundos
            fator_exponencial: Fator multiplicativo para backoff
        """
        self.max_tentativas = max_tentativas
        self.delay_inicial = delay_inicial
        self.delay_maximo = delay_maximo
        self.fator_exponencial = fator_exponencial
    
    def executar_com_retry(self, funcao, *args, **kwargs) -> Any:
        """
        Executa função com retry automático no caso de rate limit.
        
        Args:
            funcao: Função a executar
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Resultado da função
            
        Raises:
            Exception: Se todas as tentativas falharem
        """
        delay = self.delay_inicial
        ultima_excecao = None
        
        for tentativa in range(1, self.max_tentativas + 1):
            try:
                logger.debug(f"Tentativa {tentativa}/{self.max_tentativas} de chamada Groq")
                return funcao(*args, **kwargs)
            
            except Exception as e:
                ultima_excecao = e
                erro_str = str(e).lower()
                
                # Verificar se é rate limit
                if "rate_limited" in erro_str or "429" in erro_str or "rate limit" in erro_str:
                    if tentativa < self.max_tentativas:
                        logger.warning(
                            f"⚠️ Rate limit atingido (tentativa {tentativa}/{self.max_tentativas}). "
                            f"Aguardando {delay:.1f}s antes de retry..."
                        )
                        time.sleep(delay)
                        delay = min(delay * self.fator_exponencial, self.delay_maximo)
                    else:
                        logger.error(
                            f"❌ Rate limit persistente após {self.max_tentativas} tentativas. "
                            f"Usando fallback com template."
                        )
                        return None
                else:
                    # Erro não relacionado a rate limit
                    logger.error(f"Erro Groq (não relacionado a rate limit): {e}")
                    return None
        
        # Se chegou aqui, todas as tentativas falharam
        logger.error(f"❌ Todas as tentativas falharam: {ultima_excecao}")
        return None


class TipoEmail(str, Enum):
    """Tipos de email no fluxo de outreach."""
    PRIMEIRO_CONTATO = "primeiro_contato"
    SEGUIMENTO_1 = "seguimento_1"
    SEGUIMENTO_2 = "seguimento_2"
    SEGUIMENTO_3 = "seguimento_3"
    REENGAJAMENTO = "reengajamento"


@dataclass
class ContextoEmail:
    """Contexto para geração de email personalizado."""
    
    nome_pessoa: str
    cargo_pessoa: str
    empresa_nome: str
    setor_empresa: str
    tamanho_empresa: Optional[str] = None  # "1-10", "50-100", etc
    receita_empresa: Optional[str] = None  # "1M", "10M", etc
    website_empresa: str = None
    linkedin_url: Optional[str] = None
    pain_points: List[str] = None  # Problemas específicos descobertos
    valor_proposto: str = None  # Valor único que oferecemos
    tipo_email: TipoEmail = TipoEmail.PRIMEIRO_CONTATO
    empresa_vendedora_nome: str = "Nossa Empresa"
    vendedor_nome: str = "Seu Nome"
    vendedor_email: str = "vendedor@empresa.com"
    cta_url: Optional[str] = None  # Call-to-action URL
    product_match_result: Optional[Dict[str, Any]] = None  # Output do match_cdkteck_product
    destinatario_email: Optional[str] = None  # Email do destinatário (opcional, gerado se None)
    
    def __post_init__(self):
        if self.pain_points is None:
            self.pain_points = []


@dataclass
class EmailGerado:
    """Email gerado com metadados."""
    
    destinatario_email: str
    destinatario_nome: str
    assunto: str
    corpo: str
    tipo: TipoEmail
    contexto: Dict[str, Any]
    gerado_por: str  # 'template', 'openai', 'claude'
    data_geracao: datetime = None
    versao_ab: Optional[str] = None  # 'A', 'B', None
    
    def __post_init__(self):
        if self.data_geracao is None:
            self.data_geracao = datetime.now()
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            'destinatario_email': self.destinatario_email,
            'destinatario_nome': self.destinatario_nome,
            'assunto': self.assunto,
            'corpo': self.corpo,
            'tipo': self.tipo.value,
            'gerado_por': self.gerado_por,
            'versao_ab': self.versao_ab,
            'data_geracao': self.data_geracao.isoformat()
        }


class GeradorEmails:
    """Gera emails personalizados inteligentemente."""
    
    # Templates base por tipo de email
    TEMPLATES = {
        TipoEmail.PRIMEIRO_CONTATO: {
            'assuntos': [
                "🎯 Oportunidade para {empresa} - {cargo}",
                "{empresa}: Aumento de ~30% em eficiência",
                "Quick idea for {empresa} - {cargo}",
                "{empresa}: Reconhecido entre top 3 em {setor}",
            ],
            'corpo': """Olá {nome},

Encontrei seu perfil enquanto pesquisava líderes de {cargo} em {setor}.

Estou ajudando empresas como {empresa} a {valor_proposto}.

{pain_points_text}

Seria interessante uma conversa de 15min para explorar?"""
        },
        
        TipoEmail.SEGUIMENTO_1: {
            'assuntos': [
                "[Follow-up] Oportunidade para {empresa}",
                "{nome} - Quick follow-up",
                "Re: Oportunidade para {empresa}",
            ],
            'corpo': """Olá {nome},

Apenas fazendo follow-up no meu email anterior.

Entendo que você está ocupado, mas achei que essa oportunidade poderia valer seu tempo:

{valor_proposto}

Tem 15min disponível essa semana?"""
        },
        
        TipoEmail.REENGAJAMENTO: {
            'assuntos': [
                "Última tentativa: Oportunidade para {empresa}",
                "{nome}, uma última coisa...",
                "Importante: {empresa} - {cargo}",
            ],
            'corpo': """Olá {nome},

Esta é minha última mensagem - prometo!

Muitas empresas em {setor} estão vendo resultados com nossa solução.
Se {empresa} tiver interesse, vamos conversar.

Caso contrário, sem problemas - aproveito para desejar sucesso em seus projetos!"""
        }
    }
    
    def __init__(
        self,
        usar_openai: bool = False,
        openai_api_key: Optional[str] = None,
        usar_groq: bool = True,
        groq_api_key: Optional[str] = None
    ):
        """
        Inicializa o gerador de emails.
        
        Args:
            usar_openai: Se True, tenta usar OpenAI GPT-4 (DESCONTINUADO)
            openai_api_key: Chave de API da OpenAI (opcional)
            usar_groq: Se True, usa Groq com llama3-70b-8192 (RECOMENDADO)
            groq_api_key: Chave de API do Groq (opcional, tenta ler de variável de ambiente)
        """
        self.usar_openai = usar_openai
        self.openai_api_key = openai_api_key
        self.usar_groq = usar_groq
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.retry_handler = GroqRetryHandler()
        
        # Inicializar Groq
        if self.usar_groq:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("Groq inicializado para geração de emails (modelo: llama3-70b-8192)")
                self.usar_openai = False  # Groq tem prioridade
            except (ImportError, Exception) as e:
                logger.warning(
                    f"Groq não disponível ({e}). Tentando OpenAI ou usando templates."
                )
                self.usar_groq = False
                self.groq_client = None
                
                # Tentar OpenAI como fallback
                if usar_openai:
                    try:
                        import openai
                        self.openai = openai
                        if openai_api_key:
                            openai.api_key = openai_api_key
                        logger.info("OpenAI inicializado como fallback")
                    except ImportError:
                        logger.warning("OpenAI não instalado. Usando templates.")
                        self.usar_openai = False
        
        logger.info("Gerador de emails inicializado")
    
    def gerar_email(
        self,
        contexto: ContextoEmail,
        usar_ia: bool = False
    ) -> EmailGerado:
        """
        Gera um email personalizado.
        
        Args:
            contexto: Contexto para personalização
            usar_ia: Se True, tenta usar IA (Groq com resiliência)
            
        Returns:
            EmailGerado
        """
        logger.info(f"Gerando email para {contexto.nome_pessoa} em {contexto.empresa_nome}")
        
        # Tentar Groq se disponível e solicitado
        if usar_ia and self.usar_groq and self.groq_client:
            try:
                email = self._gerar_com_groq(contexto)
                if email:
                    return email
            except Exception as e:
                logger.warning(f"Erro ao usar Groq: {e}. Usando template...")
        
        # Tentar OpenAI como fallback (se Groq falhou)
        elif usar_ia and self.usar_openai:
            try:
                email = self._gerar_com_openai(contexto)
                if email:
                    return email
            except Exception as e:
                logger.warning(f"Erro ao usar OpenAI: {e}. Usando template...")
        
        # Fallback: usar template
        return self._gerar_com_template(contexto)
    
    def _gerar_com_groq(self, contexto: ContextoEmail) -> Optional[EmailGerado]:
        """
        Gera email usando Groq (llama3-70b-8192) com resiliência a rate limits.
        Integra output do match_cdkteck_product se disponível.
        
        Args:
            contexto: Contexto de personalização (pode incluir product_match_result)
            
        Returns:
            EmailGerado ou None em caso de erro persistente (usa fallback com template)
        """
        try:
            # Construir prompt e system_prompt
            if contexto.product_match_result:
                prompt, system_prompt = self._construir_prompt_com_product_match(contexto)
            else:
                prompt = self._construir_prompt(contexto)
                system_prompt = "Você é um especialista em vendas B2B que escreve emails curtos, persuasivos e personalizados. Sempre responda em JSON com campos 'assunto' e 'corpo'."
            
            logger.debug(f"Chamando Groq para {contexto.nome_pessoa}")
            
            # Função interna para chamada Groq com retry
            def chamar_groq_com_retry():
                response = self.groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                return response
            
            # Executar com retry automático em caso de rate limit
            response = self.retry_handler.executar_com_retry(chamar_groq_com_retry)
            
            if response is None:
                # Rate limit persistente - retornar None para usar fallback
                logger.warning(f"Rate limit persistente no Groq. Usando template para {contexto.nome_pessoa}")
                return None
            
            # Parse resposta
            resposta_texto = response.choices[0].message.content
            resposta_json = json.loads(resposta_texto)
            
            logger.debug(f"Email gerado com sucesso via Groq para {contexto.nome_pessoa}")
            
            return EmailGerado(
                destinatario_email=(
                    contexto.nome_pessoa.lower().replace(' ', '.') + 
                    f"@{contexto.website_empresa}" 
                    if contexto.website_empresa 
                    else contexto.nome_pessoa.lower().replace(' ', '.') + "@cdkteck.com.br"
                ),
                destinatario_nome=contexto.nome_pessoa,
                assunto=resposta_json.get('assunto', 'Oportunidade'),
                corpo=resposta_json.get('corpo', ''),
                tipo=contexto.tipo_email,
                contexto={
                    'empresa': contexto.empresa_nome,
                    'cargo': contexto.cargo_pessoa,
                    'produto': (
                        contexto.product_match_result.get('produto') 
                        if contexto.product_match_result 
                        else None
                    )
                },
                gerado_por='groq'
            )
        
        except json.JSONDecodeError as e:
            logger.warning(f"Erro ao fazer parse JSON da resposta Groq: {e}. Usando template.")
            return None
        except Exception as e:
            logger.error(f"Erro ao usar Groq: {e}")
            return None
    
    def _gerar_com_template(self, contexto: ContextoEmail) -> EmailGerado:
        """
        Gera email usando template base.
        
        Args:
            contexto: Contexto de personalização
            
        Returns:
            EmailGerado
        """
        template = self.TEMPLATES.get(contexto.tipo_email, self.TEMPLATES[TipoEmail.PRIMEIRO_CONTATO])
        
        # Selecionar assunto
        assuntos = template.get('assuntos', [])
        assunto_template = assuntos[0] if assuntos else "Oportunidade para {empresa}"
        
        # Preparar variáveis
        pain_points_text = ""
        if contexto.pain_points:
            pain_points_list = "\n".join([f"• {p}" for p in contexto.pain_points[:3]])
            pain_points_text = f"Desafios que identifiquei em {contexto.setor_empresa}:\n{pain_points_list}\n"
        
        variaveis = {
            'nome': contexto.nome_pessoa.split()[0],  # Primeiro nome
            'cargo': contexto.cargo_pessoa,
            'empresa': contexto.empresa_nome,
            'setor': contexto.setor_empresa,
            'valor_proposto': contexto.valor_proposto or 'aumentar sua eficiência',
            'pain_points_text': pain_points_text
        }
        
        # Interpolação
        assunto = assunto_template.format_map({k: v for k, v in variaveis.items() if '{' + k + '}' in assunto_template})
        corpo = template.get('corpo', '').format_map(variaveis)
        
        return EmailGerado(
            destinatario_email=contexto.destinatario_email if hasattr(contexto, 'destinatario_email') else f"{contexto.nome_pessoa.lower().replace(' ', '.')}@{contexto.website_empresa}",
            destinatario_nome=contexto.nome_pessoa,
            assunto=assunto,
            corpo=corpo,
            tipo=contexto.tipo_email,
            contexto={
                'empresa': contexto.empresa_nome,
                'cargo': contexto.cargo_pessoa,
                'setor': contexto.setor_empresa
            },
            gerado_por='template'
        )
    
    def _gerar_com_openai(self, contexto: ContextoEmail) -> Optional[EmailGerado]:
        """
        Gera email usando OpenAI GPT-4.
        Integra output do match_cdkteck_product se disponível.
        
        Args:
            contexto: Contexto de personalização (pode incluir product_match_result)
            
        Returns:
            EmailGerado ou None em caso de erro
        """
        try:
            # Usar product_match se disponível, senão construir prompt padrão
            if contexto.product_match_result:
                prompt, system_prompt = self._construir_prompt_com_product_match(contexto)
            else:
                prompt = self._construir_prompt(contexto)
                system_prompt = "Você é um especialista em vendas B2B que escreve emails curtos, persuasivos e personalizados. Sempre responda em JSON com campos 'assunto' e 'corpo'. PROIBIDO gerar saudações finais, despedidas (ex: Abraços, Atenciosamente) ou assinaturas. NÃO invente nomes de remetentes ou e-mails. Gere ESTRITAMENTE os parágrafos do corpo do e-mail focados na dor do cliente (AIDA)."
            
            response = self.openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse resposta
            resposta_texto = response.choices[0].message.content
            resposta_json = json.loads(resposta_texto)
            
            return EmailGerado(
                destinatario_email=contexto.nome_pessoa.lower().replace(' ', '.') + f"@{contexto.website_empresa}",
                destinatario_nome=contexto.nome_pessoa,
                assunto=resposta_json.get('assunto', 'Oportunidade'),
                corpo=resposta_json.get('corpo', ''),
                tipo=contexto.tipo_email,
                contexto={
                    'empresa': contexto.empresa_nome,
                    'cargo': contexto.cargo_pessoa,
                    'produto': contexto.product_match_result.get('produto') if contexto.product_match_result else None
                },
                gerado_por='openai'
            )
        
        except Exception as e:
            logger.error(f"Erro ao usar OpenAI: {e}")
            return None
    
    def gerar_lote(
        self,
        contextos: List[ContextoEmail],
        usar_ia: bool = False,
        versao_ab: bool = False,
        delay_entre_requisicoes: float = 0.5
    ) -> List[EmailGerado]:
        """
        Gera um lote de emails com resiliência a rate limits.
        
        Args:
            contextos: Lista de contextos
            usar_ia: Se True, usa IA (Groq com retry automático)
            versao_ab: Se True, gera versão A e B para A/B testing
            delay_entre_requisicoes: Delay em segundos entre requisições Groq 
                                     (recomendado: 0.5-1.0 para evitar rate limits)
            
        Returns:
            Lista de EmailGerado
        """
        logger.info(f"Gerando lote de {len(contextos)} emails (usar_ia={usar_ia})")
        
        emails = []
        
        for i, contexto in enumerate(contextos, 1):
            try:
                # Versão principal
                email = self.gerar_email(contexto, usar_ia=usar_ia)
                email.versao_ab = 'A'
                emails.append(email)
                
                # Versão B para A/B testing (se solicitado)
                if versao_ab and i % 3 == 0:  # 33% dos emails recebem variante B
                    email_b = self.gerar_email(contexto, usar_ia=usar_ia)
                    email_b.versao_ab = 'B'
                    emails.append(email_b)
                
                # Adicionar delay entre requisições para evitar rate limit
                # Apenas se estiver usando IA (Groq)
                if usar_ia and self.usar_groq and i < len(contextos):
                    time.sleep(delay_entre_requisicoes)
            
            except Exception as e:
                logger.error(f"Erro ao gerar email {i} do lote: {e}. Continuando...")
                # Continuar processando o restante do lote
                continue
        
        logger.info(
            f"Lote concluído: {len(emails)} emails gerados "
            f"({len([e for e in emails if e.versao_ab == 'B'])} variantes B)"
        )
        return emails
    
    def gerar_email_com_product_match(
        self,
        nome_pessoa: str,
        cargo_pessoa: str,
        empresa_nome: str,
        setor_empresa: str,
        website_empresa: str,
        product_match_result: Dict[str, Any],
        usar_ia: bool = True,
        vendedor_nome: str = "Time CDKTeck",
        vendedor_email: str = "sdr@cdkteck.com",
        **kwargs
    ) -> EmailGerado:
        """
        Gera email de cold outreach integrando diretamente o resultado do match_cdkteck_product.
        
        Este é o método RECOMENDADO para máxima personalização com AIDA + Product Matcher.
        
        Args:
            nome_pessoa: Nome do decisor
            cargo_pessoa: Cargo do decisor (ex: CEO, Gerente)
            empresa_nome: Nome da empresa alvo
            setor_empresa: Setor/nicho da empresa
            website_empresa: Website da empresa
            product_match_result: Output dict do match_cdkteck_product contendo:
                - 'produto': Nome do produto recomendado
                - 'proposta_valor': Proposta de valor específica
                - 'dores_resolvidas': Lista de dores resolvidas
                - 'score_confianca': Score de confiança
            usar_ia: Se True, usa OpenAI GPT-4 (padrão: True)
            vendedor_nome: Nome do vendedor/SDR
            vendedor_email: Email do vendedor/SDR
            **kwargs: Argumentos adicionais (tamanho_empresa, receita_empresa, etc)
            
        Returns:
            EmailGerado personalizado com framework AIDA
            
        Example:
            >>> from services.lead_extractor.product_matcher import match_cdkteck_product
            >>> from services.lead_extractor.email_generator import GeradorEmails
            >>> 
            >>> # Classificar lead para produto
            >>> match_result = match_cdkteck_product(
            ...     lead_niche="Clínica Odontológica",
            ...     lead_summary="30 pacientes, prontuários manuais..."
            ... )
            >>> 
            >>> # Gerar email personalizado com AIDA
            >>> gerador = GeradorEmails(usar_openai=True)
            >>> email = gerador.gerar_email_com_product_match(
            ...     nome_pessoa="Dra. Silva",
            ...     cargo_pessoa="Diretora Clínica",
            ...     empresa_nome="Clínica Dental Silva",
            ...     setor_empresa="Saúde - Odontologia",
            ...     website_empresa="clinicaldental.com.br",
            ...     product_match_result=match_result,
            ...     usar_ia=True
            ... )
            >>> print(email.corpo)
        """
        logger.info(f"Gerando email com product match para {empresa_nome}")
        
        # Extrair dores automaticamente do product_match
        dores = product_match_result.get('dores_resolvidas', [])
        
        # Preparar contexto com result do product_matcher
        contexto = ContextoEmail(
            nome_pessoa=nome_pessoa,
            cargo_pessoa=cargo_pessoa,
            empresa_nome=empresa_nome,
            setor_empresa=setor_empresa,
            website_empresa=website_empresa,
            pain_points=list(dores)[:3],  # Top 3 dores
            valor_proposto=product_match_result.get('proposta_valor'),
            vendedor_nome=vendedor_nome,
            vendedor_email=vendedor_email,
            product_match_result=product_match_result,  # Essencial para usar novo system_prompt
            tipo_email=TipoEmail.PRIMEIRO_CONTATO,
            **kwargs  # Passar argumentos adicionais
        )
        
        # Gerar email com IA (usando novo system_prompt com AIDA + product match)
        return self.gerar_email(contexto, usar_ia=usar_ia)
    
    @staticmethod
    def _construir_prompt_com_product_match(contexto: ContextoEmail) -> tuple:
        """
        Constrói prompt e system_prompt usando output do match_cdkteck_product.
        
        Args:
            contexto: Contexto com product_match_result preenchido
            
        Returns:
            Tuple (prompt, system_prompt)
        """
        match = contexto.product_match_result or {}
        produto = match.get('produto', 'Nossa Solução')
        proposta_valor = match.get('proposta_valor', 'aumentar sua eficiência')
        dores = match.get('dores_resolvidas', [])
        
        # System prompt com as diretrizes exatas do cliente
        system_prompt = f"""Você é um executivo de vendas B2B da CDKTECK. Escreva um e-mail frio (cold email) curto e direto utilizando o framework AIDA (Atenção, Interesse, Desejo, Ação) para o decisor da {contexto.empresa_nome}. O foco central do e-mail é a dor operacional do setor de {contexto.setor_empresa}. Apresente a aplicação {produto} como a solução exata para essa dor, destacando a proposta de valor: {proposta_valor}. Regras de ouro: Não mencione tecnologias (React, Python, etc), fale apenas sobre otimização de tempo, redução de custos ou vantagem competitiva. O Call to Action (Ação) final deve ser uma oferta simples: perguntar se o decisor aceita receber um vídeo de 2 minutos demonstrando a ferramenta em funcionamento."""
        
        # User prompt com detalhes específicos
        dores_text = "\n".join([f"  • {dor}" for dor in dores[:3]]) if dores else "Desafios comuns do setor"
        
        prompt = f"""Escreva um email de cold outreach B2B seguindo o framework AIDA com:

Destinatário: {contexto.nome_pessoa}, {contexto.cargo_pessoa} em {contexto.empresa_nome}

Empresa: {contexto.empresa_nome} 
Setor/Nicho: {contexto.setor_empresa}
Tamanho: {contexto.tamanho_empresa or 'PME'}

Produto a apresentar: {produto}
Proposta de Valor: {proposta_valor}

Dores operacionais principais do setor {contexto.setor_empresa}:
{dores_text}

Framework AIDA:
1. ATENÇÃO: Abrir com um gancho que capture atenção (não mencione tecnologia)
2. INTERESSE: Mostrar entendimento da dor específica do setor
3. DESEJO: Apresentar {produto} como solução, focando em resultados (tempo/custos/vantagem)
4. AÇÃO: Oferta simples - perguntar se o decisor aceita receber vídeo de 2 minutos demonstrando

Retorne APENAS em formato JSON com campos:
{{
    "assunto": "...",
    "corpo": "..."
}}

Regras:
- Email máx 250 palavras
- Tom executivo mas amigável
- Foco em resultados mensuráveis
- Sem jargão técnico
- CTA: Oferta de vídeo 2 minutos
- Português brasileiro
"""
        
        return prompt, system_prompt
    
    @staticmethod
    def _construir_prompt(contexto: ContextoEmail) -> str:
        """Constrói prompt para OpenAI (sem product_match)."""
        pain_points = "- " + "\n- ".join(contexto.pain_points) if contexto.pain_points else "Desafios comuns no setor"
        
        return f"""
        Escreva um email de outreach B2B curto e persuasivo com os seguintes detalhes:
        
        Destinatário: {contexto.nome_pessoa}, {contexto.cargo_pessoa} em {contexto.empresa_nome}
        Empresa: {contexto.empresa_nome} ({contexto.setor_empresa})
        Tamanho: {contexto.tamanho_empresa or 'PME'}
        
        Proposição de valor: {contexto.valor_proposto or 'Aumentar eficiência operacional'}
        
        Desafios identificados:
        {pain_points}
        
        Tipo de email: {contexto.tipo_email.value.replace('_', ' ').title()}
        
        Retorne APENAS em formato JSON com campos:
        {{
            "assunto": "...",
            "corpo": "..."
        }}
        
        Regras:
        - Email máx 200 palavras
        - Tom profissional mas casual
        - Include call-to-action claro
        - Personalize com dados disponíveis
        - Português brasileiro
        - PROIBIDO gerar saudações finais, despedidas (ex: Abraços, Atenciosamente) ou assinaturas.
        - NÃO invente nomes de remetentes ou e-mails.
        - Gere ESTRITAMENTE os parágrafos do corpo do e-mail focados na dor do cliente.
        """
    
    @staticmethod
    def _gerar_assinatura(contexto: ContextoEmail) -> str:
        """Gera assinatura do email."""
        return ""



# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    gerador = GeradorEmails()
    
    # Contexto de teste
    contexto = ContextoEmail(
        nome_pessoa="João Silva",
        cargo_pessoa="CEO",
        empresa_nome="TechCorp Brasil",
        setor_empresa="Technology",
        tamanho_empresa="50-100",
        website_empresa="techcorp.com.br",
        pain_points=["Reduzir custos operacionais", "Melhorar eficiência", "Automatizar processos"],
        valor_proposto="aumentar produtividade em até 40%",
        tipo_email=TipoEmail.PRIMEIRO_CONTATO,
        vendedor_nome="Maria Santos",
        vendedor_email="maria@ourcompany.com"
    )
    
    # Gerar email
    print("\n📧 Gerando email com template...")
    email = gerador.gerar_email(contexto, usar_ia=False)
    
    print(f"\n✅ Email gerado para: {email.destinatario_nome}")
    print(f"Assunto: {email.assunto}")
    print(f"\nCorpo:\n{email.corpo}")
    
    # Gerar lote
    print("\n\n📧 Gerando lote de 5 emails...")
    contextos = [contexto] * 5
    emails = gerador.gerar_lote(contextos, versao_ab=True)
    print(f"✅ Gerados {len(emails)} emails ({len([e for e in emails if e.versao_ab == 'B'])} variantes B)")
