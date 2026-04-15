"""
Camada de acesso ao banco de dados SQLite.
Gerencia operações CRUD de leads com tratamento robusto de erros.
"""

import sqlite3
import logging
from typing import List, Optional, Tuple, Any
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path

from .models import Empresa, LeadSource, LeadStatus
from .config import Config


logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Exceção customizada para erros de banco de dados."""
    pass


class DatabaseConnection:
    """Gerenciador de conexões com o banco de dados SQLite."""
    
    def __init__(self, db_path: str = Config.DATABASE_PATH):
        """
        Inicializa o gerenciador de banco de dados.
        
        Args:
            db_path: Caminho para o arquivo SQLite
        """
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
    
    @contextmanager
    def conexao(self):
        """Context manager para gerenciar conexões com o banco."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Erro de banco de dados: {e}")
            if conn:
                conn.rollback()
            raise DatabaseError(f"Erro ao conectar ao banco: {str(e)}") from e
        finally:
            if conn:
                conn.close()
    
    def criar_tabelas(self) -> None:
        """Cria as tabelas necessárias se não existirem."""
        try:
            with self.conexao() as conn:
                cursor = conn.cursor()
                
                # Tabela principal de leads/empresas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS empresas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        website TEXT NOT NULL UNIQUE,
                        email TEXT,
                        telefone TEXT,
                        endereco TEXT NOT NULL,
                        cidade TEXT NOT NULL,
                        estado TEXT NOT NULL,
                        ramo TEXT NOT NULL,
                        fonte TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'novo',
                        data_coleta DATETIME NOT NULL,
                        ultima_atualizacao DATETIME NOT NULL,
                        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de histórico de alterações
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS historico_alteracoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        empresa_id INTEGER NOT NULL,
                        campo TEXT NOT NULL,
                        valor_anterior TEXT,
                        valor_novo TEXT,
                        data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (empresa_id) REFERENCES empresas (id) ON DELETE CASCADE
                    )
                """)
                
                # Índices para melhor performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_empresas_cidade 
                    ON empresas(cidade)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_empresas_ramo 
                    ON empresas(ramo)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_empresas_status 
                    ON empresas(status)
                """)
                
                conn.commit()
                logger.info("Tabelas do banco de dados criadas/atualizadas com sucesso")
                
        except sqlite3.Error as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            raise DatabaseError(f"Falha ao criar tabelas: {str(e)}") from e
    
    def inserir_empresa(self, empresa: Empresa) -> int:
        """
        Insere uma nova empresa no banco de dados.
        
        Args:
            empresa: Instância de Empresa a ser inserida
            
        Returns:
            ID da empresa inserida
            
        Raises:
            DatabaseError: Se houver erro na inserção
        """
        try:
            with self.conexao() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO empresas 
                    (nome, website, email, telefone, endereco, cidade, estado, ramo, 
                     fonte, status, data_coleta, ultima_atualizacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    empresa.nome,
                    empresa.website,
                    empresa.email,
                    empresa.telefone,
                    empresa.endereco,
                    empresa.cidade,
                    empresa.estado,
                    empresa.ramo,
                    empresa.fonte.value,
                    empresa.status.value,
                    empresa.data_coleta,
                    empresa.ultima_atualizacao
                ))
                
                empresa_id = cursor.lastrowid
                conn.commit()
                logger.debug(f"Empresa '{empresa.nome}' inserida com ID {empresa_id}")
                return empresa_id
                
        except sqlite3.IntegrityError as e:
            logger.warning(f"Empresa duplicada ou dados inválidos: {e}")
            raise DatabaseError(f"Website já existe no banco de dados") from e
        except sqlite3.Error as e:
            logger.error(f"Erro ao inserir empresa: {e}")
            raise DatabaseError(f"Falha ao inserir empresa: {str(e)}") from e
    
    def inserir_empresas_em_lote(self, empresas: List[Empresa]) -> Tuple[int, int]:
        """
        Insere múltiplas empresas em uma transação.
        
        Args:
            empresas: Lista de empresas a inserir
            
        Returns:
            Tupla (total, sucesso) com contagem de empresas
        """
        sucesso = 0
        total = len(empresas)
        
        try:
            with self.conexao() as conn:
                cursor = conn.cursor()
                
                for empresa in empresas:
                    try:
                        cursor.execute("""
                            INSERT INTO empresas 
                            (nome, website, email, telefone, endereco, cidade, estado, ramo,
                             fonte, status, data_coleta, ultima_atualizacao)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            empresa.nome,
                            empresa.website,
                            empresa.email,
                            empresa.telefone,
                            empresa.endereco,
                            empresa.cidade,
                            empresa.estado,
                            empresa.ramo,
                            empresa.fonte.value,
                            empresa.status.value,
                            empresa.data_coleta,
                            empresa.ultima_atualizacao
                        ))
                        sucesso += 1
                    except sqlite3.IntegrityError:
                        logger.warning(f"Website duplicado: {empresa.website}")
                        continue
                
                conn.commit()
                logger.info(f"Inserção em lote: {sucesso}/{total} empresas inseridas com sucesso")
                return total, sucesso
                
        except sqlite3.Error as e:
            logger.error(f"Erro ao inserir empresas em lote: {e}")
            raise DatabaseError(f"Falha na inserção em lote: {str(e)}") from e
    
    def obter_empresa_por_id(self, empresa_id: int) -> Optional[Empresa]:
        """
        Recupera uma empresa pelo ID.
        
        Args:
            empresa_id: ID da empresa
            
        Returns:
            Instância de Empresa ou None se não encontrada
        """
        try:
            with self.conexao() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM empresas WHERE id = ?", (empresa_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_para_empresa(row)
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Erro ao obter empresa: {e}")
            raise DatabaseError(f"Falha ao recuperar empresa: {str(e)}") from e
    
    def obter_empresa_por_website(self, website: str) -> Optional[Empresa]:
        """Recupera uma empresa pelo website."""
        try:
            with self.conexao() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM empresas WHERE website = ?", (website,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_para_empresa(row)
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Erro ao obter empresa por website: {e}")
            raise DatabaseError(f"Falha ao recuperar empresa: {str(e)}") from e
    
    def listar_empresas_por_cidade(self, cidade: str) -> List[Empresa]:
        """Lista todas as empresas de uma cidade."""
        try:
            with self.conexao() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM empresas WHERE cidade = ? ORDER BY nome",
                    (cidade,)
                )
                rows = cursor.fetchall()
                return [self._row_para_empresa(row) for row in rows]
                
        except sqlite3.Error as e:
            logger.error(f"Erro ao listar empresas por cidade: {e}")
            raise DatabaseError(f"Falha ao listar empresas: {str(e)}") from e
    
    def listar_empresas_por_ramo(self, ramo: str) -> List[Empresa]:
        """Lista todas as empresas de um ramo específico."""
        try:
            with self.conexao() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM empresas WHERE ramo = ? ORDER BY nome",
                    (ramo,)
                )
                rows = cursor.fetchall()
                return [self._row_para_empresa(row) for row in rows]
                
        except sqlite3.Error as e:
            logger.error(f"Erro ao listar empresas por ramo: {e}")
            raise DatabaseError(f"Falha ao listar empresas: {str(e)}") from e
    
    def listar_todas_empresas(self, limite: int = 1000) -> List[Empresa]:
        """Lista todas as empresas com limite opcional."""
        try:
            with self.conexao() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM empresas ORDER BY data_coleta DESC LIMIT ?",
                    (limite,)
                )
                rows = cursor.fetchall()
                return [self._row_para_empresa(row) for row in rows]
                
        except sqlite3.Error as e:
            logger.error(f"Erro ao listar empresas: {e}")
            raise DatabaseError(f"Falha ao listar empresas: {str(e)}") from e
    
    def atualizar_status_empresa(self, empresa_id: int, novo_status: LeadStatus) -> None:
        """Atualiza o status de uma empresa."""
        try:
            with self.conexao() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE empresas SET status = ?, ultima_atualizacao = ? WHERE id = ?",
                    (novo_status.value, datetime.now(), empresa_id)
                )
                conn.commit()
                logger.debug(f"Status da empresa {empresa_id} atualizado para {novo_status.value}")
                
        except sqlite3.Error as e:
            logger.error(f"Erro ao atualizar status: {e}")
            raise DatabaseError(f"Falha ao atualizar status: {str(e)}") from e
    
    def obter_estatisticas(self) -> dict[str, Any]:
        """Retorna estatísticas gerais do banco de dados."""
        try:
            with self.conexao() as conn:
                cursor = conn.cursor()
                
                # Total de empresas
                cursor.execute("SELECT COUNT(*) FROM empresas")
                total = cursor.fetchone()[0]
                
                # Por status
                cursor.execute("""
                    SELECT status, COUNT(*) FROM empresas 
                    GROUP BY status
                """)
                por_status = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Por cidade (top 10)
                cursor.execute("""
                    SELECT cidade, COUNT(*) FROM empresas 
                    GROUP BY cidade 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 10
                """)
                por_cidade = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Por ramo (top 10)
                cursor.execute("""
                    SELECT ramo, COUNT(*) FROM empresas 
                    GROUP BY ramo 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 10
                """)
                por_ramo = {row[0]: row[1] for row in cursor.fetchall()}
                
                return {
                    'total_empresas': total,
                    'por_status': por_status,
                    'por_cidade': por_cidade,
                    'por_ramo': por_ramo
                }
                
        except sqlite3.Error as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            raise DatabaseError(f"Falha ao obter estatísticas: {str(e)}") from e
    
    @staticmethod
    def _row_para_empresa(row: sqlite3.Row) -> Empresa:
        """Converte uma linha do banco para objeto Empresa."""
        return Empresa(
            nome=row['nome'],
            website=row['website'],
            email=row['email'],
            telefone=row['telefone'],
            endereco=row['endereco'],
            cidade=row['cidade'],
            estado=row['estado'],
            ramo=row['ramo'],
            fonte=LeadSource(row['fonte']),
            status=LeadStatus(row['status']),
            data_coleta=datetime.fromisoformat(row['data_coleta']) if isinstance(row['data_coleta'], str) else row['data_coleta'],
            ultima_atualizacao=datetime.fromisoformat(row['ultima_atualizacao']) if isinstance(row['ultima_atualizacao'], str) else row['ultima_atualizacao']
        )
