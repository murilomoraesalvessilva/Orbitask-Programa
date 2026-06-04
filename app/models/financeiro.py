# -*- coding: utf-8 -*-
from app.database.connection import get_connection


STATUS_PAGAMENTO = [
    ("pendente",  "Pendente"),
    ("pago",      "Pago"),
    ("cancelado", "Cancelado"),
]


def listar_financeiro(filtro_pagamento: str = None):
    """Retorna OS com informacoes financeiras."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            os.id,
            os.titulo,
            os.status,
            os.status_pagamento,
            os.valor_servico,
            os.valor_pecas,
            (os.valor_servico + os.valor_pecas) AS valor_total,
            os.criado_em,
            c.nome AS cliente_nome,
            u.nome AS tecnico_nome
        FROM ordens_servico os
        LEFT JOIN clientes c ON os.cliente_id = c.id
        LEFT JOIN usuarios u ON os.tecnico_id = u.id
    """

    if filtro_pagamento:
        query += " WHERE os.status_pagamento = ?"
        cursor.execute(query + " ORDER BY os.criado_em DESC", (filtro_pagamento,))
    else:
        cursor.execute(query + " ORDER BY os.criado_em DESC")

    registros = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return registros


def atualizar_financeiro(ordem_id: int, valor_servico: float,
                          valor_pecas: float, status_pagamento: str):
    """Atualiza os campos financeiros de uma OS."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE ordens_servico
        SET valor_servico = ?, valor_pecas = ?,
            status_pagamento = ?, atualizado_em = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (valor_servico, valor_pecas, status_pagamento, ordem_id))
    conn.commit()
    conn.close()


def resumo_financeiro():
    """Retorna totais financeiros do sistema."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total_os,
            COALESCE(SUM(valor_servico + valor_pecas), 0) AS receita_total,
            COALESCE(SUM(CASE WHEN status_pagamento = 'pago'
                THEN valor_servico + valor_pecas ELSE 0 END), 0) AS receita_recebida,
            COALESCE(SUM(CASE WHEN status_pagamento = 'pendente'
                THEN valor_servico + valor_pecas ELSE 0 END), 0) AS receita_pendente,
            COUNT(CASE WHEN status_pagamento = 'pago' THEN 1 END) AS os_pagas,
            COUNT(CASE WHEN status_pagamento = 'pendente' THEN 1 END) AS os_pendentes,
            COUNT(CASE WHEN status_pagamento = 'cancelado' THEN 1 END) AS os_canceladas
        FROM ordens_servico
    """)

    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}