"""
Microsserviço 3: Enriquecedor de Dados
Coleta informações adicionais sobre empresas (receita, funcionários, etc)
para contexto mais rico em posteriores etapas de personalização.
"""

import logging
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime
import time

from lead_extractor.models import Empresa, LeadSource
from lead_extractor.config import Config


logger = logging.getLogger(__name__)


class EnricherError(Exception):
    """Exceção customizada para erros de enriquecimento."""
    pass


@dataclass
class DadosEnriquecidos:
    """Dados adicionais enriquecidos de uma empresa."""
    
    empresa_id: int
    dominio_website: str
    receita_anual: Optional[str] = None  # "1M", "10M", "100M", etc
    num_funcionarios: Optional[str] = None  # "1-10", "50-100", etc
    ano_fundacao: Optional[int] = None
    setor_industria: Optional[str] = None
    linkedin_url: Optional[str] = None
    facebook_url: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None
    descricao: Optional[str] = None
    tags: List[str] = None
    data_enriquecimento: datetime = None
    fonte_dados: str = "manual"  # demo, clearbit, apollo, hunter, manual
    
    def __post_init__(self):
        if self.data_enriquecimento is None:
            self.data_enriquecimento = datetime.now()
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        data = asdict(self)
        data['data_enriquecimento'] = self.data_enriquecimento.isoformat()
        return data


