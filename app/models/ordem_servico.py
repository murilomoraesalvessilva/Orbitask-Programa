# -*- coding: utf-8 -*-
from app.database.connection import get_connection


def listar_ordens(filtro_status: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT os.id, os.titulo, os.descricao, os.status, os.prioridade,
               os.prazo, os.criado_em, os.atualizado_em,
               c.id AS cliente_id, c.nome AS cliente_nome,
               u.id AS tecnico_id, u.nome AS tecnico_nome
        FROM ordens_servico os
        LEFT JOIN clientes c ON os.cliente_id = c.id
        LEFT JOIN usuarios u ON os.tecnico_id = u.id
    """
    if filtro_status:
        cursor.execute(query + " WHERE os.status = ? ORDER BY os.criado_em DESC", (filtro_status,))
    else:
        cursor.execute(query + " ORDER BY os.criado_em DESC")
    ordens = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return ordens


def buscar_ordem(ordem_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ordens_servico WHERE id = ?", (ordem_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def criar_ordem(titulo, descricao, prioridade, prazo, cliente_id, tecnico_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ordens_servico (titulo, descricao, prioridade, prazo, cliente_id, tecnico_id, status)
        VALUES (?, ?, ?, ?, ?, ?, 'aberta')
    """, (titulo, descricao, prioridade, prazo or None, cliente_id or None, tecnico_id or None))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def atualizar_ordem(ordem_id, titulo, descricao, status, prioridade, prazo, cliente_id, tecnico_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE ordens_servico
        SET titulo=?, descricao=?, status=?, prioridade=?, prazo=?,
            cliente_id=?, tecnico_id=?, atualizado_em=CURRENT_TIMESTAMP
        WHERE id=?
    """, (titulo, descricao, status, prioridade, prazo or None,
          cliente_id or None, tecnico_id or None, ordem_id))
    conn.commit()
    conn.close()


def deletar_ordem(ordem_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ordens_servico WHERE id = ?", (ordem_id,))
    conn.commit()
    conn.close()


def contar_por_status():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) as total FROM ordens_servico GROUP BY status")
    resultado = {row["status"]: row["total"] for row in cursor.fetchall()}
    conn.close()
    return resultado


def listar_prazos():
    """Retorna datas de prazo de OS abertas ou em andamento para o calendario."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT prazo, COUNT(*) as total, status
        FROM ordens_servico
        WHERE prazo IS NOT NULL
          AND status IN ('aberta', 'em_andamento')
        GROUP BY prazo
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows