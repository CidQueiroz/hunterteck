"""
Microsserviço de Extração de Leads - Pacote principal.
Pipeline B2B autônomo para prospecção de empresas locais.
"""

__version__ = "2.0.0"
__author__ = "SDR Agent"
__description__ = "Microsserviço autonomo de extração e persistência de leads B2B com geração de emails e roteamento dinâmico"

from .models import Empresa, LeadSource, LeadStatus, ExtratorConfig
from .database import DatabaseConnection, DatabaseError
from .extractors import (
    ExtratorBase,
    ExtratorGoogleMaps,
    ExtratorWebScrape,
    ExtratorAPIDemo,
    ExtratorError
)
from .main import PipelineExtracao
from .product_matcher import (
    match_cdkteck_product,
    ClassificadorProdutos,
    ProdutoCDKTeck,
    ProdutoInfo,
    CatalogoProdutos
)
from .email_generator import (
    GeradorEmails,
    ContextoEmail,
    EmailGerado,
    TipoEmail
)
from .smtp_dispatcher import (
    DispachadorSMTPProdutos,
    ConfiguracaoSMTP,
    MapeamentoAliases,
    ResultadoDisparo,
    StatusDisparo,
    ProvedorSMTP
)

__all__ = [
    # Modelos e status
    "Empresa",
    "LeadSource",
    "LeadStatus",
    "ExtratorConfig",
    # Database
    "DatabaseConnection",
    "DatabaseError",
    # Extractors
    "ExtratorBase",
    "ExtratorGoogleMaps",
    "ExtratorWebScrape",
    "ExtratorAPIDemo",
    "ExtratorError",
    # Pipeline
    "PipelineExtracao",
    # Product Matcher
    "match_cdkteck_product",
    "ClassificadorProdutos",
    "ProdutoCDKTeck",
    "ProdutoInfo",
    "CatalogoProdutos",
    # Email Generator
    "GeradorEmails",
    "ContextoEmail",
    "EmailGerado",
    "TipoEmail",
    # SMTP Dispatcher (NOVO)
    "DispachadorSMTPProdutos",
    "ConfiguracaoSMTP",
    "MapeamentoAliases",
    "ResultadoDisparo",
    "StatusDisparo",
    "ProvedorSMTP",
]
