"""
Microsserviço 2: Validador de Dados de Leads
Valida, deduplica e enriquece informações básicas de prospects extraídos.
Aplicar lógica de negócio e padrões de qualidade de dados.
"""

import sqlite3
import re
import logging
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

# Importar do MS1
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.lead_extractor.models import Empresa, LeadStatus, LeadSource
from services.lead_extractor.database import DatabaseConnection, DatabaseError
from services.lead_extractor.config import Config


logger = logging.getLogger(__name__)


class ValidatorError(Exception):
    """Exceção customizada para erros de validação."""
    pass


@dataclass
class RegrasValidacao:
    """Regras e padrões para validação de dados."""
    
    # Padrões
    PATTERN_EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PATTERN_WEBSITE = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    PATTERN_TELEFONE = r'^\+?[\d\s\-\(\)]{10,}$'
    
    # Extensões de email corporativo válidas
    EXTENSOES_DESCARTAVEIS = {
        'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
        'aol.com', 'mail.com', 'test.com', 'example.com'
    }
    
    # Palavras-chave que indicam website inválido
    KEYWORDS_INVALIDOS = {
        'parked', 'temporary', 'placeholder', 'test', 'demo',
        'default', 'errorpage', 'noindex'
    }
    
    # Ramos/Setores válidos (whitelist)
    RAMOS_VALIDOS = {
        'restaurantes', 'bares', 'café', 'lojas', 'varejo',
        'e-commerce', 'consultoria', 'agência', 'hotel', 'pousada',
        'saúde', 'dental', 'fitness', 'educação', 'cursos',
        'imóvel', 'construção', 'engenharia', 'manufatura',
        'serviços', 'tecnologia', 'software', 'app', 'startup',
        'marketing', 'publicidade', 'design', 'desenvolvimento', 'clínicas', 'escolas'
    }


