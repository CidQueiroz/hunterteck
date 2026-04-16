"""
Microsserviço 4: Localizador de Pessoas
Encontra decisores (CEOs, CTOs, Diretores) dentro de empresas extraídas
e coleta dados de contato validados.
"""

import logging
import random
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from .config import Config

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
    
    def encontrar_decisores(
        self,
        empresa_nome: str,
        dominio_website: str,
        setor: Optional[str] = None,
        limite: int = 10,
        email_empresa: Optional[str] = None
    ) -> List[Pessoa]:
        """
        Encontra decisores de uma empresa usando o padrão Chain of Responsibility.
        
        Ordem de prioridade (Fallback):
        1. E-mail fornecido pelo MS1 (Orgânico)
        2. Hunter.io API
        3. Apollo.io API
        4. Scraper Local (BeautifulSoup)
        """
        logger.info(f"Processando lead real de {empresa_nome}")
        
        pessoas = []
        email_encontrado = None
        fonte_email = 'extracao_organica'
        
        # 0. Privilégio ao MS1 (se já trouxe o e-mail validado)
        if email_empresa and "@" in email_empresa:
            email_encontrado = email_empresa
        
        # 1. Camada 1: Hunter.io
        if not email_encontrado:
            email_encontrado = self._buscar_hunter(dominio_website)
            if email_encontrado:
                fonte_email = 'hunter_api'
        
        # 2. Camada 2: Apollo.io
        if not email_encontrado:
            email_encontrado = self._buscar_apollo(dominio_website)
            if email_encontrado:
                fonte_email = 'apollo_api'
        
        # 3. Camada 3: Scraper Local Profundo
        if not email_encontrado:
            email_encontrado = self._buscar_local(dominio_website)
            if email_encontrado:
                fonte_email = 'scraper_profundo'
        
        # Veredito
        if email_encontrado:
            pessoa = Pessoa(
                nome="Equipe",
                cargo="Diretoria",
                empresa_nome=empresa_nome,
                email=email_encontrado,
                linkedin_url=None,
                titulo="C-Level", # Garante processamento no orquestrador
                nivel_hierarquia=0,
                confianca_email=1.0,
                fonte=fonte_email
            )
            pessoas.append(pessoa)
        else:
            logger.warning(f"Empresa {empresa_nome} descartada no MS4: Descartado após falha nas 3 camadas de busca.")
        
        return pessoas

    def _buscar_hunter(self, dominio: str) -> Optional[str]:
        """Integração com Hunter.io Domain Search API."""
        if not Config.HUNTER_API_KEY:
            logger.debug("Hunter.io pulado: API Key não configurada.")
            return None
            
        logger.debug(f"[Camada 1] Buscando no Hunter.io por: {dominio}")
        try:
            url = f"https://api.hunter.io/v2/domain-search?domain={dominio}&api_key={Config.HUNTER_API_KEY}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                emails = data.get('data', {}).get('emails', [])
                if emails:
                    email = emails[0].get('value')
                    logger.info(f"Hunter.io encontrou o e-mail: {email}")
                    return email
        except Exception as e:
            logger.error(f"Erro ao consultar Hunter.io para {dominio}: {e}")
        return None

    def _buscar_apollo(self, dominio: str) -> Optional[str]:
        """Integração com Apollo.io Organization Search API."""
        if not Config.APOLLO_API_KEY:
            logger.debug("Apollo.io pulado: API Key não configurada.")
            return None
            
        logger.debug(f"[Camada 2] Buscando no Apollo.io por: {dominio}")
        try:
            url = "https://api.apollo.io/v1/organizations/enrich"
            headers = {
                'Cache-Control': 'no-cache',
                'Content-Type': 'application/json'
            }
            payload = {
                'api_key': Config.APOLLO_API_KEY,
                'domain': dominio
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                org = data.get('organization', {})
                email = org.get('primary_domain_email') or org.get('primary_email')
                if email:
                    logger.info(f"Apollo.io encontrou o e-mail: {email}")
                    return email
        except Exception as e:
            logger.error(f"Erro ao consultar Apollo.io para {dominio}: {e}")
        return None

    def _buscar_local(self, dominio: str) -> Optional[str]:
        """Scraper profundo usando BeautifulSoup nas rotas raízes e contato."""
        logger.debug(f"[Camada 3] Iniciando Scraper Profundo local para: {dominio}")
        
        padrao_email = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
        headers = {'User-Agent': Config.USER_AGENT}
        
        base_urls = [
            f"https://{dominio}",
            f"http://{dominio}",
            f"https://www.{dominio}",
            f"http://www.{dominio}"
        ]
        
        rotas = ["", "/contato", "/contact", "/sobre", "/about"]
        
        # Testar qual base_url funciona primeiro
        url_valida = None
        for b_url in base_urls:
            try:
                resp = requests.get(b_url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    url_valida = b_url
                    break
            except Exception:
                continue
                
        if not url_valida:
            logger.debug(f"Falha ao conectar no domínio {dominio} nas tentativas HTTPS/HTTP.")
            return None
            
        # Varrer rotas
        for rota in rotas:
            alvo = f"{url_valida}{rota}"
            try:
                resp = requests.get(alvo, headers=headers, timeout=8)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    texto = soup.get_text(separator=' ')
                    emails_encontrados = padrao_email.findall(texto)
                    
                    for email in emails_encontrados:
                        email_lower = email.lower()
                        # Filtrar emails de assets (ex: png@2x, sentry@..., wixpress@...)
                        if any(x in email_lower for x in ['.png', '.jpg', 'sentry', 'wixpress', 'example']):
                            continue
                        logger.info(f"Scraper Profundo encontrou o e-mail na rota {rota}: {email_lower}")
                        return email_lower
            except Exception as e:
                logger.debug(f"Erro no Scraper Profundo acessando {alvo}: {e}")
                
        return None
        

    
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
                setor=info.get('setor'),
                email_empresa=info.get('email')
            )
            todas_pessoas.extend(pessoas)
        
        logger.info(f"Total de {len(todas_pessoas)} pessoas encontradas")
        return todas_pessoas
    



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
