"""
Microsserviço de Disparo SMTP com Roteamento Dinâmico de Remetentes
Implementa envio de emails via Zoho Mail com roteamento baseado em produtos.

Usa aliases específicos por produto para melhor rastreamento e deliverability.
"""

import logging
import smtplib
from typing import Optional, Dict, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Importar o Enum de produtos
from .product_matcher import ProdutoCDKTeck


logger = logging.getLogger(__name__)


class StatusDisparo(str, Enum):
    """Status de disparo de email."""
    PENDENTE = "pendente"
    ENVIADO = "enviado"
    ERRO_SMTP = "erro_smtp"
    ERRO_ROTEAMENTO = "erro_roteamento"
    ERRO_AUTENTICACAO = "erro_autenticacao"
    ERRO_ALIAS = "erro_alias"
    CANCELADO = "cancelado"


class ProvedorSMTP(str, Enum):
    """Provedores SMTP suportados."""
    ZOHO = "zoho"
    SMTP_GENERICO = "smtp_generico"


@dataclass
class ConfiguracaoSMTP:
    """Configuração do servidor SMTP."""
    
    host: str
    porta: int
    usar_tls: bool  # True para 587 (TLS), False para 465 (SSL)
    email_admin: str
    senha_admin: str
    timeout_conexao: int = 30
    tentativas_reconexao: int = 3
    
    def validar(self) -> bool:
        """Valida configuração SMTP."""
        if not all([self.host, self.porta, self.email_admin, self.senha_admin]):
            logger.error("Configuração SMTP incompleta")
            return False
        if self.porta not in [465, 587]:
            logger.error(f"Porta SMTP inválida: {self.porta}. Use 465 (SSL) ou 587 (TLS)")
            return False
        return True


@dataclass
class MapeamentoAliases:
    """
    Mapeamento estático entre produtos e aliases de email.
    Type-safe e imutável.
    """
    
    # Dicionário mapeando produtos para emails específicos
    PRODUTOS_EMAILS: Dict[str, str] = field(
        default_factory=lambda: {
            "SenseiDB": "senseidb@cdkteck.com.br",
            "GestaoRPD": "gestaorpd@cdkteck.com.br",
            "PapoDados": "papodados@cdkteck.com.br",
            "CaçaPreço": "cacapreco@cdkteck.com.br",
            "BioCoach": "biocoach@cdkteck.com.br",
        }
    )
    
    # Email padrão (fallback)
    EMAIL_PADRAO: str = "sdr@cdkteck.com.br"
    
    def obter_alias(self, produto: str) -> str:
        """
        Obtém o alias de email para um produto.
        
        Args:
            produto: Nome do produto (ex: "SenseiDB")
            
        Returns:
            Email do alias correspondente ou EMAIL_PADRAO se não encontrado
        """
        alias = self.PRODUTOS_EMAILS.get(produto, self.EMAIL_PADRAO)
        logger.debug(f"Alias resolvido para produto '{produto}': {alias}")
        return alias
    
    def validar_alias(self, produto: str) -> Tuple[bool, str]:
        """
        Valida se um alias está mapeado para um produto.
        
        Args:
            produto: Nome do produto
            
        Returns:
            Tuple[bool, str] - (é válido, mensagem)
        """
        if produto in self.PRODUTOS_EMAILS:
            return True, f"Alias válido para produto '{produto}'"
        return False, f"Produto '{produto}' não possui alias mapeado"


