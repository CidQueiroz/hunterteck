"""
Configuração centralizada do microsserviço de extração de leads.
Gerencia variáveis de ambiente e parâmetros de execução.
"""

import os
from typing import Optional
from pathlib import Path


class Config:
    """Classe de configuração da aplicação."""
    
    # Diretórios
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Banco de dados
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", str(DATA_DIR / "leads.db"))
    DATABASE_BACKUP_DIR: str = os.getenv("DATABASE_BACKUP_DIR", str(DATA_DIR / "backups"))
    
    # Configurações de scraping
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_INTERVAL: float = float(os.getenv("REQUEST_INTERVAL", "1.0"))
    
    # User Agent
    USER_AGENT: str = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Execução
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    WORKERS: int = int(os.getenv("WORKERS", "4"))
    
    # APIs e serviços externos
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    LINKEDIN_API_KEY: Optional[str] = os.getenv("LINKEDIN_API_KEY")
    
    @classmethod
    def validar(cls) -> None:
        """Valida a configuração inicializada."""
        if cls.REQUEST_TIMEOUT < 1:
            raise ValueError("REQUEST_TIMEOUT deve ser >= 1")
        if cls.MAX_RETRIES < 1:
            raise ValueError("MAX_RETRIES deve ser >= 1")
        if cls.WORKERS < 1:
            raise ValueError("WORKERS deve ser >= 1")
    
    @classmethod
    def criar_diretorios(cls) -> None:
        """Cria os diretórios necessários."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        Path(cls.DATABASE_BACKUP_DIR).mkdir(parents=True, exist_ok=True)


# Criar diretórios na inicialização
Config.criar_diretorios()
Config.validar()
