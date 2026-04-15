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
        
        logger.info("✅ Todos os microsserviços inicializados")
    
    def executar_pipeline_completo(
        self,
        query: str,
        cidade: str,
        estado: str,
        limite_leads: int = 50,
        gerar_emails: bool = True
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
            logger.info("\n📧 [ETAPA 5/5] MS6 - GERAÇÃO DE EMAILS INTELIGENTES")
            logger.info("-"*80)
            etapa_emails = self._executar_geracao_emails(
                pessoas_encontradas,
                leads_validos,
                etapa_enriquecimento['dados_enriquecidos']
            )
            resultado_final['etapas']['emails'] = etapa_emails
        
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
                estado=estado
            )
            
            # Persistir no banco
            resultado = self.extrator.persistir_leads(leads)
            
            return {
                'status': 'sucesso',
                'total_leads': len(leads),
                'persistidos': resultado['sucesso'],
                'leads': leads,
                'detalhes': resultado
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
            
            for empresa in leads[:10]:  # Limitar a 10 para demo
                dominio = self._extrair_dominio(empresa.website)
                pessoas = self.finder.encontrar_decisores(
                    empresa_nome=empresa.nome,
                    dominio_website=dominio,
                    setor=empresa.ramo
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
        """MS6: Geração de emails."""
        logger.info(f"Gerando emails personalizados para {len(pessoas)} pessoas...")
        
        try:
            emails_gerados = []
            
            # Map de lead por nome de empresa
            leads_map = {lead.nome: lead for lead in leads}
            
            for pessoa in pessoas[:20]:  # Limitar para demo
                # Encontrar lead correspondente
                lead = leads_map.get(pessoa.empresa_nome)
                if not lead:
                    continue
                
                # Encontrar dados enriquecidos
                dado_enriquecido = next(
                    (d for d in dados_enriquecidos if d.dominio_website in lead.website),
                    None
                )
                
                # Construir contexto
                contexto = ContextoEmail(
                    nome_pessoa=pessoa.nome,
                    cargo_pessoa=pessoa.cargo,
                    empresa_nome=lead.nome,
                    setor_empresa=lead.ramo,
                    tamanho_empresa=dado_enriquecido.num_funcionarios if dado_enriquecido else None,
                    receita_empresa=dado_enriquecido.receita_anual if dado_enriquecido else None,
                    website_empresa=self._extrair_dominio(lead.website),
                    valor_proposto="aumentar eficiência operacional",
                    tipo_email=TipoEmail.PRIMEIRO_CONTATO,
                    vendedor_nome="Time de Vendas",
                    vendedor_email="vendas@ourcompany.com"
                )
                contexto.destinatario_email = pessoa.email
                
                # Gerar email
                email = self.gerador_emails.gerar_email(contexto, usar_ia=False)
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
        
        print("\n" + "="*80)
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