class ValidadorLeads:
    """Validador de dados de leads extraídos."""
    
    def __init__(self, regras: RegrasValidacao = None):
        """
        Inicializa o validador.
        
        Args:
            regras: Regras de validação customizadas
        """
        self.regras = regras or RegrasValidacao()
        self.db = DatabaseConnection()
        logger.info("Validador de leads inicializado")
    
    def validar_empresa(self, empresa: Empresa) -> Tuple[bool, List[str]]:
        """
        Valida uma empresa contra regras de qualidade.
        
        Args:
            empresa: Empresa a validar
            
        Returns:
            Tupla (válido: bool, erros: List[str])
        """
        erros = []
        
        # Validar nome
        if not empresa.nome or len(empresa.nome.strip()) < 2:
            erros.append("Nome muito curto ou vazio")
        if any(palavra in empresa.nome.lower() for palavra in ['test', 'demo', 'temp']):
            erros.append("Nome parece ser de teste/demo")
        
        # Validar website
        if not empresa.website or len(empresa.website) < 8:
            erros.append("Website inválido")
        elif not re.match(self.regras.PATTERN_WEBSITE, empresa.website):
            erros.append("Website não é uma URL válida")
        else:
            # Verificar se é parked/placeholder
            dominio = self._extrair_dominio(empresa.website)
            if any(kw in dominio.lower() for kw in self.regras.KEYWORDS_INVALIDOS):
                erros.append("Website parece ser placeholder/parked")
        
        # Validar email (se fornecido)
        if empresa.email:
            if not re.match(self.regras.PATTERN_EMAIL, empresa.email):
                erros.append("Email não é válido")
            else:
                dominio_email = empresa.email.split('@')[1]
                if dominio_email in self.regras.EXTENSOES_DESCARTAVEIS:
                    erros.append("Email pessoal, não corporativo")
        
        # Validar telefone (se fornecido)
        if empresa.telefone:
            if not re.match(self.regras.PATTERN_TELEFONE, empresa.telefone):
                erros.append("Telefone inválido")
        
        # Validar endereço
        if not empresa.endereco or len(empresa.endereco.strip()) < 5:
            erros.append("Endereço muito curto")
        
        # Validar cidade/estado
        if not empresa.cidade or len(empresa.cidade.strip()) < 2:
            erros.append("Cidade vazia/inválida")
        if not empresa.estado or len(empresa.estado.strip()) < 2:
            erros.append("Estado vazio/inválido")
        
        # Validar ramo
        if not empresa.ramo or len(empresa.ramo.strip()) < 2:
            erros.append("Ramo não especificado")
        
        # Validar fonte
        logger.debug(f"Verificando fonte: type={type(empresa.fonte)}, value={empresa.fonte}, isinstance={isinstance(empresa.fonte, LeadSource)}")
        if not isinstance(empresa.fonte, LeadSource):
            erros.append("Fonte de lead inválida")
            logger.debug(f"  ❌ Fonte inválida adicionada ao erro")
        
        return len(erros) == 0, erros
    
    def detectar_duplicatas(
        self,
        empresa: Empresa,
        conexao: Optional[sqlite3.Connection] = None
    ) -> Tuple[bool, Optional[Empresa]]:
        """
        Detecta se empresa já existe no banco.
        
        Args:
            empresa: Empresa a verificar
            conexao: Conexão existente (opcional)
            
        Returns:
            Tupla (é_duplicata: bool, empresa_existente: Empresa ou None)
        """
        try:
            # Primeiro, verificar por website exato
            existente = self.db.obter_empresa_por_website(empresa.website)
            if existente:
                return True, existente
            
            # Verificar fuzzy match por nome + cidade
            # (implementar depois com algoritmo Levenshtein para produção)
            
            return False, None
        
        except DatabaseError as e:
            logger.error(f"Erro ao detectar duplicatas: {e}")
            return False, None
    
    def limpar_dados(self, empresa: Empresa) -> Empresa:
        """
        Limpa e normaliza dados da empresa.
        
        Args:
            empresa: Empresa a limpar
            
        Returns:
            Empresa com dados normalizados
        """
        # Limpar strings
        empresa.nome = empresa.nome.strip().title() if empresa.nome else empresa.nome
        empresa.website = empresa.website.strip().lower() if empresa.website else empresa.website
        empresa.email = empresa.email.strip().lower() if empresa.email else None
        empresa.telefone = self._limpar_telefone(empresa.telefone) if empresa.telefone else None
        empresa.endereco = empresa.endereco.strip() if empresa.endereco else empresa.endereco
        empresa.cidade = empresa.cidade.strip().title() if empresa.cidade else empresa.cidade
        empresa.estado = empresa.estado.strip().upper() if empresa.estado else empresa.estado
        empresa.ramo = empresa.ramo.strip().lower() if empresa.ramo else empresa.ramo
        
        # Garantir que website tem protocolo
        if empresa.website and not empresa.website.startswith(('http://', 'https://')):
            empresa.website = 'https://' + empresa.website
        
        return empresa
    
    def enriquecer_minimo(self, empresa: Empresa) -> Empresa:
        """
        Enriquecimento mínimo: deduz dados faltantes.
        
        Args:
            empresa: Empresa a enriquecer
            
        Returns:
            Empresa enriquecida
        """
        # Se não tem email, tentar extrair domínio e gerar email genérico
        if not empresa.email:
            dominio = self._extrair_dominio(empresa.website)
            # Comum: contato@, info@, hello@
            empresa.email = f"info@{dominio}"
        
        # Se não tem ramo, deuzir da fonte ou deixar genérico
        if not empresa.ramo or empresa.ramo == 'geral':
            empresa.ramo = 'Serviços'
        
        return empresa
    
    def gerar_score_qualidade(self, empresa: Empresa) -> float:
        """
        Gera score de qualidade do lead (0-100).
        
        Critérios:
        - Nome completo (+10)
        - Email corporativo (+20)
        - Telefone (+15)
        - Endereço detalhado (+15)
        - Website funcional (+20)
        - Ramo válido (+10)
        - Sem flags de alerta (-variável)
        
        Args:
            empresa: Empresa a avaliar
            
        Returns:
            Score 0-100
        """
        score = 50  # Base score
        
        # Nome
        if empresa.nome and len(empresa.nome) > 5:
            score += 10
        
        # Email corporativo
        if empresa.email:
            score += 15
            if '@' in empresa.email:
                dominio = empresa.email.split('@')[1]
                if dominio in self.regras.EXTENSOES_DESCARTAVEIS:
                    score -= 10
        
        # Telefone
        if empresa.telefone and len(empresa.telefone) > 9:
            score += 10
        
        # Endereço
        if empresa.endereco and len(empresa.endereco) > 10:
            score += 10
        
        # Website
        if empresa.website and empresa.website.startswith('http'):
            score += 15
        
        # Ramo conhecido
        if empresa.ramo.lower() in self.regras.RAMOS_VALIDOS:
            score += 10
        
        # Normalizar score
        return max(0, min(100, score))
    
    def validar_lote(
        self,
        empresas: List[Empresa],
        remover_invalidas: bool = True
    ) -> Tuple[List[Empresa], Dict[str, Any]]:
        """
        Valida um lote de empresas.
        
        Args:
            empresas: Lista de empresas
            remover_invalidas: Se True, remove empresas inválidas
            
        Returns:
            Tupla (empresas_validas, estatísticas)
        """
        validas = []
        invalidas_count = 0
        duplicatas_count = 0
        limpas = 0
        
        logger.info(f"Validando lote de {len(empresas)} empresas")
        
        for empresa in empresas:
            try:
                # Limpar dados
                empresa = self.limpar_dados(empresa)
                limpas += 1
                
                # Validar
                valida, erros = self.validar_empresa(empresa)
                if not valida:
                    logger.debug(f"Empresa '{empresa.nome}' inválida: {erros}")
                    invalidas_count += 1
                    if not remover_invalidas:
                        validas.append(empresa)
                    continue
                
                # Detectar duplicatas
                eh_duplicata, _ = self.detectar_duplicatas(empresa)
                if eh_duplicata:
                    logger.debug(f"Duplicata encontrada: {empresa.website}")
                    duplicatas_count += 1
                    continue
                
                # Enriquecer minimamente
                empresa = self.enriquecer_minimo(empresa)
                
                # Gerar score
                empresa.score_qualidade = self.gerar_score_qualidade(empresa)
                
                validas.append(empresa)
            
            except Exception as e:
                logger.error(f"Erro ao validar empresa: {e}")
                invalidas_count += 1
        
        estatisticas = {
            'total_original': len(empresas),
            'total_validas': len(validas),
            'invalidas': invalidas_count,
            'duplicatas': duplicatas_count,
            'limpas': limpas,
            'taxa_validade': len(validas) / max(1, len(empresas)) * 100
        }
        
        logger.info(f"Validação concluída: {estatisticas}")
        return validas, estatisticas
    
    @staticmethod
    def _extrair_dominio(website: str) -> str:
        """Extrai domínio de uma URL."""
        website = website.replace('https://', '').replace('http://', '')
        website = website.split('/')[0]
        return website
    
    @staticmethod
    def _limpar_telefone(telefone: str) -> str:
        """Limpa e normaliza número de telefone."""
        # Remover caracteres especiais
        telefone = re.sub(r'[^\d\+\-]', '', telefone)
        return telefone


# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Criar validador
    validador = ValidadorLeads()
    
    # Teste com dados
    from lead_extractor.models import LeadSource
    
    empresas_teste = [
        Empresa(
            nome="Restaurante Delícia",
            website="https://restaurante-delicia.com.br",
            email="contato@restaurante-delicia.com.br",
            telefone="+55 11 98765-4321",
            endereco="Rua das Flores 123",
            cidade="São Paulo",
            estado="SP",
            ramo="Restaurantes",
            fonte=LeadSource.API
        ),
        Empresa(
            nome="",  # Inválido: nome vazio
            website="https://exemplo.com",
            endereco="Rua X",
            cidade="RJ",
            estado="RJ",
            ramo="Varejo",
            fonte=LeadSource.API
        ),
    ]
    
    validas, stats = validador.validar_lote(empresas_teste)
    print(f"\n✅ {len(validas)} empresas válidas")
    print(f"📊 Estatísticas: {stats}")
