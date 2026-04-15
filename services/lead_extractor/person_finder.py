"""
Microsserviço 4: Localizador de Pessoas
Encontra decisores (CEOs, CTOs, Diretores) dentro de empresas extraídas
e coleta dados de contato validados.
"""

import logging
import random
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime


logger = logging.getLogger(__name__)


class PersonFinderError(Exception):
    """Exceção customizada para erros de busca de pessoas."""
    pass


@dataclass
class Pessoa:
    """Representa uma pessoa/decisor encontrado em uma empresa."""
    
    nome: str
    cargo: str
    empresa_nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    linkedin_url: Optional[str] = None
    titulo: str = None  # CEO, CTO, Diretor, etc
    nivel_hierarquia: int = 0  # 0=C-level, 1=Direcionário, 2=Senior, 3=Active
    confianca_email: float = 0.85  # 0-1, quanto confiável é o email
    fonte: str = 'linkedin'  # linkedin, clearbit, hunter, manual
    data_descoberta: datetime = None
    
    def __post_init__(self):
        if self.data_descoberta is None:
            self.data_descoberta = datetime.now()
        
        # Normalizar título
        if self.titulo is None and self.cargo:
            self.titulo = self._extrair_titulo(self.cargo)
        
        # Calcular nível hierárquico
        if self.nivel_hierarquia == 0:
            self.nivel_hierarquia = self._calcular_nivel(self.cargo)
    
    def _extrair_titulo(self, cargo: str) -> str:
        """Extrai título principal do cargo."""
        cargo_lower = cargo.lower()
        
        títulos_c = ['ceo', 'cto', 'cfo', 'coo', 'cro', 'cmo', 'chro', 'clevel']
        títulos_exec = ['founder', 'presidente', 'vice', 'diretor', 'superintendente']
        títulos_senior = ['gerente', 'supervisor', 'coordenador', 'specialist']
        
        for titulo in títulos_c:
            if titulo in cargo_lower:
                return 'C-Level'
        
        for titulo in títulos_exec:
            if titulo in cargo_lower:
                return 'Executive'
        
        for titulo in títulos_senior:
            if titulo in cargo_lower:
                return 'Senior'
        
        return 'Active'
    
    def _calcular_nivel(self, cargo: str) -> int:
        """Calcula nível hierárquico do cargo."""
        cargo_lower = cargo.lower()
        
        if any(t in cargo_lower for t in ['ceo', 'cto', 'cfo', 'founder']):
            return 0
        elif any(t in cargo_lower for t in ['diretor', 'vice', 'presidente']):
            return 1
        elif any(t in cargo_lower for t in ['gerente', 'senhor', 'coordenador']):
            return 2
        else:
            return 3
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        data = asdict(self)
        data['data_descoberta'] = self.data_descoberta.isoformat()
        return data


