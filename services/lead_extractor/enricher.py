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
        
        # Sem chaves de API reais (Clearbit/Hunter/Snovio), retornamos apenas o lead cru intacto.
        return DadosEnriquecidos(
            empresa_id=0,
            dominio_website=dominio,
            receita_anual=None,
            num_funcionarios=None,
            ano_fundacao=None,
            setor_industria=empresa.ramo.title() if empresa.ramo else 'Serviços',
            linkedin_url=f"https://linkedin.com/company/{dominio.split('.')[0]}",
            tags=[empresa.ramo.lower()] if empresa.ramo else ['serviços'],
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
                # Retornar intacto mesmo em erro
                dados = DadosEnriquecidos(
                    empresa_id=0,
                    dominio_website=self._extrair_dominio(empresa.website),
                    receita_anual=None,
                    num_funcionarios=None,
                    ano_fundacao=None,
                    setor_industria=empresa.ramo.title() if empresa.ramo else 'Serviços',
                    linkedin_url=f"https://linkedin.com/company/{self._extrair_dominio(empresa.website).split('.')[0]}",
                    tags=[empresa.ramo.lower()] if empresa.ramo else ['serviços'],
                    fonte_dados='manual'
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
