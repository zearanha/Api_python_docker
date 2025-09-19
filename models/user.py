import psycopg2
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class User:
    """Representa o Model do Usuário e suas operações de banco de dados."""

    @staticmethod
    def create_user(conn, name, password):
        """Cria um novo usuário com senha hash."""
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (name, password) VALUES (%s, %s) RETURNING id;", (name, password_hash))
                new_user_id = cur.fetchone()[0]
                conn.commit()
                return new_user_id
        except psycopg2.Error as e:
            conn.rollback()
            raise e

    @staticmethod
    def get_user_by_name(conn, name):
        """Busca um usuário pelo nome."""
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, password FROM users WHERE name = %s", (name,))
                user = cur.fetchone()
                if user:
                    return {"id": user[0], "name": user[1], "password_hash": user[2]}
                return None
        except psycopg2.Error as e:
            raise e
    
    @staticmethod
    def get_all_users(conn):
        """Busca todos os usuários do banco de dados."""
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name FROM users ORDER BY id;")
                users = cur.fetchall()
                return [{"id": user[0], "name": user[1]} for user in users]
        except psycopg2.Error as e:
            raise e
    
    @staticmethod
    def get_user_by_id(conn, user_id):
        """Busca um único usuário por ID."""
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name FROM users WHERE id = %s;", (user_id,))
                user = cur.fetchone()
                if user:
                    return {"id": user[0], "name": user[1]}
                return None
        except psycopg2.Error as e:
            raise e

    @staticmethod
    def update_user(conn, user_id, new_name, new_password=None):
        """Atualiza um usuário existente."""
        try:
            with conn.cursor() as cur:
                if new_password:
                    password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
                    cur.execute("UPDATE users SET name = %s, password = %s WHERE id = %s RETURNING id;", (new_name, password_hash, user_id))
                else:
                    cur.execute("UPDATE users SET name = %s WHERE id = %s RETURNING id;", (new_name, user_id))
                
                updated_id = cur.fetchone()
                if updated_id:
                    conn.commit()
                    return True
                return False
        except psycopg2.Error as e:
            conn.rollback()
            raise e

    @staticmethod
    def delete_user(conn, user_id):
        """Deleta um usuário por ID."""
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
                deleted_id = cur.fetchone()
                if deleted_id:
                    conn.commit()
                    return True
                return False
        except psycopg2.Error as e:
            conn.rollback()
            raise e