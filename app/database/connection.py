# -*- coding: utf-8 -*-
import sqlite3
import os
import sys


def obter_diretorio_base():
    """
    Retorna o diretorio correto onde o banco de dados deve ficar.

    - Quando rodando como .exe (PyInstaller), sys.frozen é True e
      sys.executable aponta para o proprio .exe. Usamos a pasta
      onde o .exe esta, NAO a pasta temporaria de extracao (_MEIPASS).
    - Quando rodando via 'python main.py' (desenvolvimento), usamos
      a pasta raiz do projeto normalmente.
    """
    if getattr(sys, 'frozen', False):
        # Rodando como executavel empacotado
        return os.path.dirname(sys.executable)
    else:
        # Rodando como script Python normal
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


BASE_DIR = obter_diretorio_base()
DB_PATH = os.path.join(BASE_DIR, "orbitask.db")


def get_connection():
    """Retorna uma conexao com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn