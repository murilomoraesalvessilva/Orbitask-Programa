# -*- coding: utf-8 -*-
from app.database.connection import get_connection


def listar_clientes():
    """Retorna todos os clientes cadastrados."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes ORDER BY nome ASC")
    clientes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return clientes


def buscar_cliente(cliente_id: int):
    """Retorna um cliente pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
    cliente = cursor.fetchone()
    conn.close()
    return dict(cliente) if cliente else None


def criar_cliente(nome: str, telefone: str, email: str, documento: str, endereco: str):
    """Cria um novo cliente no banco de dados."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clientes (nome, telefone, email, documento, endereco)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, telefone, email, documento, endereco))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def atualizar_cliente(cliente_id: int, nome: str, telefone: str, email: str, documento: str, endereco: str):
    """Atualiza os dados de um cliente existente."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clientes
        SET nome = ?, telefone = ?, email = ?, documento = ?, endereco = ?
        WHERE id = ?
    """, (nome, telefone, email, documento, endereco, cliente_id))
    conn.commit()
    conn.close()


def deletar_cliente(cliente_id: int):
    """Remove um cliente do banco de dados."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    conn.commit()
    conn.close()


def contar_clientes():
    """Retorna o total de clientes cadastrados."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clientes")
    total = cursor.fetchone()[0]
    conn.close()
    return total