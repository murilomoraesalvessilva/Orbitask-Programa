# -*- coding: utf-8 -*-
from app.database.connection import get_connection


def listar_equipamentos(ordem_id: int = None):
    """Retorna equipamentos, opcionalmente filtrados por OS."""
    conn = get_connection()
    cursor = conn.cursor()

    if ordem_id:
        cursor.execute("""
            SELECT e.*, os.titulo AS ordem_titulo
            FROM equipamentos e
            LEFT JOIN ordens_servico os ON e.ordem_id = os.id
            WHERE e.ordem_id = ?
            ORDER BY e.nome ASC
        """, (ordem_id,))
    else:
        cursor.execute("""
            SELECT e.*, os.titulo AS ordem_titulo
            FROM equipamentos e
            LEFT JOIN ordens_servico os ON e.ordem_id = os.id
            ORDER BY e.nome ASC
        """)

    equipamentos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return equipamentos


def buscar_equipamento(equip_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipamentos WHERE id = ?", (equip_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def criar_equipamento(nome: str, tipo: str, marca: str, modelo: str,
                      numero_serie: str, descricao: str, ordem_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO equipamentos (nome, tipo, marca, modelo, numero_serie, descricao, ordem_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, tipo, marca, modelo, numero_serie, descricao, ordem_id or None))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def atualizar_equipamento(equip_id: int, nome: str, tipo: str, marca: str, modelo: str,
                           numero_serie: str, descricao: str, ordem_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE equipamentos
        SET nome = ?, tipo = ?, marca = ?, modelo = ?,
            numero_serie = ?, descricao = ?, ordem_id = ?
        WHERE id = ?
    """, (nome, tipo, marca, modelo, numero_serie, descricao, ordem_id or None, equip_id))
    conn.commit()
    conn.close()


def deletar_equipamento(equip_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM equipamentos WHERE id = ?", (equip_id,))
    conn.commit()
    conn.close()


def contar_equipamentos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM equipamentos")
    total = cursor.fetchone()[0]
    conn.close()
    return total