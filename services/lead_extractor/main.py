"""
Microsserviço de Extração de Leads - Ponto de entrada principal.
Orquestra a coleta de dados, validação e persistência em SQLite.
"""

import logging
import sys
import json
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from .models import Empresa, LeadSource, LeadStatus, ExtratorConfig
from .database import DatabaseConnection, DatabaseError
from .extractors import (
    ExtratorGoogleMaps,
    ExtratorWebScrape,
    ExtratorAPIDemo,
    ExtratorError
)
from .config import Config


# Configurar logging
def _configurar_logging():
    """Configura o sistema de logging da aplicação."""
    log_format = logging.Formatter(Config.LOG_FORMAT)
    
    # Handler para arquivo
    log_dir = Path(Config.LOGS_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(
        log_dir / f"lead_extractor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    file_handler.setFormatter(log_format)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(Config.LOG_LEVEL)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


logger = logging.getLogger(__name__)


class PipelineExtracao:
    """Pipeline completo de extração de leads."""
    
    def __init__(self):
        """Inicializa o pipeline de extração."""
        self.db = DatabaseConnection()
        self.db.criar_tabelas()
        self.config_extrator = ExtratorConfig(
            timeout_segundos=Config.REQUEST_TIMEOUT,
            max_tentativas=Config.MAX_RETRIES,
            intervalo_requisicoes=Config.REQUEST_INTERVAL,
            banco_dados=Config.DATABASE_PATH
        )
        logger.info("Pipeline de extração inicializado")
    
    def extrair_com_google_maps(
        self,
        query: str,
        cidade: str,
        estado: str,
        limite: int = 20
    ) -> List[Empresa]:
        """
        Extrai leads usando Google Maps API.
        
        Args:
            query: Termo de busca
            cidade: Cidade alvo
            estado: Estado alvo
            limite: Número máximo de resultados
            
        Returns:
            Lista de empresas extraídas
        """
        try:
            logger.info(f"Iniciando extração Google Maps: {query} em {cidade}, {estado}")
            extrator = ExtratorGoogleMaps(config=self.config_extrator)
            empresas = extrator.extrair(
                query=query,
                cidade=cidade,
                estado=estado,
                limite=limite
            )
            logger.info(f"Extração completada: {len(empresas)} leads obtidos")
            return empresas
        except ExtratorError as e:
            logger.error(f"Erro na extração Google Maps: {e}")
            return []
    
    def extrair_com_web_scraping(
        self,
        url_base: str,
        ramo: str,
        cidade: str,
        estado: str,
        seletores: Dict[str, str]
    ) -> List[Empresa]:
        """
        Extrai leads via web scraping.
        
        Args:
            url_base: URL para scraping
            ramo: Categoria de negócio
            cidade: Cidade
            estado: Estado
            seletores: Dicionário com seletores CSS
            
        Returns:
            Lista de empresas extraídas
        """
        try:
            logger.info(f"Iniciando web scraping: {url_base}")
            extrator = ExtratorWebScrape(config=self.config_extrator)
            empresas = extrator.extrair(
                url_base=url_base,
                ramo=ramo,
                cidade=cidade,
                estado=estado,
                seletores=seletores
            )
            logger.info(f"Scraping completado: {len(empresas)} leads obtidos")
            return empresas
        except ExtratorError as e:
            logger.error(f"Erro no scraping: {e}")
            return []
    
    def extrair_com_api_demo(
        self,
        ramo: str,
        cidade: str,
        estado: str
    ) -> List[Empresa]:
        """
        Extrai leads usando API de demonstração (sem custos).
        
        Args:
            ramo: Categoria de negócio
            cidade: Cidade
            estado: Estado
            
        Returns:
            Lista de empresas de demonstração
        """
        try:
            logger.info(f"Iniciando extração API Demo: {ramo}")
            extrator = ExtratorAPIDemo(config=self.config_extrator)
            empresas = extrator.extrair(
                ramo=ramo,
                cidade=cidade,
                estado=estado
            )
            logger.info(f"Extração API Demo completada: {len(empresas)} leads")
            return empresas
        except ExtratorError as e:
            logger.error(f"Erro na extração API Demo: {e}")
            return []
    
    def persistir_leads(self, empresas: List[Empresa]) -> Dict[str, Any]:
        """
        Persiste uma lista de leads no banco de dados.
        
        Args:
            empresas: Lista de empresas para persistir
            
        Returns:
            Dicionário com resultado da operação
        """
        if not empresas:
            logger.warning("Nenhuma empresa para persistir")
            return {'status': 'erro', 'mensagem': 'Lista vazia', 'total': 0, 'sucesso': 0}
        
        try:
            logger.info(f"Persistindo {len(empresas)} empresas no banco de dados")
            total, sucesso = self.db.inserir_empresas_em_lote(empresas)
            
            resultado = {
                'status': 'sucesso',
                'mensagem': f'{sucesso}/{total} empresas persistidas',
                'total': total,
                'sucesso': sucesso,
                'timestamp': datetime.now().isoformat()
            }
            logger.info(f"Persistência completada: {resultado}")
            return resultado
            
        except DatabaseError as e:
            logger.error(f"Erro ao persistir dados: {e}")
            return {'status': 'erro', 'mensagem': str(e), 'total': len(empresas), 'sucesso': 0}
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco de dados."""
        try:
            stats = self.db.obter_estatisticas()
            logger.debug(f"Estatísticas obtidas: {stats}")
            return stats
        except DatabaseError as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def listar_leads_recentes(self, limite: int = 50) -> List[Dict[str, Any]]:
        """Lista os leads mais recentes."""
        try:
            empresas = self.db.listar_todas_empresas(limite=limite)
            return [empresa.to_dict() for empresa in empresas]
        except DatabaseError as e:
            logger.error(f"Erro ao listar leads: {e}")
            return []


def exemplo_completo():
    """Exemplo de uso completo do pipeline."""
    print("\n" + "="*80)
    print("MICROSSERVIÇO DE EXTRAÇÃO DE LEADS - EXEMPLO DE USO")
    print("="*80 + "\n")
    
    pipeline = PipelineExtracao()
    
    # Exemplo 1: Extração com API Demo (sem custos)
    print("[1] Extração com API Demo - Restaurantes em São Paulo")
    print("-" * 80)
    empresas_api = pipeline.extrair_com_api_demo(
        ramo="restaurantes",
        cidade="São Paulo",
        estado="SP"
    )
    
    if empresas_api:
        print(f"✓ {len(empresas_api)} restaurantes encontrados\n")
        for empresa in empresas_api[:3]:
            print(f"  - {empresa.nome}")
            print(f"    Website: {empresa.website}")
            print(f"    Telefone: {empresa.telefone}\n")
    
    # Persistir dados
    resultado = pipeline.persistir_leads(empresas_api)
    print(f"Resultado da persistência: {resultado['mensagem']}\n")
    
    # Exemplo 2: Mais dados de outro ramo
    print("[2] Extração com API Demo - Lojas")
    print("-" * 80)
    empresas_lojas = pipeline.extrair_com_api_demo(
        ramo="lojas",
        cidade="Rio de Janeiro",
        estado="RJ"
    )
    
    if empresas_lojas:
        print(f"✓ {len(empresas_lojas)} lojas encontradas")
        resultado = pipeline.persistir_leads(empresas_lojas)
        print(f"Resultado da persistência: {resultado['mensagem']}\n")
    
    # Exibir estatísticas
    print("[3] Estatísticas do Banco de Dados")
    print("-" * 80)
    stats = pipeline.obter_estatisticas()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # Listar leads recentes
    print("\n[4] Leads Recentes (últimas 10)")
    print("-" * 80)
    leads_recentes = pipeline.listar_leads_recentes(limite=10)
    for lead in leads_recentes:
        print(f"  - {lead['nome']} ({lead['cidade']}, {lead['estado']})")
        print(f"    Status: {lead['status']} | Fonte: {lead['fonte']}")
    
    print("\n" + "="*80)
    print("EXEMPLO CONCLUÍDO COM SUCESSO!")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Configurar logging
    _configurar_logging()
    
    logger.info("="*80)
    logger.info("INICIANDO MICROSSERVIÇO DE EXTRAÇÃO DE LEADS")
    logger.info("="*80)
    
    try:
        exemplo_completo()
    except KeyboardInterrupt:
        logger.info("Pipeline interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Erro crítico: {e}", exc_info=True)
        sys.exit(1)
