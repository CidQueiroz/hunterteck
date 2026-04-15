#!/bin/bash

################################################################################
# SCRIPT DE INICIALIZAÇÃO - HUNTERTECK
# Automatiza a configuração completa do projeto HunterTeck
# Executa: verificações de ambiente, instalação de dependências e setup de BD
################################################################################

set -e  # Exits on error

# Cores para output legível
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

check_command() {
    if command -v $1 &> /dev/null; then
        log_success "$1 encontrado"
        return 0
    else
        log_error "$1 não encontrado"
        return 1
    fi
}

# ============================================================================
# VERIFICAÇÕES DE PRÉ-REQUISITOS
# ============================================================================

log_info "=========================================="
log_info "HUNTERTECK - Script de Inicialização"
log_info "=========================================="
echo

log_info "Etapa 1: Verificando pré-requisitos..."
echo

PREREQS_OK=true

if ! check_command python3; then
    PREREQS_OK=false
fi

if ! check_command pip; then
    PREREQS_OK=false
fi

if ! check_command git; then
    PREREQS_OK=false
fi

# Verificar versão do Python (3.9+)
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
MIN_MAJOR=3
MIN_MINOR=9

# Extrair major e minor version
MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

# Comparar versão
if [ "$MAJOR" -gt "$MIN_MAJOR" ] || ([ "$MAJOR" -eq "$MIN_MAJOR" ] && [ "$MINOR" -ge "$MIN_MINOR" ]); then
    log_success "Python $PYTHON_VERSION (>= $MIN_MAJOR.$MIN_MINOR)"
else
    log_error "Python $PYTHON_VERSION. Requer >=$MIN_MAJOR.$MIN_MINOR"
    PREREQS_OK=false
fi

if [ "$PREREQS_OK" = false ]; then
    log_error "Pré-requisitos não atendidos. Instalação cancelada."
    exit 1
fi

echo

# ============================================================================
# SETUP DE DIRETÓRIOS
# ============================================================================

log_info "Etapa 2: Configurando diretórios..."
echo

PROJECT_DIR=$(pwd)
cd "$PROJECT_DIR"

# Criar diretórios necessários
mkdir -p data/backups logs
chmod -R 755 data logs

log_success "Diretórios criados/verificados:"
log_success "  - $PROJECT_DIR/data"
log_success "  - $PROJECT_DIR/data/backups"
log_success "  - $PROJECT_DIR/logs"

echo

# ============================================================================
# CONFIGURAÇÃO DE VARIÁVEIS DE AMBIENTE
# ============================================================================

log_info "Etapa 3: Configurando variáveis de ambiente..."
echo

if [ ! -f .env ]; then
    log_warning ".env não encontrado. Copiando de .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        log_success ".env criado a partir de .env.example"
        log_warning "⚠ IMPORTANTE: Edite .env e configure suas chaves de API (GROQ_API_KEY, etc)"
    else
        log_error ".env.example não encontrado. Criando .env padrão..."
        cat > .env << 'EOF'
# HunterTeck Environment Variables
GROQ_API_KEY=gsk_YOUR_API_KEY_HERE
DATABASE_PATH=data/leads.db
DATABASE_BACKUP_DIR=data/backups
LOG_LEVEL=INFO
REQUEST_TIMEOUT=30
MAX_RETRIES=3
REQUEST_INTERVAL=1.0
DEBUG=False
WORKERS=4
EOF
        log_warning "⚠ IMPORTANTE: Inicie GROQ_API_KEY em .env"
    fi
else
    log_success ".env já existe"
fi

echo

# ============================================================================
# CRIAÇÃO DE VENV (OPCIONAL)
# ============================================================================

log_info "Etapa 4: Configurando ambiente virtual (opcional)..."
echo

if [ ! -d venv ]; then
    log_info "Criando ambiente virtual..."
    python3 -m venv venv
    log_success "Ambiente virtual criado"
else
    log_success "Ambiente virtual já existe"
fi

# Ativar venv
source venv/bin/activate
log_success "Ambiente virtual ativado"

echo

# ============================================================================
# INSTALAÇÃO DE DEPENDÊNCIAS
# ============================================================================

log_info "Etapa 5: Instalando dependências Python..."
echo

log_info "Atualizando pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

log_info "Instalando dependências do pyproject.toml..."
pip install -e ".[dev,groq]"

log_success "Dependências instaladas com sucesso"

echo

# ============================================================================
# SETUP DO BANCO DE DADOS
# ============================================================================

log_info "Etapa 6: Inicializando banco de dados..."
echo

python3 << 'PYTHON_EOF'
import sys
from pathlib import Path

# Adicionar project ao path
sys.path.insert(0, str(Path.cwd()))

try:
    from services.lead_extractor.database import DatabaseConnection
    from services.lead_extractor.config import Config
    
    # Validar config
    Config.validar()
    
    db = DatabaseConnection(Config.DATABASE_PATH)
    db.criar_tabelas()
    
    print(f"✓ Banco de dados criado em: {Config.DATABASE_PATH}")
    print(f"✓ Backup dir: {Config.DATABASE_BACKUP_DIR}")
    
except Exception as e:
    print(f"✗ Erro ao inicializar BD: {e}")
    sys.exit(1)
PYTHON_EOF

echo

# ============================================================================
# VERIFICAÇÕES FINAIS
# ============================================================================

log_info "Etapa 7: Verificações finais..."
echo

# Testar imports básicos
python3 << 'PYTHON_EOF'
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

print("Verificando imports do projeto...")

try:
    from services.lead_extractor.config import Config
    print("  ✓ Config")
    from services.lead_extractor.database import DatabaseConnection
    print("  ✓ DatabaseConnection")
    from services.lead_extractor.models import Empresa, LeadStatus
    print("  ✓ Models")
    from services.lead_extractor.main import PipelineExtracao
    print("  ✓ PipelineExtracao")
    from orquestrador import PipelineAutonomoB2B
    print("  ✓ PipelineAutonomoB2B")
    print("\n✓ Todos os imports estão OK!")
except ImportError as e:
    print(f"\n✗ Erro de import: {e}")
    sys.exit(1)
PYTHON_EOF

echo

# ============================================================================
# RESUMO E PRÓXIMAS ETAPAS
# ============================================================================

echo
log_success "=========================================="
log_success "INICIALIZAÇÃO CONCLUÍDA COM SUCESSO!"
log_success "=========================================="
echo

echo -e "${BLUE}Próximos passos:${NC}"
echo "  1. Editar .env com suas chaves de API (especialmente GROQ_API_KEY)"
echo "  2. Executar: python app_hunter.py"
echo "     Ou: streamlit run app_hunter.py"
echo "  3. Executar pipeline: python orquestrador.py"
echo "  4. Ver documentação: cat QUICK_START.md"
echo

echo -e "${BLUE}Estrutura de Diretórios:${NC}"
echo "  data/           - Banco de dados SQLite e backups"
echo "  logs/           - Arquivos de log"
echo "  services/       - Microsserviços (MS1-MS7)"
echo "  backend/        - API backend (se aplicável)"
echo "  frontend/       - Interface Streamlit"
echo

echo -e "${BLUE}Comandos Úteis:${NC}"
echo "  make help              - Ver todos os targets do Makefile"
echo "  docker-compose up      - Iniciar com Docker"
echo "  python -m pytest       - Executar testes"
echo

log_success "Pronto para começar!"
echo
