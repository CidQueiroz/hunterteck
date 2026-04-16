"""
Orquestrador Central do Pipeline B2B Autônomo
Coordena MS1-MS7 em um fluxo automático similar ao AutoGTM
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import json

# Imports dos microsserviços
from services.lead_extractor.main import PipelineExtracao
from services.lead_extractor.validator import ValidadorLeads
from services.lead_extractor.enricher import EnriquecedorDados
from services.lead_extractor.person_finder import LocalizadorPessoas, Pessoa
from services.lead_extractor.email_generator import GeradorEmails, ContextoEmail, TipoEmail
from services.lead_extractor.models import Empresa, LeadStatus
from services.lead_extractor.smtp_dispatcher import DispachadorSMTPProdutos
from services.lead_extractor.config import Config
from services.lead_extractor.product_matcher import match_cdkteck_product


logger = logging.getLogger(__name__)


class PipelineAutonomoB2B:
    """Pipeline completo de automação de vendas B2B estilo AutoGTM."""
    
    def __init__(self):
        """Inicializa o pipeline autônomo."""
        logger.info("="*80)
        logger.info("🚀 PIPELINE AUTÔNOMO B2B - INICIALIZANDO")
        logger.info("="*80)
        
        # Inicializar microsserviços
        self.extrator = PipelineExtracao()
        self.validador = ValidadorLeads()
        self.enriquecedor = EnriquecedorDados()
        self.finder = LocalizadorPessoas()
        self.gerador_emails = GeradorEmails()
        self.dispatcher = DispachadorSMTPProdutos(Config.SMTP_CONFIG)
        
        logger.info("✅ Todos os microsserviços inicializados")
    
    def executar_pipeline_completo(
        self,
        query: str,
        cidade: str,
        estado: str,
        limite_leads: int = 50,
        gerar_emails: bool = True,
        disparar_emails: bool = True
    ) -> Dict[str, Any]:
        """
        Executa o pipeline completo do Lead Generation até Email Generation.
        
        Args:
            query: Termo de busca (ex: "restaurantes")
            cidade: Cidade alvo
            estado: Estado alvo
            limite_leads: Número máximo de leads
            gerar_emails: Se deve gerar emails automaticamente
            
        Returns:
            Resultado geral do pipeline
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🎯 INICIANDO EXECUÇÃO COMPLETA")
        logger.info(f"Query: {query} | Cidade: {cidade}, {estado}")
        logger.info(f"{'='*80}\n")
        
        resultado_final = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'cidade': cidade,
            'estado': estado,
            'etapas': {}
        }
        
        # MS1: Extração de Leads
        logger.info("\n📍 [ETAPA 1/5] MS1 - EXTRAÇÃO DE LEADS")
        logger.info("-"*80)
        etapa_extracao = self._executar_extracao(
            query=query,
            cidade=cidade,
            estado=estado,
            limite=limite_leads
        )
        resultado_final['etapas']['extracao'] = etapa_extracao
        
        leads_brutos = etapa_extracao['leads']
        if not leads_brutos:
            logger.warning("❌ Nenhum lead extraído!")
            return resultado_final
        
        # MS2: Validação de Dados
        logger.info("\n✅ [ETAPA 2/5] MS2 - VALIDAÇÃO DE DADOS")
        logger.info("-"*80)
        etapa_validacao = self._executar_validacao(leads_brutos)
        resultado_final['etapas']['validacao'] = etapa_validacao
        
        leads_validos = etapa_validacao['leads_validos']
        if not leads_validos:
            logger.warning("❌ Nenhum lead passou na validação!")
            return resultado_final
            
        # NOVA ETAPA: Salvar no banco APENAS os Leads Válidos e não duplicados
        logger.info("\n💾 [ETAPA 2.5] Persistindo novos leads validados...")
        self.extrator.persistir_leads(leads_validos)
        
        # MS3: Enriquecimento de Dados
        logger.info("\n🔍 [ETAPA 3/5] MS3 - ENRIQUECIMENTO DE DADOS")
        logger.info("-"*80)
        etapa_enriquecimento = self._executar_enriquecimento(leads_validos)
        resultado_final['etapas']['enriquecimento'] = etapa_enriquecimento
        
        # MS4: Localização de Pessoas
        logger.info("\n👥 [ETAPA 4/5] MS4 - LOCALIZAÇÃO DE DECISORES")
        logger.info("-"*80)
        etapa_pessoas = self._executar_busca_pessoas(leads_validos)
        resultado_final['etapas']['pessoas'] = etapa_pessoas
        
        pessoas_encontradas = etapa_pessoas['pessoas']
        
        # MS6: Geração de Emails
        if gerar_emails and pessoas_encontradas:
            logger.info("\n📧 [ETAPA 5/6] MS6 - GERAÇÃO DE EMAILS INTELIGENTES")
            logger.info("-"*80)
            etapa_emails = self._executar_geracao_emails(
                pessoas_encontradas,
                leads_validos,
                etapa_enriquecimento['dados_enriquecidos']
            )
            resultado_final['etapas']['emails'] = etapa_emails
            
            # MS7: Disparo de Emails
            if disparar_emails:
                logger.info("\n🚀 [ETAPA 6/6] MS7 - DISPARO DE EMAILS")
                logger.info("-"*80)
                etapa_disparo = self._executar_disparo_emails(etapa_emails['emails'])
                resultado_final['etapas']['disparo'] = etapa_disparo
            else:
                logger.info("\n🚀 [ETAPA 6/6] MS7 - DISPARO DE EMAILS pulado (disparar_emails=False)")
                resultado_final['etapas']['disparo'] = {
                    'status': 'pulado', 'enviados': 0, 'falhas': 0, 'resultados': []
                }
        
        # Resumo final
        logger.info("\n" + "="*80)
        logger.info("📊 RESUMO FINAL DO PIPELINE")
        logger.info("="*80)
        self._exibir_resumo(resultado_final)
        
        return resultado_final
    
    def _executar_extracao(
        self,
        query: str,
        cidade: str,
        estado: str,
        limite: int
    ) -> Dict[str, Any]:
        """MS1: Extração de leads."""
        logger.info(f"Extraindo leads: {query} em {cidade}...")
        
        try:
            # Usar API Demo para demo (sem custos)
            leads = self.extrator.extrair_com_api_demo(
                ramo=query,
                cidade=cidade,
                estado=estado,
                limite=limite
            )
            
            # A persistência agora ocorre APÓS a validação (MS2)
            
            return {
                'status': 'sucesso',
                'total_leads': len(leads),
                'persistidos': 0,
                'leads': leads,
                'detalhes': {}
            }
        
        except Exception as e:
            logger.error(f"Erro na extração: {e}")
            return {'status': 'erro', 'mensagem': str(e), 'leads': []}
    
    def _executar_validacao(self, leads: List[Empresa]) -> Dict[str, Any]:
        """MS2: Validação de dados."""
        logger.info(f"Validando {len(leads)} leads...")
        
        try:
            leads_validos, stats = self.validador.validar_lote(
                leads,
                remover_invalidas=True
            )
            
            logger.info(f"✓ {stats['total_validas']} leads válidos ({stats['taxa_validade']:.1f}%)")
            logger.info(f"✗ {stats['invalidas']} leads inválidos")
            logger.info(f"⚠️  {stats['duplicatas']} duplicatas")
            
            return {
                'status': 'sucesso',
                'leads_validos': leads_validos,
                'estatisticas': stats
            }
        
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return {'status': 'erro', 'mensagem': str(e), 'leads_validos': []}
    
    def _executar_enriquecimento(self, leads: List[Empresa]) -> Dict[str, Any]:
        """MS3: Enriquecimento de dados."""
        logger.info(f"Enriquecendo {len(leads)} leads com dados adicionais...")
        
        try:
            dados_enriquecidos = self.enriquecedor.enriquecer_lote(leads)
            
            logger.info(f"✓ {len(dados_enriquecidos)} leads enriquecidos")
            
            # Resumo de dados enriquecidos
            setores = {}
            for dado in dados_enriquecidos:
                setor = dado.setor_industria or 'Desconhecido'
                setores[setor] = setores.get(setor, 0) + 1
            
            logger.info(f"Setores encontrados: {setores}")
            
            return {
                'status': 'sucesso',
                'dados_enriquecidos': dados_enriquecidos,
                'setores': setores,
                'total': len(dados_enriquecidos)
            }
        
        except Exception as e:
            logger.error(f"Erro no enriquecimento: {e}")
            return {'status': 'erro', 'mensagem': str(e), 'dados_enriquecidos': []}
    
    def _executar_busca_pessoas(self, leads: List[Empresa]) -> Dict[str, Any]:
        """MS4: Localização de pessoas."""
        logger.info(f"Buscando decisores em {len(leads)} empresas...")
        
        try:
            todas_pessoas = []
            
            for empresa in leads:
                dominio = self._extrair_dominio(empresa.website)
                pessoas = self.finder.encontrar_decisores(
                    empresa_nome=empresa.nome,
                    dominio_website=dominio,
                    setor=empresa.ramo,
                    email_empresa=empresa.email
                )
                todas_pessoas.extend(pessoas)
            
            logger.info(f"✓ {len(todas_pessoas)} decisores encontrados")
            
            # Estatísticas
            cargos = {}
            for pessoa in todas_pessoas:
                cargo = pessoa.titulo
                cargos[cargo] = cargos.get(cargo, 0) + 1
            
            logger.info(f"Distribuição de cargos: {cargos}")
            
            return {
                'status': 'sucesso',
                'pessoas': todas_pessoas,
                'total': len(todas_pessoas),
                'distribuicao_cargos': cargos
            }
        
        except Exception as e:
            logger.error(f"Erro na busca de pessoas: {e}")
            return {'status': 'erro', 'mensagem': str(e), 'pessoas': []}
    
    def _executar_geracao_emails(
        self,
        pessoas: List[Pessoa],
        leads: List[Empresa],
        dados_enriquecidos: List[Any]
    ) -> Dict[str, Any]:
        """MS6: Geração de emails inteligentemente alinhada com os produtos."""
        logger.info(f"Gerando emails personalizados para {len(pessoas)} pessoas...")
        
        try:
            from services.lead_extractor.product_matcher import match_cdkteck_product
            emails_gerados = []
            
            # Map de lead por nome de empresa
            leads_map = {lead.nome: lead for lead in leads}
            
            # --- CORTE RÍGIDO (GUILHOTINA FINAL) ANTES DE GASTAR TOKENS DA IA ---
            pessoas_com_email = []
            for pessoa in pessoas:
                if pessoa.email and str(pessoa.email).strip() not in ("", "-", "—") and "@" in str(pessoa.email):
                    pessoas_com_email.append(pessoa)
                else:
                    logger.warning(f"❌ Lead Descartado: {pessoa.nome} na {pessoa.empresa_nome} (Motivo: Sem email válido para disparo)")
                    
            if not pessoas_com_email:
                logger.warning("🚫 Nenhum lead sobreviveu à Guilhotina Final (todos sem email). Cancelando MS6/MS7.")
                return {'status': 'sucesso', 'emails': [], 'total': 0, 'mensagem': 'Nenhum email válido encontrado.'}
            
            for pessoa in pessoas_com_email:
                # Encontrar lead correspondente
                lead = leads_map.get(pessoa.empresa_nome)
                if not lead:
                    continue
                
                # Encontrar dados enriquecidos
                dado_enriquecido = next(
                    (d for d in dados_enriquecidos if d.dominio_website in lead.website),
                    None
                )
                
                # Determinar o produto ANTES de gerar o email
                text_to_analyze = (lead.ramo or "Empresa") + " " + (dado_enriquecido.num_funcionarios if dado_enriquecido and dado_enriquecido.num_funcionarios else "PME")
                try:
                    match_result = match_cdkteck_product(lead_niche=lead.ramo, lead_summary=text_to_analyze)
                    nome_produto = match_result.get('produto', 'PapoDados')
                    proposta = match_result.get('proposta_valor', 'extrair insights através de Inteligência Artificial')
                except Exception:
                    nome_produto = "PapoDados"
                    proposta = "tomar melhores decisões baseadas em dados"

                email_vendedor = f"{nome_produto.lower()}@cdkteck.com.br"
                
                # Construir contexto
                contexto = ContextoEmail(
                    nome_pessoa=pessoa.nome,
                    cargo_pessoa=pessoa.cargo,
                    empresa_nome=lead.nome,
                    setor_empresa=lead.ramo,
                    empresa_vendedora_nome=f"Time {nome_produto}",
                    tamanho_empresa=dado_enriquecido.num_funcionarios if dado_enriquecido else None,
                    receita_empresa=dado_enriquecido.receita_anual if dado_enriquecido else None,
                    website_empresa=self._extrair_dominio(lead.website),
                    valor_proposto=proposta,
                    tipo_email=TipoEmail.PRIMEIRO_CONTATO,
                    vendedor_nome="Cidirclay Queiroz",
                    vendedor_email=email_vendedor,
                    cta_url=f"https://{nome_produto.lower()}.cdkteck.com.br"
                )
                contexto.destinatario_email = pessoa.email
                
                # Gerar email
                email = self.gerador_emails.gerar_email(contexto, usar_ia=False)
                
                # Renderizar HTML com Assinatura ANTES da exibição na UI
                from services.lead_extractor.smtp_dispatcher import ZOHO_SIGNATURE_HTML
                corpo_bruto = email.corpo
                if "<" not in corpo_bruto or ">" not in corpo_bruto:
                    corpo_bruto = corpo_bruto.replace('\n', '<br>')
                
                email.corpo = f"<html><body>{corpo_bruto}{ZOHO_SIGNATURE_HTML}</body></html>"
                
                emails_gerados.append(email.to_dict())
            
            logger.info(f"✓ {len(emails_gerados)} emails gerados")
            
            return {
                'status': 'sucesso',
                'emails': emails_gerados,
                'total': len(emails_gerados)
            }
        
        except Exception as e:
            logger.error(f"Erro na geração de emails: {e}")
            return {'status': 'erro', 'mensagem': str(e), 'emails': []}
    
    def _executar_disparo_emails(self, emails_gerados: List[Dict[str, Any]]) -> Dict[str, Any]:
        """MS7: Disparo de emails usando SMTP Dispatcher."""
        logger.info(f"Disparando {len(emails_gerados)} emails em lote...")
        
        try:
            lote_para_disparo = []
            for email_dados in emails_gerados:
                # Determinar o produto a partir do destinatário e metadados contextuais
                text_to_analyze = email_dados.get('assunto', '') + " " + email_dados.get('corpo', '')
                try:
                    match_result = match_cdkteck_product(lead_niche="B2B Generic", lead_summary=text_to_analyze)
                    nome_produto = match_result.get('produto')
                except Exception:
                    nome_produto = None
                
                lote_para_disparo.append({
                    'destinatario': email_dados.get('destinatario_email', ''),
                    'assunto': email_dados.get('assunto', ''),
                    'corpo_html': email_dados.get('corpo', ''),
                    'corpo_texto': email_dados.get('corpo', ''),
                    'produto_selecionado': nome_produto
                })
            
            resultados = self.dispatcher.disparar_lote(lote_para_disparo, parar_em_erro=False)
            
            sucessos = sum(1 for r in resultados if r.sucesso)
            
            logger.info(f"✓ {sucessos} de {len(resultados)} emails enviados com sucesso")
            
            return {
                'status': 'sucesso',
                'enviados': sucessos,
                'falhas': len(resultados) - sucessos,
                'resultados': [r.to_dict() for r in resultados]
            }
        
        except Exception as e:
            logger.error(f"Erro no disparo de emails: {e}")
            return {'status': 'erro', 'mensagem': str(e), 'enviados': 0, 'falhas': len(emails_gerados)}
    
    def _exibir_resumo(self, resultado: Dict[str, Any]):
        """Exibe resumo final do pipeline."""
        
        print("\n")
        print("╔════════════════════════════════════════════════════════════════════════════╗")
        print("║                    📊 RESULTADO FINAL DO PIPELINE 📊                       ║")
        print("╚════════════════════════════════════════════════════════════════════════════╝")
        
        etapas = resultado.get('etapas', {})
        
        # Extração
        if 'extracao' in etapas:
            ext = etapas['extracao']
            print(f"\n✅ [MS1] EXTRAÇÃO")
            print(f"   Leads extraídos: {ext.get('total_leads', 0)}")
            print(f"   Persistidos: {ext.get('persistidos', 0)}")
        
        # Validação
        if 'validacao' in etapas:
            val = etapas['validacao']
            print(f"\n✅ [MS2] VALIDAÇÃO")
            print(f"   Leads válidos: {len(val.get('leads_validos', []))}")
            stats = val.get('estatisticas', {})
            print(f"   Taxa de validade: {stats.get('taxa_validade', 0):.1f}%")
        
        # Enriquecimento
        if 'enriquecimento' in etapas:
            enr = etapas['enriquecimento']
            print(f"\n✅ [MS3] ENRIQUECIMENTO")
            print(f"   Leads enriquecidos: {enr.get('total', 0)}")
            print(f"   Setores: {enr.get('setores', {})}")
        
        # Pessoas
        if 'pessoas' in etapas:
            pes = etapas['pessoas']
            print(f"\n✅ [MS4] LOCALIZAÇÃO DE DECISORES")
            print(f"   Decisores encontrados: {pes.get('total', 0)}")
            print(f"   Cargos: {pes.get('distribuicao_cargos', {})}")
        
        # Emails
        if 'emails' in etapas:
            eml = etapas['emails']
            print(f"\n✅ [MS6] GERAÇÃO DE EMAILS")
            print(f"   Emails gerados: {eml.get('total', 0)}")
            
        # Disparo
        if 'disparo' in etapas:
            disp = etapas['disparo']
            print(f"\n🚀 [MS7] DISPARO SMTP")
            print(f"   Emails enviados: {disp.get('enviados', 0)}")
            print(f"   Falhas SMTP: {disp.get('falhas', 0)}")
        
        # Checar se houve algum erro crítico no pipeline
        teve_erro = any(etapa.get('status') == 'erro' for etapa in etapas.values() if isinstance(etapa, dict))
        
        print("\n" + "="*80)
        if teve_erro:
            print("⚠️ PIPELINE FINALIZADO COM FALTAS/ERROS.")
        else:
            print("🎉 PIPELINE EXECUTADO COM SUCESSO!")
        print("="*80 + "\n")
    
    @staticmethod
    def _extrair_dominio(website: str) -> str:
        """Extrai domínio de uma URL."""
        website = website.replace('https://', '').replace('http://', '')
        website = website.split('/')[0]
        return website


# Script de demonstração
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Criar pipeline
    pipeline = PipelineAutonomoB2B()
    
    # Executar pipeline completo
    resultado = pipeline.executar_pipeline_completo(
        query="restaurantes",
        cidade="São Paulo",
        estado="SP",
        limite_leads=10,
        gerar_emails=True
    )
    
    # Salvar resultado
    with open('resultado_pipeline.json', 'w', encoding='utf-8') as f:
        # Converter Pessoa objects para dict
        def converter(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return str(obj)
        
        json.dump(resultado, f, indent=2, ensure_ascii=False, default=converter)
    
    logger.info("✅ Resultado salvo em 'resultado_pipeline.json'")
