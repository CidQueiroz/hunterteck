"""
Módulo de extractores de leads.
Implementa diferentes estratégias de coleta de dados de empresas.
"""

import logging
import requests
import time
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from .models import Empresa, LeadSource, ExtratorConfig
from .config import Config


logger = logging.getLogger(__name__)


class ExtratorError(Exception):
    """Exceção customizada para erros de extração."""
    pass


class ExtratorBase(ABC):
    """Classe base abstrata para extractores de leads."""
    
    def __init__(self, config: ExtratorConfig = None):
        """
        Inicializa o extrator.
        
        Args:
            config: Configuração do extrator
        """
        self.config = config or ExtratorConfig()
        self.config.validar()
        self.session = self._criar_sessao()
        
    def _criar_sessao(self) -> requests.Session:
        """Cria uma sessão HTTP com configurações padrão."""
        sessao = requests.Session()
        sessao.headers.update({
            'User-Agent': self.config.user_agent,
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
        })
        return sessao
    
    @abstractmethod
    def extrair(self, **kwargs) -> List[Empresa]:
        """
        Método abstrato para extração de leads.
        
        Returns:
            Lista de empresas extraídas
        """
        pass
    
    def _fazer_requisicao(
        self, 
        url: str, 
        metodo: str = "GET",
        **kwargs
    ) -> Optional[requests.Response]:
        """
        Realiza uma requisição HTTP com retry.
        
        Args:
            url: URL da requisição
            metodo: Método HTTP (GET, POST, etc)
            **kwargs: Argumentos adicionais para a requisição
            
        Returns:
            Response objeto ou None se falhar
        """
        for tentativa in range(self.config.max_tentativas):
            try:
                if tentativa > 0:
                    time.sleep(self.config.intervalo_requisicoes * tentativa)
                
                response = self.session.request(
                    metodo,
                    url,
                    timeout=self.config.timeout_segundos,
                    **kwargs
                )
                response.raise_for_status()
                return response
                
            except requests.Timeout:
                logger.warning(f"Timeout na tentativa {tentativa + 1}/{self.config.max_tentativas}: {url}")
            except requests.ConnectionError as e:
                logger.warning(f"Erro de conexão na tentativa {tentativa + 1}/{self.config.max_tentativas}: {e}")
            except requests.HTTPError as e:
                if response.status_code == 429:  # Rate limit
                    logger.warning(f"Rate limit atingido. Aguardando...")
                    time.sleep(5)
                elif response.status_code >= 500:
                    logger.warning(f"Erro de servidor {response.status_code}. Tentando novamente...")
                else:
                    logger.error(f"Erro HTTP {response.status_code}: {e}")
                    return None
            except Exception as e:
                logger.error(f"Erro inesperado na requisição: {e}")
                if tentativa == self.config.max_tentativas - 1:
                    raise ExtratorError(f"Falha ao fazer requisição após {self.config.max_tentativas} tentativas") from e
        
        return None


class ExtratorGoogleMaps(ExtratorBase):
    """Extrator de leads usando Google Maps API."""
    
    API_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    def __init__(self, api_key: Optional[str] = None, config: ExtratorConfig = None):
        """
        Inicializa o extrator do Google Maps.
        
        Args:
            api_key: Chave de API do Google
            config: Configuração do extrator
        """
        super().__init__(config)
        self.api_key = api_key or Config.GOOGLE_API_KEY
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY não configurada. Google Maps não funcionará.")
    
    def extrair(
        self,
        query: str,
        cidade: str,
        estado: str,
        limite: int = 20
    ) -> List[Empresa]:
        """
        Extrai leads usando Google Maps API.
        
        Args:
            query: Termo de busca (ex: "restaurantes em")
            cidade: Cidade para busca
            estado: Estado/Região
            limite: Número máximo de resultados
            
        Returns:
            Lista de empresas encontradas
        """
        if not self.api_key:
            raise ExtratorError("API key do Google não configurada")
        
        empresas = []
        busca_completa = f"{query} {cidade}, {estado}"
        
        try:
            logger.info(f"Iniciando extração Google Maps: {busca_completa}")
            
            params = {
                'query': busca_completa,
                'key': self.api_key,
                'language': 'pt-BR'
            }
            
            response = self._fazer_requisicao(self.API_URL, params=params)
            if not response:
                raise ExtratorError("Falha ao conectar com Google Maps API")
            
            dados = response.json()
            
            if dados.get('status') != 'OK':
                raise ExtratorError(f"Google Maps retornou: {dados.get('status')}")
            
            for resultado in dados.get('results', [])[:limite]:
                try:
                    empresa = Empresa(
                        nome=resultado.get('name', 'N/A'),
                        website=resultado.get('website', ''),
                        endereco=resultado.get('formatted_address', ''),
                        cidade=cidade,
                        estado=estado,
                        ramo=resultado.get('types', ['geral'])[0],
                        fonte=LeadSource.GOOGLE_MAPS,
                        telefone=resultado.get('formatted_phone_number'),
                        email=None  # Google Maps não fornece email
                    )
                    empresas.append(empresa)
                except ValueError as e:
                    logger.warning(f"Erro ao processar resultado: {e}")
                    continue
            
            logger.info(f"Extração Google Maps concluída: {len(empresas)} empresas encontradas")
            
        except Exception as e:
            logger.error(f"Erro durante extração Google Maps: {e}")
            raise ExtratorError(f"Falha na extração: {str(e)}") from e
        
        return empresas


