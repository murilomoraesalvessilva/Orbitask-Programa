import bcrypt
from app.database.connection import get_connection


def fazer_login(email: str, senha: str):
    """
    Verifica as credenciais do usuário.
    Retorna os dados do usuário se válido, ou None se inválido.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE email = ? AND ativo = 1", (email,))
    usuario = cursor.fetchone()
    conn.close()

    if usuario is None:
        return None

    senha_correta = bcrypt.checkpw(senha.encode(), usuario["senha"].encode())
    if not senha_correta:
        return None

    return dict(usuario)