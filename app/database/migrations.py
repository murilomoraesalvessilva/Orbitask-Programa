# -*- coding: utf-8 -*-
from app.database.connection import get_connection
import bcrypt


def criar_tabelas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL DEFAULT 'tecnico',
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            email TEXT,
            documento TEXT,
            endereco TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            status TEXT NOT NULL DEFAULT 'aberta',
            prioridade TEXT NOT NULL DEFAULT 'normal',
            prazo DATE,
            cliente_id INTEGER,
            tecnico_id INTEGER,
            valor_servico REAL DEFAULT 0.0,
            valor_pecas REAL DEFAULT 0.0,
            status_pagamento TEXT DEFAULT 'pendente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (tecnico_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT,
            marca TEXT,
            modelo TEXT,
            numero_serie TEXT,
            descricao TEXT,
            ordem_id INTEGER,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ordem_id) REFERENCES ordens_servico(id)
        )
    """)

    conn.commit()
    conn.close()


def migracoes_seguras():
    """Adiciona colunas novas em bancos ja existentes sem quebrar dados."""
    conn = get_connection()
    cursor = conn.cursor()
    colunas = [
        ("ALTER TABLE ordens_servico ADD COLUMN valor_servico REAL DEFAULT 0.0",),
        ("ALTER TABLE ordens_servico ADD COLUMN valor_pecas REAL DEFAULT 0.0",),
        ("ALTER TABLE ordens_servico ADD COLUMN status_pagamento TEXT DEFAULT 'pendente'",),
        ("ALTER TABLE ordens_servico ADD COLUMN prazo DATE",),
    ]
    for (sql,) in colunas:
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception:
            pass
    conn.close()


def criar_admin_padrao():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        senha_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, perfil)
            VALUES (?, ?, ?, ?)
        """, ("Administrador", "admin@orbitask.com", senha_hash, "admin"))
        conn.commit()
    conn.close()


def inicializar_banco():
    criar_tabelas()
    migracoes_seguras()
    criar_admin_padrao()