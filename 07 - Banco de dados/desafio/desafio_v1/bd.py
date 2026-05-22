import sqlite3
from sqlite3 import Connection, Cursor


def criar_bd(cursor: Cursor) -> None:
    # Criação da tabela única de clientes para armazenar tanto PF quanto PJ
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT EXISTS,
            telefone TEXT,
            status TEXT DEFAULT 'ativo',
            tipo_cliente TEXT NOT EXISTS, -- Armazena 'PF' ou 'PJ'
            -- Campos específicos de Pessoa Física
            nome TEXT,
            cpf TEXT UNIQUE,
            renda_mensal REAL,
            -- Campos específicos de Pessoa Jurídica
            nome_fantasia TEXT,
            cnpj TEXT UNIQUE,
            faturamento_anual REAL
        );
    """)


def criar_conexao() -> Connection:
    # Conecta ou cria o arquivo do banco de dados na raiz da execução
    conexao = sqlite3.connect("db.sqlite")
    # Ativa restrições importantes como chaves estrangeiras e a regra de UNIQUE
    conexao.execute("PRAGMA foreign_keys = ON;") 
    return conexao