class EnriquecedorDados:
    """Enriquece dados de empresas com informações adicionais."""
    
    # URLs de APIs de enriquecimento simuladas
    URL_CLEARBIT = "https://api.clearbit.com/v1/companies/find"
    URL_HUNTER = "https://api.hunter.io/v2/domain-search"
    
    def __init__(self):
        """Inicializa o enriquecedor."""
        self.session = self._criar_sessao()
        logger.info("Enriquecedor de dados inicializado")
    
    def _criar_sessao(self) -> requests.Session:
        """Cria sessão HTTP com headers padrão."""
        sessao = requests.Session()
        sessao.headers.update({
            'User-Agent': Config.USER_AGENT,
            'Accept': 'application/json'
        })
        return sessao
    
    def enriquecer_empresa(self, empresa: Empresa) -> DadosEnriquecidos:
        """
        Enriquece dados de uma empresa.
        
        Args:
            empresa: Empresa a enriquecer
            
        Returns:
            Objeto DadosEnriquecidos
        """
        logger.info(f"Enriquecendo empresa: {empresa.nome}")
        
        dominio = self._extrair_dominio(empresa.website)
        
        # Tentar diferentes fontes de dados
        try:
            # Fonte 1: Clearbit (simulado para demo)
            dados = self._enriquecer_clearbit(dominio, empresa.nome)
            if dados:
                return dados
        except Exception as e:
            logger.debug(f"Clearbit falhou: {e}")
        
        try:
            # Fonte 2: Hunter (simulado para demo)
            dados = self._enriquecer_hunter(dominio)
            if dados:
                return dados
        except Exception as e:
            logger.debug(f"Hunter falhou: {e}")
        
        # Retornar dados mínimos se nada funcionou
        return self._enriquecer_minimo(dominio, empresa.nome)
    
    def _enriquecer_clearbit(self, dominio: str, nome_empresa: str) -> Optional[DadosEnriquecidos]:
        """
        Simula enriquecimento com Clearbit.
        Em produção, usar API real: https://clearbit.com
        
        Args:
            dominio: Domínio da empresa
            nome_empresa: Nome da empresa
            
        Returns:
            DadosEnriquecidos ou None
        """
        logger.debug(f"Tentando Clearbit para {dominio}")
        
        # Base de dados simulada de empresas conhecidas
        dados_conhecidos = {
            'google.com': {
                'receita_anual': '280B',
                'num_funcionarios': '190k+',
                'ano_fundacao': 1998,
                'setor_industria': 'Technology',
                'linkedin_url': 'https://linkedin.com/company/google',
                'descricao': 'Search Engine and Cloud Services'
            },
            'microsoft.com': {
                'receita_anual': '200B',
                'num_funcionarios': '220k+',
                'ano_fundacao': 1975,
                'setor_industria': 'Technology',
                'linkedin_url': 'https://linkedin.com/company/microsoft',
                'descricao': 'Software and Cloud Solutions'
            },
            'amazon.com': {
                'receita_anual': '575B',
                'num_funcionarios': '1.5M+',
                'ano_fundacao': 1994,
                'setor_industria': 'E-commerce, Cloud',
                'linkedin_url': 'https://linkedin.com/company/amazon',
                'descricao': 'E-commerce and Cloud Computing'
            }
        }
        
        if dominio in dados_conhecidos:
            dados_dict = dados_conhecidos[dominio]
            tags = [dados_dict.get('setor_industria', '').lower()]
            
            return DadosEnriquecidos(
                empresa_id=0,  # Será preenchido após inserção no DB
                dominio_website=dominio,
                receita_anual=dados_dict.get('receita_anual'),
                num_funcionarios=dados_dict.get('num_funcionarios'),
                ano_fundacao=dados_dict.get('ano_fundacao'),
                setor_industria=dados_dict.get('setor_industria'),
                linkedin_url=dados_dict.get('linkedin_url'),
                descricao=dados_dict.get('descricao'),
                tags=tags,
                fonte_dados='clearbit'
            )
        
        return None
    
    def _enriquecer_hunter(self, dominio: str) -> Optional[DadosEnriquecidos]:
        """
        Simula enriquecimento com Hunter.io.
        Em produção: https://hunter.io
        """
        logger.debug(f"Tentando Hunter para {dominio}")
        
        # Simulation: retornar padrão ou dados aleatórios
        # Em produção, seria uma chamada real à API
        
        return None
    
    def _enriquecer_minimo(self, dominio: str, nome_empresa: str) -> DadosEnriquecidos:
        """
        Enriquecimento mínimo com dados inferidos/padrão.
        
        Args:
            dominio: Domínio da empresa
            nome_empresa: Nome da empresa
            
        Returns:
            DadosEnriquecidos com dados mínimos
        """
        logger.debug(f"Enriquecimento mínimo para {dominio}")
        
        # Inferir setor pela extensão de domínio ou keywords
        setor = self._inferir_setor(nome_empresa, dominio)
        
        return DadosEnriquecidos(
            empresa_id=0,
            dominio_website=dominio,
            receita_anual=None,
            num_funcionarios=None,
            ano_fundacao=None,
            setor_industria=setor,
            linkedin_url=f"https://linkedin.com/company/{dominio.split('.')[0]}",
            tags=[setor.lower()],
            fonte_dados='manual'
        )
    
    def enriquecer_lote(
        self,
        empresas: List[Empresa],
        delay: float = 0.5
    ) -> List[DadosEnriquecidos]:
        """
        Enriquece um lote de empresas.
        
        Args:
            empresas: Lista de empresas
            delay: Delay entre requisições (s)
            
        Returns:
            Lista de dados enriquecidos
        """
        logger.info(f"Enriquecendo lote de {len(empresas)} empresas")
        
        dados_enriquecidos = []
        
        for i, empresa in enumerate(empresas, 1):
            try:
                dados = self.enriquecer_empresa(empresa)
                dados_enriquecidos.append(dados)
                
                # Respeitar rate limiting
                if i < len(empresas):
                    time.sleep(delay)
            
            except Exception as e:
                logger.error(f"Erro ao enriquecer {empresa.nome}: {e}")
                # Retornar enriquecimento mínimo mesmo em erro
                dados = self._enriquecer_minimo(
                    self._extrair_dominio(empresa.website),
                    empresa.nome
                )
                dados_enriquecidos.append(dados)
        
        logger.info(f"Enriquecimento de lote concluído: {len(dados_enriquecidos)} registros")
        return dados_enriquecidos
    
    @staticmethod
    def _extrair_dominio(website: str) -> str:
        """Extrai domínio de uma URL."""
        website = website.replace('https://', '').replace('http://', '')
        website = website.split('/')[0]
        return website
    
    @staticmethod
    def _inferir_setor(nome_empresa: str, dominio: str) -> str:
        """
        Infere o setor pelo nome ou domínio.
        
        Args:
            nome_empresa: Nome da empresa
            dominio: Domínio
            
        Returns:
            Setor inferido
        """
        nome_lower = nome_empresa.lower()
        dominio_lower = dominio.lower()
        
        # Keywords para detectar setor
        palavras_chave = {
            'tech': ['tech', 'software', 'app', 'digital', 'cyber'],
            'saúde': ['health', 'medical', 'clinic', 'dental', 'pharma', 'médic', 'dentista'],
            'varejo': ['store', 'shop', 'retail', 'loja', 'e-commerce'],
            'alimentos': ['food', 'restaurant', 'cafe', 'restaurant', 'padaria'],
            'imóvel': ['real', 'estate', 'imobil', 'property'],
            'educação': ['school', 'university', 'educ', 'academy', 'curso'],
            'fitness': ['gym', 'fitness', 'sport', 'academia'],
        }
        
        for setor, palavras in palavras_chave.items():
            for palavra in palavras:
                if palavra in nome_lower or palavra in dominio_lower:
                    return setor.title()
        
        return 'Serviços'  # Default


# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    from lead_extractor.models import LeadSource
    
    enriquecedor = EnriquecedorDados()
    
    # Teste
    empresa = Empresa(
        nome="Google Brazil",
        website="https://google.com.br",
        endereco="Avenida Paulista",
        cidade="São Paulo",
        estado="SP",
        ramo="Technology",
        fonte=LeadSource.API
    )
    
    print("\n🔄 Enriquecendo empresa...")
    dados = enriquecedor.enriquecer_empresa(empresa)
    print(f"✅ Dados enriquecidos: {dados.to_dict()}")
