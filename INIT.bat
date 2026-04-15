@echo off
REM ============================================================================
REM SCRIPT DE INICIALIZAÇÃO - HUNTERTECK (Windows)
REM Automatiza a configuração completa do projeto HunterTeck
REM ============================================================================

setlocal enabledelayedexpansion

title HunterTeck - Inicializacao
color 0A

REM ============================================================================
REM FUNÇÕES AUXILIARES
REM ============================================================================

echo.
echo ========================================
echo HUNTERTECK - Script de Inicializacao
echo ========================================
echo.

REM ============================================================================
REM VERIFICACAO DE PRE-REQUISITOS
REM ============================================================================

echo [*] Etapa 1: Verificando pre-requisitos...
echo.

where python >nul 2>nul
if errorlevel 1 (
    color 0C
    echo [X] Python nao encontrado. Instale Python 3.9+ de https://www.python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% encontrado

where pip >nul 2>nul
if errorlevel 1 (
    color 0C
    echo [X] pip nao encontrado
    pause
    exit /b 1
)
echo [OK] pip encontrado

where git >nul 2>nul
if errorlevel 1 (
    echo [AVISO] git nao encontrado (opcional)
)

echo.

REM ============================================================================
REM SETUP DE DIRETORIOS
REM ============================================================================

echo [*] Etapa 2: Configurando diretorios...
echo.

if not exist "data" mkdir data
echo [OK] Diretorio data criado/verificado

if not exist "data\backups" mkdir data\backups
echo [OK] Diretorio data\backups criado/verificado

if not exist "logs" mkdir logs
echo [OK] Diretorio logs criado/verificado

echo.

REM ============================================================================
REM CONFIGURACAO DE VARIAVEIS DE AMBIENTE
REM ============================================================================

echo [*] Etapa 3: Configurando variaveis de ambiente...
echo.

if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo [OK] .env criado a partir de .env.example
        color 0E
        echo [AVISO] IMPORTANTE: Edite .env e configure suas chaves de API (GROQ_API_KEY, etc)
        color 0A
    ) else (
        (
            echo # HunterTeck Environment Variables
            echo GROQ_API_KEY=gsk_YOUR_API_KEY_HERE
            echo DATABASE_PATH=data/leads.db
            echo DATABASE_BACKUP_DIR=data/backups
            echo LOG_LEVEL=INFO
            echo REQUEST_TIMEOUT=30
            echo MAX_RETRIES=3
            echo REQUEST_INTERVAL=1.0
            echo DEBUG=False
            echo WORKERS=4
        ) > .env
        color 0E
        echo [AVISO] .env criado. Configure GROQ_API_KEY e outras chaves!
        color 0A
    )
) else (
    echo [OK] .env ja existe
)

echo.

REM ============================================================================
REM CRIACAO DE VENV
REM ============================================================================

echo [*] Etapa 4: Configurando ambiente virtual...
echo.

if not exist "venv" (
    echo [*] Criando ambiente virtual...
    python -m venv venv
    echo [OK] Ambiente virtual criado
) else (
    echo [OK] Ambiente virtual ja existe
)

REM Ativar venv
call venv\Scripts\activate.bat
echo [OK] Ambiente virtual ativado

echo.

REM ============================================================================
REM INSTALACAO DE DEPENDENCIAS
REM ============================================================================

echo [*] Etapa 5: Instalando dependencias Python...
echo.

echo [*] Atualizando pip, setuptools, wheel...
python -m pip install --upgrade pip setuptools wheel

echo [*] Instalando dependencias do pyproject.toml...
pip install -e ".[dev,groq]"

if errorlevel 1 (
    color 0C
    echo [X] Erro ao instalar dependencias
    pause
    exit /b 1
)

echo [OK] Dependencias instaladas com sucesso
echo.

REM ============================================================================
REM SETUP DO BANCO DE DADOS
REM ============================================================================

echo [*] Etapa 6: Inicializando banco de dados...
echo.

python << 'PYTHON_EOF'
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

try:
    from services.lead_extractor.database import DatabaseConnection
    from services.lead_extractor.config import Config
    
    Config.validar()
    db = DatabaseConnection(Config.DATABASE_PATH)
    db.criar_tabelas()
    
    print(f"[OK] Banco de dados criado em: {Config.DATABASE_PATH}")
    print(f"[OK] Backup dir: {Config.DATABASE_BACKUP_DIR}")
    
except Exception as e:
    print(f"[X] Erro ao inicializar BD: {e}")
    sys.exit(1)
PYTHON_EOF

echo.

REM ============================================================================
REM VERIFICACOES FINAIS
REM ============================================================================

echo [*] Etapa 7: Verificacoes finais...
echo.

python << 'PYTHON_EOF'
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

print("Verificando imports do projeto...")

try:
    from services.lead_extractor.config import Config
    print("  [OK] Config")
    from services.lead_extractor.database import DatabaseConnection
    print("  [OK] DatabaseConnection")
    from services.lead_extractor.models import Empresa, LeadStatus
    print("  [OK] Models")
    from services.lead_extractor.main import PipelineExtracao
    print("  [OK] PipelineExtracao")
    from orquestrador import PipelineAutonomoB2B
    print("  [OK] PipelineAutonomoB2B")
    print("\n[OK] Todos os imports estao OK!")
except ImportError as e:
    print(f"\n[X] Erro de import: {e}")
    sys.exit(1)
PYTHON_EOF

echo.

REM ============================================================================
REM RESUMO E PROXIMAS ETAPAS
REM ============================================================================

echo.
color 0B
echo ==========================================
echo [OK] INICIALIZACAO CONCLUIDA COM SUCESSO!
echo ==========================================
color 0A
echo.

echo Proximos passos:
echo   1. Editar .env com suas chaves de API (especialmente GROQ_API_KEY)
echo   2. Executar: python app_hunter.py
echo      Ou: streamlit run app_hunter.py
echo   3. Executar pipeline: python orquestrador.py
echo   4. Ver documentacao: type QUICK_START.md
echo.

echo Estrutura de Diretorios:
echo   data\            - Banco de dados SQLite e backups
echo   logs\            - Arquivos de log
echo   services\        - Microsservicos (MS1-MS7)
echo   backend\         - API backend (se aplicavel)
echo   frontend\        - Interface Streamlit
echo.

echo Comandos Uteis:
echo   docker-compose up      - Iniciar com Docker
echo   python -m pytest       - Executar testes
echo.

color 0B
echo [OK] Pronto para comecar!
color 0A
echo.

pause