@dataclass
class ResultadoDisparo:
    """Resultado do disparo de um email."""
    
    sucesso: bool
    status: StatusDisparo
    destinatario: str
    remetente: str
    produto_selecionado: str
    mensagem: str
    data_disparo: datetime = field(default_factory=datetime.now)
    tempo_execucao_ms: Optional[float] = None
    erro_detalhado: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte resultado para dicionário (útil para logging/auditoria)."""
        return {
            'sucesso': self.sucesso,
            'status': self.status.value,
            'destinatario': self.destinatario,
            'remetente': self.remetente,
            'produto_selecionado': self.produto_selecionado,
            'mensagem': self.mensagem,
            'data_disparo': self.data_disparo.isoformat(),
            'tempo_execucao_ms': self.tempo_execucao_ms,
            'erro_detalhado': self.erro_detalhado,
        }


ZOHO_SIGNATURE_HTML = """
<br>
<br>
<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial, sans-serif">
    <tbody>
        <tr>
            <td width="4" style="background-color:rgb(255, 140, 0)">
                <br>
            </td>
            <td width="15">
                <br>
            </td>
            <td valign="middle">
                <img src="https://cdkteck.com.br/assets/favicon.png" alt="CDK TECK" width="80" style="display:block; border:none">
            </td>
            <td width="15">
                <br>
            </td>
            <td valign="middle">
                <div>
                    <span class="colour" style="color:rgb(0, 0, 0)">
                        <b>
                            <span class="size" style="font-size:18px">
                                Cidirclay Queiroz
                            </span>
                        </b>
                    </span>
                    <br>
                </div>
                <div>
                    <span class="colour" style="color:rgb(85, 85, 85)">
                        <span class="size" style="font-size:14px">
                            CDK TECK Soluções Tecnológicas
                        </span>
                    </span>
                    <br>
                </div>
                <div>
                    <br>
                </div>
                <div style="height:8px">
                    <br>
                </div>
                <div>
                    <span class="size" style="font-size:12px">
                        <a href="https://www.cdkteck.com.br" style="color:rgb(0, 174, 239); text-decoration:none; font-weight:bold" target="_blank">
                            www.cdkteck.com.br
                        </a>
                        <span class="colour" style="color:rgb(153, 153, 153)">
                            &nbsp;|&nbsp;Macaé - RJ
                        </span>
                    </span>
                    <br>
                </div>
            </td>
            <td width="15">
                <br>
            </td>
            <td width="4" style="background-color:rgb(0, 229, 255)">
                <br>
            </td>
        </tr>
    </tbody>
</table>
<div>
    <br>
