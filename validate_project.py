#!/usr/bin/env python3
"""
HUNTERTECK - Validador de Projeto
Diagnostica problemas, verifica integridade e valida configuração
Executar: python validate_project.py
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Tuple
import importlib.util

# Cores para terminal
class Colors:
    OK = '\033[92m'      # Verde
    WARNING = '\033[93m'  # Amarelo
    ERROR = '\033[91m'    # Vermelho
    INFO = '\033[94m'     # Azul
    RESET = '\033[0m'     # Reset

def print_ok(msg: str):
    print(f"{Colors.OK}[✓]{Colors.RESET} {msg}")

def print_warning(msg: str):
    print(f"{Colors.WARNING}[⚠]{Colors.RESET} {msg}")

def print_error(msg: str):
    print(f"{Colors.ERROR}[✗]{Colors.RESET} {msg}")

def print_info(msg: str):
    print(f"{Colors.INFO}[i]{Colors.RESET} {msg}")

def print_header(title: str):
    print(f"\n{Colors.INFO}{'='*50}{Colors.RESET}")
    print(f"{Colors.INFO}{title.center(50)}{Colors.RESET}")
    print(f"{Colors.INFO}{'='*50}{Colors.RESET}\n")

# ==============================================================================
# VALIDADORES
# ==============================================================================

def validate_project_structure() -> Tuple[bool, List[str]]:
    """Valida estrutura de diretórios"""
    print_header("1. ESTRUTURA DE DIRETÓRIOS")
    
    required_dirs = [
        'services/lead_extractor',
        'backend',
        'frontend',
        'deployment/docker',
        'data',
        'logs',
        'docs'
    ]
    
    required_files = [
        '.env.example',
        'pyproject.toml',
        'docker-compose.yml',
        'app_hunter.py',
        'orquestrador.py',
        'README.md',
    ]
    
    issues = []
    status = True
    
    # Verificar diretórios
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_ok(f"Diretório: {dir_path}")
        else:
            print_warning(f"Diretório: {dir_path} (não encontrado)")
            if dir_path not in ['data', 'logs']:  # data e logs podem não existir pre-init
                issues.append(f"Diretório ausente: {dir_path}")
                status = False
    
    print()
    
    # Verificar arquivos
    for file_path in required_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            size_kb = size / 1024
            print_ok(f"Arquivo: {file_path} ({size_kb:.1f}KB)")
        else:
            print_error(f"Arquivo: {file_path} (AUSENTE)")
            issues.append(f"Arquivo ausente: {file_path}")
            status = False
    
    return status, issues

def validate_imports() -> Tuple[bool, List[str]]:
    """Valida se os imports funcionam"""
    print_header("2. VALIDAÇÃO DE IMPORTS")
    
    sys.path.insert(0, str(Path.cwd()))
    
    modules_to_test = [
        ('services.lead_extractor.config', ['Config']),
        ('services.lead_extractor.models', ['Empresa', 'LeadStatus']),
        ('services.lead_extractor.database', ['DatabaseConnection']),
        ('services.lead_extractor.main', ['PipelineExtracao']),
        ('orquestrador', ['PipelineAutonomoB2B']),
    ]
    
    issues = []
    status = True
    
    for module_name, classes in modules_to_test:
        try:
            module = __import__(module_name, fromlist=classes)
            for class_name in classes:
                if hasattr(module, class_name):
                    print_ok(f"{module_name}.{class_name}")
                else:
                    print_error(f"{module_name}.{class_name} (não encontrado)")
                    issues.append(f"Classe não encontrada: {module_name}.{class_name}")
                    status = False
        except ImportError as e:
            print_error(f"{module_name}: {str(e)}")
            issues.append(f"Erro de import: {module_name}")
            status = False
        except Exception as e:
            print_warning(f"{module_name}: {str(e)}")
    
    return status, issues

def validate_dependencies() -> Tuple[bool, List[str]]:
    """Valida se dependências estão instaladas"""
    print_header("3. DEPENDÊNCIAS INSTALADAS")
    
    required_packages = [
        'streamlit',
        'pandas',
        'requests',
        'bs4',  # beautifulsoup4
        'lxml',
        'pydantic',
        'dotenv',
    ]
    
    issues = []
    status = True
    
    for package in required_packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is not None:
                try:
                    module = __import__(package)
                    version = getattr(module, '__version__', 'N/A')
                    print_ok(f"{package}: {version}")
                except:
                    print_ok(f"{package}: (instalado)")
            else:
                print_error(f"{package}: NÃO INSTALADO")
                issues.append(f"Dependência ausente: {package}")
                status = False
        except Exception as e:
            print_error(f"{package}: {str(e)}")
            issues.append(f"Erro ao verificar: {package}")
            status = False
    
    return status, issues

def validate_environment() -> Tuple[bool, List[str]]:
    """Valida configuração de ambiente"""
    print_header("4. VARIÁVEIS DE AMBIENTE")
    
    issues = []
    status = True
    
    # Verificar .env
    if Path('.env').exists():
        print_ok(".env existe")
        
        with open('.env', 'r') as f:
            env_content = f.read()
        
        required_vars = [
            'GROQ_API_KEY',
            'DATABASE_PATH',
            'LOG_LEVEL',
        ]
        
        for var in required_vars:
            if var in env_content:
                value = os.getenv(var, 'NOT_SET')
                if value == 'NOT_SET' or value.startswith('YOUR_'):
                    print_warning(f"{var}: (não configurado)")
                    issues.append(f"Variável não configurada: {var}")
                else:
                    masked_value = value[:5] + '***' if len(value) > 5 else '***'
                    print_ok(f"{var}: {masked_value}")
            else:
                print_warning(f"{var}: (não encontrada em .env)")
    else:
        if Path('.env.example').exists():
            print_warning(".env não encontrado (apenas .env.example)")
            issues.append("Execute: cp .env.example .env")
        else:
            print_error(".env e .env.example não encontrados")
            status = False
    
    return status, issues

def validate_database() -> Tuple[bool, List[str]]:
    """Valida conexão e estrutura do banco"""
    print_header("5. BANCO DE DADOS")
    
    issues = []
    status = True
    
    try:
        from services.lead_extractor.config import Config
        from services.lead_extractor.database import DatabaseConnection
        
        db_path = Path(Config.DATABASE_PATH)
        parent_dir = db_path.parent
        
        if not parent_dir.exists():
            print_warning(f"Diretório do BD não existe: {parent_dir}")
            parent_dir.mkdir(parents=True, exist_ok=True)
            print_ok(f"Diretório criado: {parent_dir}")
        
        # Tentar conectar/criar tabelas
        try:
            db = DatabaseConnection(Config.DATABASE_PATH)
            db.criar_tabelas()
            print_ok(f"Banco de dados: {Config.DATABASE_PATH}")
            
            # Verificar tabelas
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if tables:
                print_ok(f"Tabelas criadas: {len(tables)}")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print_warning("Nenhuma tabela encontrada")
            
            conn.close()
            
        except Exception as e:
            print_error(f"Erro ao conectar BD: {str(e)}")
            issues.append(f"Erro de BD: {str(e)}")
            status = False
        
    except ImportError as e:
        print_warning(f"Cannot import Config/DatabaseConnection: {str(e)}")
    
    return status, issues

def validate_docker() -> Tuple[bool, List[str]]:
    """Valida Docker setup"""
    print_header("6. DOCKER SETUP")
    
    issues = []
    status = True
    
    # Verificar Dockerfile
    docker_files = [
        ('deployment/docker/Dockerfile', 'Backend'),
        ('deployment/docker/Dockerfile.streamlit', 'Streamlit'),
    ]
    
    for docker_file, name in docker_files:
        if Path(docker_file).exists():
            with open(docker_file, 'r') as f:
                content = f.read()
            
            lines = len(content.split('\n'))
            print_ok(f"{name}: {docker_file} ({lines} linhas)")
        else:
            print_warning(f"{name}: {docker_file} (não encontrado)")
    
    # Verificar docker-compose.yml
    if Path('docker-compose.yml').exists():
        print_ok("docker-compose.yml encontrado")
        
        with open('docker-compose.yml', 'r') as f:
            compose_content = f.read()
        
        services = ['backend', 'frontend']
        for service in services:
            if service in compose_content:
                print_ok(f"  Service: {service}")
            else:
                print_warning(f"  Service: {service} (não definido)")
                issues.append(f"Service ausente em docker-compose: {service}")
    else:
        print_error("docker-compose.yml não encontrado")
        status = False
    
    return status, issues

def validate_python_environment() -> Tuple[bool, List[str]]:
    """Valida ambiente Python"""
    print_header("7. AMBIENTE PYTHON")
    
    issues = []
    status = True
    
    # Versão Python
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print_ok(f"Python: {py_version}")
    
    if sys.version_info >= (3, 9):
        print_ok("Python >= 3.9 ✓")
    else:
        print_error(f"Python < 3.9 (requer >= 3.9)")
        issues.append("Python version too old")
        status = False
    
    # Virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print_ok(f"Virtual environment ativo: {sys.prefix}")
    else:
        print_warning("Virtual environment não ativo (recomendado)")
    
    return status, issues

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print(f"\n{Colors.INFO}{'='*50}{Colors.RESET}")
    print(f"{Colors.INFO}{'HUNTERTECK - PROJECT VALIDATOR'.center(50)}{Colors.RESET}")
    print(f"{Colors.INFO}{'='*50}{Colors.RESET}\n")
    
    all_issues = []
    all_status = []
    
    # Executar validadores
    validators = [
        validate_project_structure,
        validate_imports,
        validate_dependencies,
        validate_environment,
        validate_database,
        validate_docker,
        validate_python_environment,
    ]
    
    for validator in validators:
        try:
            status, issues = validator()
            all_status.append(status)
            all_issues.extend(issues)
        except Exception as e:
            print_error(f"Erro ao executar {validator.__name__}: {str(e)}")
            all_status.append(False)
    
    # Relatório final
    print_header("RELATÓRIO FINAL")
    
    total_checks = len(validators)
    passed = sum(all_status)
    failed = total_checks - passed
    
    print(f"Total de verificações: {total_checks}")
    print_ok(f"Passou: {passed}")
    if failed > 0:
        print_error(f"Falhou: {failed}")
    
    if all_issues:
        print(f"\n{Colors.WARNING}PROBLEMAS ENCONTRADOS:{Colors.RESET}")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
    
    if all(all_status):
        print(f"\n{Colors.OK}✓ PROJETO ESTÁ SAUDÁVEL E PRONTO PARA USO!{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.ERROR}✗ EXISTEM PROBLEMAS A SEREM RESOLVIDOS{Colors.RESET}")
        print(f"{Colors.WARNING}Execute: bash INIT.sh (ou INIT.bat no Windows){Colors.RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