class ExtratorWebScrape(ExtratorBase):
    """Extrator genérico de leads via web scraping."""
    
    def __init__(self, config: ExtratorConfig = None):
        """Inicializa o extrator de web scraping."""
        super().__init__(config)
    
    def extrair(
        self,
        url_base: str,
        ramo: str,
        cidade: str,
        estado: str,
        seletores: dict
    ) -> List[Empresa]:
        """
        Extrai leads de um website via scraping.
        
        Args:
            url_base: URL base para scraping
            ramo: Categoria/Ramo de negócio
            cidade: Cidade
            estado: Estado
            seletores: Dicionário com seletores CSS para dados (nome, website, etc)
            
        Returns:
            Lista de empresas extraídas
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise ExtratorError("BeautifulSoup4 é necessário para web scraping. Instale com: pip install beautifulsoup4")
        
        empresas = []
        
        try:
            logger.info(f"Iniciando web scraping: {url_base}")
            
            response = self._fazer_requisicao(url_base)
            if not response:
                raise ExtratorError("Falha ao conectar com URL")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontrar elementos usando seletores CSS
            elementos = soup.select(seletores.get('elemento', ''))
            
            if not elementos:
                logger.warning(f"Nenhum elemento encontrado com seletor: {seletores.get('elemento')}")
                return empresas
            
            for elemento in elementos:
                try:
                    nome = elemento.select_one(seletores.get('nome', ''))
                    website = elemento.select_one(seletores.get('website', ''))
                    email = elemento.select_one(seletores.get('email', ''))
                    telefone = elemento.select_one(seletores.get('telefone', ''))
                    endereco = elemento.select_one(seletores.get('endereco', ''))
                    
                    empresa = Empresa(
                        nome=nome.get_text(strip=True) if nome else 'N/A',
                        website=website.get('href', website.get_text(strip=True)) if website else '',
                        email=email.get_text(strip=True) if email else None,
                        telefone=telefone.get_text(strip=True) if telefone else None,
                        endereco=endereco.get_text(strip=True) if endereco else '',
                        cidade=cidade,
                        estado=estado,
                        ramo=ramo,
                        fonte=LeadSource.WEB_SCRAPE
                    )
                    empresas.append(empresa)
                except ValueError as e:
                    logger.warning(f"Erro ao processar elemento: {e}")
                    continue
            
            logger.info(f"Web scraping concluído: {len(empresas)} empresas extraídas")
            
        except Exception as e:
            logger.error(f"Erro durante web scraping: {e}")
            raise ExtratorError(f"Falha no scraping: {str(e)}") from e
        
        return empresas


class ExtratorAPIDemo(ExtratorBase):
    """Extrator real de leads via busca na web nativa."""
    
    DADOS_EXEMPLO_BR = {
        "restaurantes": [
            {"nome": "Restaurante São Paulo Grill", "website": "https://www.spaulgrill.com.br", "email": "contato@spaulgrill.com.br", "telefone": "(11) 3333-4444", "endereco": "São Paulo, SP"},
            {"nome": "Pizzaria Bella Italia", "website": "https://www.bellaitalia.com.br", "email": "reservas@bellaitalia.com.br", "telefone": "(11) 3344-5555", "endereco": "São Paulo, SP"},
            {"nome": "Casa da Comida Nordestina", "website": "https://www.casanordestina.com.br", "email": "info@casanordestina.com.br", "telefone": "(11) 3355-6666", "endereco": "São Paulo, SP"},
        ],
        "clínicas": [
            {"nome": "Clínica Médica Rio", "website": "https://www.clinicamedicarjo.com.br", "email": "agendamento@clinicamedicarjo.com.br", "telefone": "(21) 2111-2222", "endereco": "Rio de Janeiro, RJ"},
            {"nome": "Clínica Plus Saúde", "website": "https://www.clinicaplussaude.com.br", "email": "contato@clinicaplussaude.com.br", "telefone": "(21) 2222-3333", "endereco": "Rio de Janeiro, RJ"},
        ],
        "escolas": [
            {"nome": "Escola Rio de Janeiro", "website": "https://www.escolariodejaneiro.com.br", "email": "admissoes@escolariodejaneiro.com.br", "telefone": "(21) 3111-2222", "endereco": "Rio de Janeiro, RJ"},
            {"nome": "Colégio Belo Horizonte", "website": "https://www.colegiobelohor.com.br", "email": "matriculas@colegiobelohor.com.br", "telefone": "(31) 3222-3333", "endereco": "Belo Horizonte, MG"},
        ],
    }
    
    def __init__(self, config: ExtratorConfig = None):
        super().__init__(config)
        logger.info("Extrator Nativo de Web (DDG HTML) inicializado")
    
    def extrair(
        self,
        query: str = None,
        ramo: str = None,
        cidade: str = None,
        estado: str = None,
        limite: int = 10
    ) -> List[Empresa]:
        import re
        import time
        from bs4 import BeautifulSoup
        
        termo_busca = query or ramo or "empresas"
        
        if not cidade or not estado:
            logger.error("Cidade e Estado são obrigatórios")
            return []
        
        empresas = []
        busca = f"{termo_busca} {cidade} {estado}"
        
        try:
            logger.info(f"Buscando (Web Scrape Nativo): {busca}")
            
            url = "https://html.duckduckgo.com/html/"
            data = {'q': busca}
            
            response = self._fazer_requisicao(url, metodo="POST", data=data)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                resultados = soup.find_all('div', class_='result')
                
                if resultados:
                    logger.info(f"Encontrados {len(resultados)} resultados da web")
                    
                    urls_processadas = set()
                    
                    for resultado in resultados[:limite * 2]:
                        try:
                            title_a = resultado.find('a', class_='result__a')
                            url_a = resultado.find('a', class_='result__url') 
                            snippet_a = resultado.find('a', class_='result__snippet')
                            
                            if not title_a:
                                continue
                                
                            title = title_a.text.strip()
                            url_res = url_a.text.strip() if url_a else ''
                            description = snippet_a.text.strip() if snippet_a else ''
                            
                            # Filtro básico de lixo ou duplicata
                            if not url_res or url_res in urls_processadas or "ddg/" in url_res:
                                continue
                            
                            urls_processadas.add(url_res)
                            
                            nome = title[:100]
                            if len(nome) < 3:
                                continue
                                
                            if len(nome.split()) > 8:
                                nome = " ".join(nome.split()[:4])
                            
                            email = None
                            telefone = None
                            
                            if description:
                                emails = re.findall(
                                    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                                    description + " " + title
                                )
                                if emails:
                                    email = emails[0]
                                    if any(domain in email.lower() for domain in ['noreply', 'no-reply']):
                                        email = None
                                
                                telefones = re.findall(
                                    r'\(?(\d{2})\)?\s?9?\d{4}-\d{4}|\(\d{2}\)\s\d{4,5}-\d{4}|\d{4,5}-\d{4}',
                                    description
                                )
                                if telefones:
                                    primeiro = telefones[0]
                                    if isinstance(primeiro, tuple):
                                        telefone = "".join(str(p) for p in primeiro if p)
                                    else:
                                        telefone = str(primeiro)
                            
                            url_final = f"https://{url_res}" if not url_res.startswith('http') else url_res
                            
                            empresa = Empresa(
                                nome=nome,
                                website=url_final,
                                email=email,
                                telefone=telefone,
                                endereco=f"Centro, {cidade}, {estado}",
                                cidade=cidade,
                                estado=estado,
                                ramo=termo_busca.lower(),
                                fonte=LeadSource.WEB_SCRAPE
                            )
                            empresas.append(empresa)
                            logger.debug(f"Lead extraído: {nome} ({url_final})")
                            
                            if len(empresas) >= limite:
                                break
                                
                        except ValueError as e:
                            continue
                else:
                    logger.warning(f"Nenhum resultado web encontrado para: {busca}")
        
        except Exception as e:
            logger.error(f"Erro durante extração Web: {e}")
            
        if not empresas:
            logger.info("Extração concluída: 0 leads encontrados na busca real.")
        else:
            logger.info(f"Extração concluída: {len(empresas)} leads encontrados")
        return empresas
