"""
Modelos de dados para o microsserviço de extração de leads.
Utiliza dataclasses com tipagem estática para garantir integridade dos dados.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from enum import Enum


class LeadSource(str, Enum):
    """Enumeração das fontes de coleta de leads."""
    GOOGLE_MAPS = "google_maps"
    YELLOWPAGES = "yellowpages"
    LINKEDIN = "linkedin"
    WEB_SCRAPE = "web_scrape"
    API = "api"
    DADOS_ESTRUTURADOS = "dados_estruturados"


class LeadStatus(str, Enum):
    """Estados possíveis de um lead."""
    NOVO = "novo"
    QUALIFICADO = "qualificado"
    EMAIL_VALIDADO = "email_validado"
    CONTATO_REALIZADO = "contato_realizado"
    DESCARTADO = "descartado"


@dataclass
class Empresa:
    """
    Modelo que representa uma empresa/lead coletada.
    
    Attributes:
        nome: Nome da empresa
        website: URL do website da empresa
        email: Email de contato (opcional)
        telefone: Número de telefone (opcional)
        endereco: Endereço da empresa
        cidade: Município onde a empresa está localizada
        estado: Estado/Região
        ramo: Setor/Indústria
        fonte: Origem da coleta (Google Maps, LinkedIn, etc)
        status: Status atual do lead
        data_coleta: Data e hora da coleta
        ultima_atualizacao: Última atualização do registro
    """
    nome: str
    website: str
    endereco: str
    cidade: str
    estado: str
    ramo: str
    fonte: LeadSource
    email: Optional[str] = None
    telefone: Optional[str] = None
    status: LeadStatus = LeadStatus.NOVO
    data_coleta: datetime = None
    ultima_atualizacao: Optional[datetime] = None
    
    def __post_init__(self):
        """Valida os dados da empresa após inicialização."""
        if self.data_coleta is None:
            self.data_coleta = datetime.now()
        if self.ultima_atualizacao is None:
            self.ultima_atualizacao = datetime.now()
        
        # Validações básicas
        if not self.nome or not isinstance(self.nome, str):
            raise ValueError("Nome da empresa deve ser uma string não vazia")
        if not self.website or not isinstance(self.website, str):
            raise ValueError("Website deve ser uma string não vazia")
        if not self.cidade or not isinstance(self.cidade, str):
            raise ValueError("Cidade deve ser uma string não vazia")
    
    def to_dict(self) -> dict:
        """Converte a empresa para dicionário."""
        data = asdict(self)
        data['fonte'] = self.fonte.value
        data['status'] = self.status.value
        data['data_coleta'] = self.data_coleta.isoformat() if isinstance(self.data_coleta, datetime) else self.data_coleta
        data['ultima_atualizacao'] = self.ultima_atualizacao.isoformat() if isinstance(self.ultima_atualizacao, datetime) else self.ultima_atualizacao
        return data


@dataclass
class ExtratorConfig:
    """Configurações do extrator de leads."""
    timeout_segundos: int = 30
    max_tentativas: int = 3
    intervalo_requisicoes: float = 1.0  # segundos entre requisições
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    banco_dados: str = "leads.db"
    
    def validar(self) -> None:
        """Valida as configurações."""
        if self.timeout_segundos < 1:
            raise ValueError("timeout_segundos deve ser >= 1")
        if self.max_tentativas < 1:
            raise ValueError("max_tentativas deve ser >= 1")
        if self.intervalo_requisicoes < 0:
            raise ValueError("intervalo_requisicoes não pode ser negativo")
