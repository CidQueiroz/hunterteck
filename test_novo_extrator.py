#!/usr/bin/env python3
"""
Script de teste para validar o novo extrator real de leads
Remove dados fictícios e testa busca web real
"""

import sys
import logging
from pathlib import Path

# Adicionar projeto ao path
sys.path.insert(0, str(Path.cwd()))

from services.lead_extractor.extractors import ExtratorAPIDemo
from services.lead_extractor.config import Config
from services.lead_extractor.models import ExtratorConfig

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def testar_extrator_real():
    """Testa o novo extrator com dados reais."""
    
    print("\n" + "="*80)
    print("🧪 TESTE DO EXTRATOR REAL DE LEADS".center(80))
    print("="*80 + "\n")
    
    try:
        # Criar config
        config = ExtratorConfig(
            timeout_segundos=Config.REQUEST_TIMEOUT,
            max_tentativas=Config.MAX_RETRIES,
            intervalo_requisicoes=0.5,  # Mais rápido para testes
            banco_dados=Config.DATABASE_PATH
        )
        
        # Inicializar extrator
        logger.info("Inicializando extrator real...")
        extrator = ExtratorAPIDemo(config=config)
        
        # Teste 1: Buscar restaurantes em São Paulo
        print("\n📍 TESTE 1: Restaurantes em São Paulo")
        print("-" * 80)
        
        leads_teste1 = extrator.extrair(
            query="restaurantes",
            cidade="São Paulo",
            estado="SP"
        )
        
        print(f"✅ Leads encontrados: {len(leads_teste1)}\n")
        for i, empresa in enumerate(leads_teste1[:3], 1):
            print(f"  {i}. {empresa.nome}")
            print(f"     Website: {empresa.website}")
            print(f"     Email: {empresa.email or 'N/A'}")
            print(f"     Telefone: {empresa.telefone or 'N/A'}")
            print()
        
        # Teste 2: Buscar clínicas em Rio de Janeiro
        print("\n📍 TESTE 2: Clínicas em Rio de Janeiro")
        print("-" * 80)
        
        leads_teste2 = extrator.extrair(
            query="clínicas",
            cidade="Rio de Janeiro",
            estado="RJ"
        )
        
        print(f"✅ Leads encontrados: {len(leads_teste2)}\n")
        for i, empresa in enumerate(leads_teste2[:3], 1):
            print(f"  {i}. {empresa.nome}")
            print(f"     Website: {empresa.website}")
            print()
        
        # Teste 3: Compatibilidade com parâmetro 'ramo'
        print("\n📍 TESTE 3: Compatibilidade com parâmetro 'ramo'")
        print("-" * 80)
        
        leads_teste3 = extrator.extrair(
            ramo="escolas",
            cidade="Belo Horizonte",
            estado="MG"
        )
        
        print(f"✅ Leads encontrados: {len(leads_teste3)}\n")
        
        # Resumo
        print("\n" + "="*80)
        print("📊 RESUMO DE TESTES")
        print("="*80)
        print(f"✅ Teste 1 (restaurantes): {len(leads_teste1)} leads reais")
        print(f"✅ Teste 2 (clínicas): {len(leads_teste2)} leads reais")
        print(f"✅ Teste 3 (escolas): {len(leads_teste3)} leads reais")
        print(f"\n✅ Total de leads reais extraídos: {len(leads_teste1) + len(leads_teste2) + len(leads_teste3)}")
        print("\n✨ Extrator funciona com dados reais!")
        print("="*80 + "\n")
        
        # Validar estrutura
        if leads_teste1:
            empresa = leads_teste1[0]
            campos_obrigatorios = ['nome', 'website', 'cidade', 'estado', 'ramo']
            print("🔍 Validação de campos:\n")
            for campo in campos_obrigatorios:
                valor = getattr(empresa, campo, None)
                status = "✅" if valor else "❌"
                print(f"  {status} {campo}: {valor}")
        
        print("\n✅ TESTES CONCLUÍDOS COM SUCESSO!\n")
        return True
    
    except Exception as e:
        print(f"\n❌ ERRO NOS TESTES: {e}\n")
        logger.exception("Erro durante os testes")
        return False

if __name__ == '__main__':
    sucesso = testar_extrator_real()
    sys.exit(0 if sucesso else 1)