</div>
"""

class DispachadorSMTPProdutos:
    """
    Dispachador SMTP com roteamento dinâmico baseado em produtos.
    
    Características:
    - Roteamento automático de remetentes por produto
    - Suporte a Zoho Mail (porta 465/SSL e 587/TLS)
    - Logs estruturados e auditoria completa
    - Type hints completos
    - Tratamento robusto de exceções
    """
    
    def __init__(
        self,
        config_smtp: ConfiguracaoSMTP,
        mapeamento_aliases: Optional[MapeamentoAliases] = None,
    ):
        """
        Inicializa o despachador SMTP.
        
        Args:
            config_smtp: Configuração do servidor SMTP
            mapeamento_aliases: Mapeamento produtos → emails (usa padrão se None)
            
        Raises:
            ValueError: Se configuração SMTP for inválida
        """
        if not config_smtp.validar():
            raise ValueError("Configuração SMTP inválida")
        
        self.config_smtp = config_smtp
        self.mapeamento = mapeamento_aliases or MapeamentoAliases()
        
        logger.info(
            f"DispachadorSMTPProdutos inicializado | "
            f"Host: {config_smtp.host} | "
            f"Porta: {config_smtp.porta} | "
            f"TLS: {config_smtp.usar_tls}"
        )
    
    def _obter_remetente(self, produto: str) -> str:
        """
        Obtém o remetente corrigido baseado no produto.
        
        Args:
            produto: Nome do produto (resultado do match_cdkteck_product)
            
        Returns:
            Email do remetente (alias do produto)
            
        Raises:
            KeyError: Se produto não for reconhecido
        """
        # Validar se produto é válido
        produtos_validos = [p.value for p in ProdutoCDKTeck]
        if produto not in produtos_validos:
            logger.warning(
                f"Produto '{produto}' não reconhecido. Produtos válidos: {produtos_validos}"
            )
            # Usar fallback
            remetente = self.mapeamento.EMAIL_PADRAO
        else:
            remetente = self.mapeamento.obter_alias(produto)
        
        return remetente
    
    def _construir_mensagem_mime(
        self,
        destinatario: str,
        remetente: str,
        assunto: str,
        corpo_html: str,
        corpo_texto: Optional[str] = None,
    ) -> MIMEMultipart:
        """
        Constrói mensagem MIME com headers corretos, incluindo List-Unsubscribe.
        
        Args:
            destinatario: Email do destinatário
            remetente: Email do remetente (com alias)
            assunto: Assunto do email
            corpo_html: Corpo em HTML
            corpo_texto: Corpo em texto plano (alternativa)
            
        Returns:
            MIMEMultipart construído
        """
        msg = MIMEMultipart('alternative')
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = assunto
        
        # Injetar cabeçalho List-Unsubscribe com formato mailto dinâmico
        # RFC 8058: <mailto:email?subject=unsubscribe>
        # Para fallback (sem produto), usar suporte@cdkteck.com.br
        list_unsubscribe_email: str = (
            "suporte@cdkteck.com.br" 
            if remetente == self.mapeamento.EMAIL_PADRAO 
            else remetente
        )
        list_unsubscribe_header: str = f"<mailto:{list_unsubscribe_email}?subject=unsubscribe>"
        msg['List-Unsubscribe'] = list_unsubscribe_header
        
        logger.debug(f"Header List-Unsubscribe adicionado para {destinatario}: {list_unsubscribe_header}")
        
        # O corpo_html já vem montado e renderizado do MS6.
        corpo_html_completo = corpo_html
        
        # Se não tiver texto plano, criar versão simplificada do HTML
        if not corpo_texto:
            # Remover tags HTML simples
            import re
            corpo_texto = re.sub('<[^<]+?>', '', corpo_html_completo)
        
        # Attach alternativas (texto primeiro, depois HTML)
        msg.attach(MIMEText(corpo_texto, 'plain', 'utf-8'))
        msg.attach(MIMEText(corpo_html_completo, 'html', 'utf-8'))
        
        return msg
    
    def _conectar_smtp(self) -> smtplib.SMTP:
        """
        Estabelece conexão SMTP com Zoho.
        
        Returns:
            Conexão SMTP estabelecida
            
        Raises:
            smtplib.SMTPException: Se falhar conexão
            smtplib.SMTPAuthenticationError: Se falhar autenticação
        """
        try:
            if self.config_smtp.usar_tls:
                # TLS na porta 587
                server = smtplib.SMTP(
                    self.config_smtp.host,
                    self.config_smtp.porta,
                    timeout=self.config_smtp.timeout_conexao
                )
                server.starttls()
            else:
                # SSL na porta 465
                server = smtplib.SMTP_SSL(
                    self.config_smtp.host,
                    self.config_smtp.porta,
                    timeout=self.config_smtp.timeout_conexao
                )
            
            # Autenticar
            server.login(self.config_smtp.email_admin, self.config_smtp.senha_admin)
            
            logger.debug(
                f"Conexão SMTP estabelecida: {self.config_smtp.host}:{self.config_smtp.porta}"
            )
            return server
        
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Falha na autenticação SMTP: {str(e)}")
            raise
        except smtplib.SMTPException as e:
            logger.error(f"Erro SMTP ao conectar: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao conectar SMTP: {str(e)}")
            raise
    
    def disparar_email(
        self,
        destinatario: str,
        assunto: str,
        corpo_html: str,
        corpo_texto: Optional[str] = None,
        produto_selecionado: Optional[str] = None,
        tentar_reconectar: bool = True,
    ) -> ResultadoDisparo:
        """
        Dispara email com roteamento automático de remetente por produto.
        
        Args:
            destinatario: Email do destinatário
            assunto: Assunto do email
            corpo_html: Corpo em HTML
            corpo_texto: Corpo em texto plano (opcional)
            produto_selecionado: Produto (para roteamento). Se None, usa EMAIL_PADRAO
            tentar_reconectar: Se True, tenta reconectar em caso de erro
            
        Returns:
            ResultadoDisparo com detalhes da operação
        """
        import time
        tempo_inicio = time.time()
        
        # Determinar remetente baseado no produto
        try:
            if not produto_selecionado:
                logger.warning("Produto não informado, usando email padrão")
                remetente = self.mapeamento.EMAIL_PADRAO
            else:
                remetente = self._obter_remetente(produto_selecionado)
            
            logger.info(
                f"Despachando email | "
                f"Destinatário: {destinatario} | "
                f"Remetente: {remetente} | "
                f"Produto: {produto_selecionado}"
            )
        
        except Exception as e:
            tempo_execucao = (time.time() - tempo_inicio) * 1000
            logger.error(f"Erro ao validar remetente: {str(e)}")
            return ResultadoDisparo(
                sucesso=False,
                status=StatusDisparo.ERRO_ROTEAMENTO,
                destinatario=destinatario,
                remetente=produto_selecionado or self.mapeamento.EMAIL_PADRAO,
                produto_selecionado=produto_selecionado or "desconhecido",
                mensagem="Erro ao validar remetente para o produto",
                tempo_execucao_ms=tempo_execucao,
                erro_detalhado=str(e),
            )
        
        # Construir mensagem MIME
        try:
            msg = self._construir_mensagem_mime(
                destinatario=destinatario,
                remetente=remetente,
                assunto=assunto,
                corpo_html=corpo_html,
                corpo_texto=corpo_texto,
            )
            logger.debug(f"Mensagem MIME construída para {destinatario}")
        
        except Exception as e:
            tempo_execucao = (time.time() - tempo_inicio) * 1000
            logger.error(f"Erro ao construir mensagem MIME: {str(e)}")
            return ResultadoDisparo(
                sucesso=False,
                status=StatusDisparo.ERRO_SMTP,
                destinatario=destinatario,
                remetente=remetente,
                produto_selecionado=produto_selecionado or "desconhecido",
                mensagem="Erro ao construir mensagem MIME",
                tempo_execucao_ms=tempo_execucao,
                erro_detalhado=str(e),
            )
        
        # Tentar enviar
        tentativa = 0
        ultima_excecao = None
        
        while tentativa < self.config_smtp.tentativas_reconexao:
            try:
                server = self._conectar_smtp()
                
                try:
                    # Enviar email
                    server.send_message(msg)
                    server.quit()
                    
                    tempo_execucao = (time.time() - tempo_inicio) * 1000
                    
                    logger.info(
                        f"✅ Email enviado com sucesso | "
                        f"Destinatário: {destinatario} | "
                        f"Remetente: {remetente} | "
                        f"Produto: {produto_selecionado} | "
                        f"Tempo: {tempo_execucao:.2f}ms"
                    )
                    
                    return ResultadoDisparo(
                        sucesso=True,
                        status=StatusDisparo.ENVIADO,
                        destinatario=destinatario,
                        remetente=remetente,
                        produto_selecionado=produto_selecionado or "desconhecido",
                        mensagem=f"Email enviado com sucesso via alias '{remetente}'",
                        tempo_execucao_ms=tempo_execucao,
                    )
                
                finally:
                    try:
                        server.quit()
                    except:
                        pass
            
            except smtplib.SMTPAuthenticationError as e:
                ultima_excecao = e
                tempo_execucao = (time.time() - tempo_inicio) * 1000
                logger.error(
                    f"❌ Erro de autenticação SMTP (tentativa {tentativa + 1}/"
                    f"{self.config_smtp.tentativas_reconexao}): {str(e)}"
                )
                return ResultadoDisparo(
                    sucesso=False,
                    status=StatusDisparo.ERRO_AUTENTICACAO,
                    destinatario=destinatario,
                    remetente=remetente,
                    produto_selecionado=produto_selecionado or "desconhecido",
                    mensagem="Falha na autenticação SMTP com Zoho",
                    tempo_execucao_ms=tempo_execucao,
                    erro_detalhado=str(e),
                )
            
            except smtplib.SMTPRecipientsRefused as e:
                ultima_excecao = e
                tempo_execucao = (time.time() - tempo_inicio) * 1000
                
                # Verificar se erro é por alias (remetente)
                if "553" in str(e) or "relay" in str(e).lower():
                    logger.error(
                        f"❌ Erro de alias SMTP (remetente '{remetente}' rejeitado): {str(e)}"
                    )
                    return ResultadoDisparo(
                        sucesso=False,
                        status=StatusDisparo.ERRO_ALIAS,
                        destinatario=destinatario,
                        remetente=remetente,
                        produto_selecionado=produto_selecionado or "desconhecido",
                        mensagem=f"Alias '{remetente}' recusado pelo servidor SMTP Zoho",
                        tempo_execucao_ms=tempo_execucao,
                        erro_detalhado=str(e),
                    )
                else:
                    logger.error(f"Destinatário rejeitado: {str(e)}")
                    return ResultadoDisparo(
                        sucesso=False,
                        status=StatusDisparo.ERRO_SMTP,
                        destinatario=destinatario,
                        remetente=remetente,
                        produto_selecionado=produto_selecionado or "desconhecido",
                        mensagem="Destinatário rejeitado pelo servidor SMTP",
                        tempo_execucao_ms=tempo_execucao,
                        erro_detalhado=str(e),
                    )
            
            except (smtplib.SMTPException, OSError) as e:
                ultima_excecao = e
                tentativa += 1
                logger.warning(
                    f"⚠️ Erro SMTP (tentativa {tentativa}/"
                    f"{self.config_smtp.tentativas_reconexao}): {str(e)}"
                )
                
                if tentativa < self.config_smtp.tentativas_reconexao and tentar_reconectar:
                    import time
                    wait_time = 2 ** tentativa  # Backoff exponencial
                    logger.info(f"Aguardando {wait_time}s antes de reconectar...")
                    time.sleep(wait_time)
                else:
                    tempo_execucao = (time.time() - tempo_inicio) * 1000
                    logger.error(
                        f"❌ Falha ao enviar email após "
                        f"{self.config_smtp.tentativas_reconexao} tentativas"
                    )
                    return ResultadoDisparo(
                        sucesso=False,
                        status=StatusDisparo.ERRO_SMTP,
                        destinatario=destinatario,
                        remetente=remetente,
                        produto_selecionado=produto_selecionado or "desconhecido",
                        mensagem=f"Falha SMTP após {self.config_smtp.tentativas_reconexao} tentativas",
                        tempo_execucao_ms=tempo_execucao,
                        erro_detalhado=str(ultima_excecao),
                    )
        
        tempo_execucao = (time.time() - tempo_inicio) * 1000
        return ResultadoDisparo(
            sucesso=False,
            status=StatusDisparo.ERRO_SMTP,
            destinatario=destinatario,
            remetente=remetente,
            produto_selecionado=produto_selecionado or "desconhecido",
            mensagem="Erro desconhecido ao enviar email",
            tempo_execucao_ms=tempo_execucao,
            erro_detalhado=str(ultima_excecao) if ultima_excecao else "Erro indefinido",
        )
    
    def disparar_lote(
        self,
        emails: list[Dict[str, Any]],
        parar_em_erro: bool = False,
    ) -> list[ResultadoDisparo]:
        """
        Dispara múltiplos emails em lote.
        
        Args:
            emails: Lista de dicts com chaves:
                - destinatario (str required)
                - assunto (str required)
                - corpo_html (str required)
                - corpo_texto (str optional)
                - produto_selecionado (str optional)
            parar_em_erro: Se True, para em primeiro erro
            
        Returns:
            Lista de ResultadoDisparo para cada email
        """
        resultados: list[ResultadoDisparo] = []
        
        logger.info(f"Iniciando disparo em lote de {len(emails)} emails")
        
        for idx, email in enumerate(emails, 1):
            try:
                # Validar campos obrigatórios
                if not all(k in email for k in ['destinatario', 'assunto', 'corpo_html']):
                    logger.error(
                        f"Email {idx}: campos obrigatórios faltando. "
                        f"Requeridos: destinatario, assunto, corpo_html"
                    )
                    continue
                
                resultado = self.disparar_email(
                    destinatario=email['destinatario'],
                    assunto=email['assunto'],
                    corpo_html=email['corpo_html'],
                    corpo_texto=email.get('corpo_texto'),
                    produto_selecionado=email.get('produto_selecionado'),
                )
                
                resultados.append(resultado)
                
                if not resultado.sucesso and parar_em_erro:
                    logger.warning(f"Parando lote por erro no email {idx}")
                    break
            
            except Exception as e:
                logger.error(f"Erro ao processar email {idx}: {str(e)}")
                if parar_em_erro:
                    break
        
        # Resumo
        sucessos = sum(1 for r in resultados if r.sucesso)
        erros = len(resultados) - sucessos
        logger.info(
            f"Lote concluído | "
            f"Total: {len(resultados)} | "
            f"Sucessos: {sucessos} | "
            f"Erros: {erros}"
        )
        
        return resultados