class LocalizadorPessoas:
    """Localiza e extrai dados de pessoas em empresas."""
    
    # Nomes genéricos para roles comuns (podem ser customizados)
    ROLES_COMUNS = {
        'ceo': ['CEO', 'Chief Executive Officer', 'Presidente'],
        'cto': ['CTO', 'Chief Technology Officer', 'Diretor de Tecnologia'],
        'cfo': ['CFO', 'Chief Financial Officer', 'Diretor Financeiro'],
        'sales': ['Sales Director', 'VP Sales', 'Head of Sales', 'Diretor Comercial'],
        'marketing': ['Head of Marketing', 'CMO', 'Marketing Manager'],
        'product': ['Product Manager', 'Head of Product', 'Gerente de Produto'],
        'hr': ['HR Manager', 'Head of People', 'Gerente de RH'],
    }
    
    def __init__(self):
        """Inicializa o localizador de pessoas."""
        logger.info("Localizador de pessoas inicializado")
    
    def encontrar_decisores(
        self,
        empresa_nome: str,
        dominio_website: str,
        setor: Optional[str] = None,
        limite: int = 10
    ) -> List[Pessoa]:
        """
        Encontra decisores de uma empresa.
        
        Em produção, integraria com LinkedIn API, Hunter.io, Clearbit, etc.
        Neste exemplo, simula com dados realistas.
        
        Args:
            empresa_nome: Nome da empresa
            dominio_website: Domínio (para construir emails)
            setor: Setor de negócio (opcional)
            limite: Número máximo de pessoas
            
        Returns:
            Lista de Pessoa
        """
        logger.info(f"Procurando decisores em {empresa_nome}")
        
        pessoas = []
        
        # Gerar pessoas simuladas (em produção, seria consulta real)
        roles_priority = [
            ('CEO', 'ceo', 0),
            ('CTO', 'cto', 0),
            ('Sales Director', 'sales', 1),
            ('Marketing Manager', 'marketing', 2),
            ('Product Manager', 'product', 2),
        ]
        
        for i, (role, role_key, nivel) in enumerate(roles_priority[:limite]):
            # Gerar email realista
            nome_primeiro = self._gerar_primeiro_nome(role)
            nome_sobrenome = self._gerar_sobrenome()
            email = self._gerar_email(nome_primeiro, nome_sobrenome, dominio_website)
            
            pessoa = Pessoa(
                nome=f"{nome_primeiro} {nome_sobrenome}",
                cargo=role,
                empresa_nome=empresa_nome,
                email=email,
                linkedin_url=f"https://linkedin.com/in/{nome_primeiro}{nome_sobrenome}".lower(),
                titulo=self._mapear_titulo(role),
                nivel_hierarquia=nivel,
                confianca_email=0.75 + random.uniform(0, 0.25),
                fonte='linkedin'
            )
            
            pessoas.append(pessoa)
        
        logger.info(f"Encontradas {len(pessoas)} possíveis decisores")
        return pessoas
    
    def validar_email(
        self,
        email: str,
        dominio_website: str
    ) -> tuple[bool, float]:
        """
        Valida se um email pertence à empresa.
        
        Args:
            email: Email a validar
            dominio_website: Domínio da empresa
            
        Returns:
            Tupla (válido: bool, confiança: float 0-1)
        """
        # Verificar se email termina com domínio correto
        if email.endswith(f"@{dominio_website}"):
            return True, 0.95
        
        # Verificar variações de domínio
        variações = [
            f"@{dominio_website.split('.')[0]}.com",
            f"@{dominio_website.split('.')[0]}.com.br",
        ]
        
        for var in variações:
            if email.endswith(var):
                return True, 0.75
        
        return False, 0.0
    
    def gerar_emails_alternativos(
        self,
        primeira_nome: str,
        sobrenome: str,
        dominio: str,
        quantidade: int = 3
    ) -> List[str]:
        """
        Gera variações de um email corporativo.
        
        Args:
            primeira_nome: Primeiro nome
            sobrenome: Sobrenome
            dominio: Domínio
            quantidade: Quantas variações
            
        Returns:
            Lista de emails alternativos
        """
        primeiro = primeira_nome.lower()
        ultimo = sobrenome.lower()
        
        padroes = [
            f"{primeiro}.{ultimo}@{dominio}",
            f"{primeiro}@{dominio}",
            f"{primeiro[0]}{ultimo}@{dominio}",
            f"{primeiro}{ultimo[0]}@{dominio}",
            f"{primeiro}_{ultimo}@{dominio}",
        ]
        
        return padroes[:quantidade]
    
    def processar_lote(
        self,
        empresas_info: List[Dict[str, str]]
    ) -> List[Pessoa]:
        """
        Processa um lote de empresas para encontrar decisores.
        
        Args:
            empresas_info: Lista de dicts com 'nome', 'dominio', 'setor'
            
        Returns:
            Lista de todas as pessoas encontradas
        """
        logger.info(f"Processando lote de {len(empresas_info)} empresas")
        
        todas_pessoas = []
        
        for info in empresas_info:
            pessoas = self.encontrar_decisores(
                empresa_nome=info.get('nome'),
                dominio_website=info.get('dominio'),
                setor=info.get('setor')
            )
            todas_pessoas.extend(pessoas)
        
        logger.info(f"Total de {len(todas_pessoas)} pessoas encontradas")
        return todas_pessoas
    
    @staticmethod
    def _mapear_titulo(cargo: str) -> str:
        """Mapeia cargo para título simples."""
        cargo_lower = cargo.lower()
        
        if 'ceo' in cargo_lower or 'president' in cargo_lower:
            return 'C-Level'
        elif 'director' in cargo_lower or 'vice' in cargo_lower:
            return 'Executive'
        elif 'manager' in cargo_lower or 'senior' in cargo_lower:
            return 'Senior'
        else:
            return 'Active'
    
    @staticmethod
    def _gerar_primeiro_nome(role: str) -> str:
        """Gera primeiro nome realista baseado no role."""
        nomes = {
            ('CEO', 'ceo'): ['João', 'Roberto', 'Carlos', 'Paulo', 'Francisco'],
            ('CTO', 'cto'): ['André', 'Bruno', 'Diego', 'Eduardo', 'Fernando'],
            ('Sales', 'sales'): ['Marcos', 'Lucas', 'Miguel', 'Rafael', 'Rodrigo'],
            ('Marketing', 'marketing'): ['Isabela', 'Juliana', 'Camila', 'Fernanda', 'Patricia'],
            ('Product', 'product'): ['Ana', 'Marina', 'Beatriz', 'Carla', 'Daniela'],
        }
        
        for chaves, lista_nomes in nomes.items():
            if role.lower() in [k.lower() for k in chaves]:
                return random.choice(lista_nomes)
        
        return random.choice(['João', 'Maria', 'Pedro', 'Ana'])
    
    @staticmethod
    def _gerar_sobrenome() -> str:
        """Gera sobrenome realista."""
        sobrenomes = [
            'Silva', 'Santos', 'Oliveira', 'Sousa', 'Costa',
            'Ferreira', 'Pereira', 'Gomes', 'Martins', 'Carvalho',
            'Alves', 'Rocha', 'Dias', 'Barbosa', 'Lopes'
        ]
        return random.choice(sobrenomes)
    
    @staticmethod
    def _gerar_email(primeiro: str, sobrenome: str, dominio: str) -> str:
        """Gera email realista."""
        padroes = [
            f"{primeiro.lower()}.{sobrenome.lower()}",
            f"{primeiro.lower()}",
            f"{primeiro[0].lower()}{sobrenome.lower()}",
        ]
        
        padrao = random.choice(padroes)
        return f"{padrao}@{dominio}"


# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    localizador = LocalizadorPessoas()
    
    # Teste
    print("\n🔍 Procurando decisores...")
    pessoas = localizador.encontrar_decisores(
        empresa_nome="TechCorp Brasil",
        dominio_website="techcorp.com.br",
        setor="Technology"
    )
    
    print(f"\n✅ {len(pessoas)} pessoas encontradas:\n")
    for pessoa in pessoas:
        print(f"  👤 {pessoa.nome}")
        print(f"     Cargo: {pessoa.cargo}")
        print(f"     Email: {pessoa.email}")
        print(f"     Confiança: {pessoa.confianca_email:.0%}")
        print()
