# -*- coding: utf-8 -*-
from app.database.connection import get_connection
import bcrypt


def listar_usuarios():
    """Retorna todos os usuarios cadastrados."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, perfil, ativo, criado_em FROM usuarios ORDER BY nome ASC")
    usuarios = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return usuarios


def buscar_usuario(usuario_id: int):
    """Retorna um usuario pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, perfil, ativo FROM usuarios WHERE id = ?", (usuario_id,))
    usuario = cursor.fetchone()
    conn.close()
    return dict(usuario) if usuario else None


def criar_usuario(nome: str, email: str, senha: str, perfil: str):
    """Cria um novo usuario com senha criptografada."""
    conn = get_connection()
    cursor = conn.cursor()

    # Verifica se o e-mail ja existe
    cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return None, "E-mail ja cadastrado no sistema."

    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    cursor.execute("""
        INSERT INTO usuarios (nome, email, senha, perfil, ativo)
        VALUES (?, ?, ?, ?, 1)
    """, (nome, email, senha_hash, perfil))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id, None


def atualizar_usuario(usuario_id: int, nome: str, email: str, perfil: str):
    """Atualiza nome, email e perfil de um usuario."""
    conn = get_connection()
    cursor = conn.cursor()

    # Verifica se o e-mail ja pertence a outro usuario
    cursor.execute("SELECT id FROM usuarios WHERE email = ? AND id != ?", (email, usuario_id))
    if cursor.fetchone():
        conn.close()
        return False, "E-mail ja em uso por outro usuario."

    cursor.execute("""
        UPDATE usuarios SET nome = ?, email = ?, perfil = ? WHERE id = ?
    """, (nome, email, perfil, usuario_id))
    conn.commit()
    conn.close()
    return True, None


def trocar_senha(usuario_id: int, senha_atual: str, nova_senha: str):
    """Troca a senha do usuario apos validar a senha atual."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT senha FROM usuarios WHERE id = ?", (usuario_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return False, "Usuario nao encontrado."

    if not bcrypt.checkpw(senha_atual.encode(), row["senha"].encode()):
        conn.close()
        return False, "Senha atual incorreta."

    nova_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
    cursor.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (nova_hash, usuario_id))
    conn.commit()
    conn.close()
    return True, None


def alternar_ativo(usuario_id: int):
    """Ativa ou desativa um usuario."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ativo FROM usuarios WHERE id = ?", (usuario_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return

    novo_estado = 0 if row["ativo"] == 1 else 1
    cursor.execute("UPDATE usuarios SET ativo = ? WHERE id = ?", (novo_estado, usuario_id))
    conn.commit()
    conn.close()


def contar_usuarios():
    """Retorna o total de usuarios ativos."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE ativo = 1")
    total = cursor.fetchone()[0]
    conn.close()
    return total