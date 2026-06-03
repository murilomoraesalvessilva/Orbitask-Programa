from app.database.connection import get_connection
import bcrypt


def criar_tabelas():
    """Cria todas as tabelas necessárias no banco de dados."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL DEFAULT 'tecnico',  -- admin | tecnico
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de clientes
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

    # Tabela de ordens de serviço
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            status TEXT NOT NULL DEFAULT 'aberta',  -- aberta | em_andamento | concluida | cancelada
            prioridade TEXT NOT NULL DEFAULT 'normal',  -- baixa | normal | alta | urgente
            cliente_id INTEGER,
            tecnico_id INTEGER,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (tecnico_id) REFERENCES usuarios(id)
        )
    """)

    conn.commit()
    conn.close()


def criar_admin_padrao():
    """Cria o usuário admin padrão se não existir nenhum usuário."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total = cursor.fetchone()[0]

    if total == 0:
        senha_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, perfil)
            VALUES (?, ?, ?, ?)
        """, ("Administrador", "admin@orbitask.com", senha_hash, "admin"))
        conn.commit()
        print("✅ Usuário admin criado: admin@orbitask.com | senha: admin123")

    conn.close()


def inicializar_banco():
    """Inicializa o banco: cria tabelas e admin padrão."""
    criar_tabelas()
    criar_admin_padrao()