import os
import psycopg2

def get_db_connection():
    """Conecta ao banco de dados usando variáveis de ambiente."""
    DB_HOST = os.environ.get('DB_HOST', 'db')
    DB_NAME = os.environ.get('DB_NAME', 'my_database')
    DB_USER = os.environ.get('DB_USER', 'user')
    DB_PASS = os.environ.get('DB_PASS', 'password')
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar com o banco de dados: {e}")
        return None