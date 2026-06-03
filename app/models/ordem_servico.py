# -*- coding: utf-8 -*-
from app.database.connection import get_connection


def listar_ordens(filtro_status: str = None):
    """Retorna todas as ordens de servico, com join em cliente e tecnico."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            os.id,
            os.titulo,
            os.descricao,
            os.status,
            os.prioridade,
            os.criado_em,
            os.atualizado_em,
            c.id AS cliente_id,
            c.nome AS cliente_nome,
            u.id AS tecnico_id,
            u.nome AS tecnico_nome
        FROM ordens_servico os
        LEFT JOIN clientes c ON os.cliente_id = c.id
        LEFT JOIN usuarios u ON os.tecnico_id = u.id
    """

    if filtro_status:
        query += " WHERE os.status = ?"
        cursor.execute(query + " ORDER BY os.criado_em DESC", (filtro_status,))
    else:
        cursor.execute(query + " ORDER BY os.criado_em DESC")

    ordens = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return ordens


def buscar_ordem(ordem_id: int):
    """Retorna uma ordem de servico pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ordens_servico WHERE id = ?", (ordem_id,))
    ordem = cursor.fetchone()
    conn.close()
    return dict(ordem) if ordem else None


def criar_ordem(titulo: str, descricao: str, prioridade: str, cliente_id: int, tecnico_id: int):
    """Cria uma nova ordem de servico."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ordens_servico (titulo, descricao, prioridade, cliente_id, tecnico_id, status)
        VALUES (?, ?, ?, ?, ?, 'aberta')
    """, (titulo, descricao, prioridade, cliente_id or None, tecnico_id or None))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def atualizar_ordem(ordem_id: int, titulo: str, descricao: str, status: str,
                     prioridade: str, cliente_id: int, tecnico_id: int):
    """Atualiza os dados de uma ordem de servico."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE ordens_servico
        SET titulo = ?, descricao = ?, status = ?, prioridade = ?,
            cliente_id = ?, tecnico_id = ?,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (titulo, descricao, status, prioridade,
          cliente_id or None, tecnico_id or None, ordem_id))
    conn.commit()
    conn.close()


def deletar_ordem(ordem_id: int):
    """Remove uma ordem de servico."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ordens_servico WHERE id = ?", (ordem_id,))
    conn.commit()
    conn.close()


def contar_por_status():
    """Retorna contagem de OS agrupadas por status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status, COUNT(*) as total
        FROM ordens_servico
        GROUP BY status
    """)
    resultado = {row["status"]: row["total"] for row in cursor.fetchall()}
    conn.close()
    return resultado