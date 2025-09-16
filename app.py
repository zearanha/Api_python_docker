import os
import psycopg2
from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY', 'default-super-secreta')
jwt = JWTManager(app)

# Inicializa o Bcrypt para hashing de senhas
bcrypt = Bcrypt(app)

# Configurações do banco de dados (mesmas do docker-compose.yml)
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_NAME = os.environ.get('DB_NAME', 'my_database')
DB_USER = os.environ.get('DB_USER', 'user')
DB_PASS = os.environ.get('DB_PASS', 'password')

def get_db_connection():
    """Conecta ao banco de dados."""
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


# Rota de health check para verificar a conexão com o banco de dados
@app.route('/health', methods=['GET'])
def health_check():
    """
    Verifica a saúde da aplicação e a conexão com o banco de dados.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            return jsonify({"status": "ok", "message": "API e banco de dados estão operacionais."}), 200
        else:
            return jsonify({"status": "error", "message": "API operacional, mas falha na conexão com o banco de dados."}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro inesperado: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# --- Rota de Autenticação (Login) ---
@app.route('/login', methods=['POST'])
def login():
    """Autentica o usuário e retorna um token JWT."""
    data = request.json
    name = data.get('name', None)
    password = data.get('password', None)

    if not name or not password:
        return jsonify({"msg": "Nome de usuário e senha são obrigatórios"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"msg": "Falha na conexão com o banco de dados"}), 500

    try:
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE name = %s", (name,))
        user_password_hash = cur.fetchone()
        cur.close()
        conn.close()

        if user_password_hash and bcrypt.check_password_hash(user_password_hash[0], password):
            access_token = create_access_token(identity=name)
            return jsonify(access_token=access_token)
        else:
            return jsonify({"msg": "Nome de usuário ou senha incorretos"}), 401
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

# --- Rotas CRUD Protegidas ---

# GET All Users (Protegida)
@app.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Retorna todos os usuários."""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Falha na conexão com o banco de dados."}), 500
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM users ORDER BY id;")
        users = cur.fetchall()
        cur.close()
        conn.close()
        
        users_list = [{"id": user[0], "name": user[1]} for user in users]
        return jsonify(users_list)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# GET User by ID (Protegida)
@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_by_id(user_id):
    """Retorna um usuário específico por ID."""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Falha na conexão com o banco de dados."}), 500
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM users WHERE id = %s;", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            return jsonify({"id": user[0], "name": user[1]})
        else:
            return jsonify({"status": "error", "message": "Usuário não encontrado."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# POST (Criar Usuário)
@app.route('/users', methods=['POST'])
def create_user():
    """Cria um novo usuário com hash de senha."""
    data = request.json
    name = data.get('name')
    password = data.get('password')
    if not name or not password:
        return jsonify({"status": "error", "message": "Nome e senha são obrigatórios."}), 400
    
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Falha na conexão com o banco de dados."}), 500
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, password) VALUES (%s, %s) RETURNING id;", (name, password_hash))
        new_user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "ok", "message": "Usuário criado com sucesso.", "id": new_user_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# PUT (Atualizar Usuário)
@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Atualiza um usuário existente por ID."""
    data = request.json
    new_name = data.get('name')
    new_password = data.get('password')
    
    if not new_name and not new_password:
        return jsonify({"status": "error", "message": "Pelo menos um campo ('name' ou 'password') deve ser fornecido."}), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Falha na conexão com o banco de dados."}), 500
    try:
        cur = conn.cursor()
        if new_password:
            password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            cur.execute("UPDATE users SET name = %s, password = %s WHERE id = %s RETURNING id;", (new_name, password_hash, user_id))
        else:
            cur.execute("UPDATE users SET name = %s WHERE id = %s RETURNING id;", (new_name, user_id))

        updated_id = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if updated_id:
            return jsonify({"status": "ok", "message": "Usuário atualizado com sucesso."})
        else:
            return jsonify({"status": "error", "message": "Usuário não encontrado."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# DELETE a User (Protegida)
@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Deleta um usuário por ID."""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Falha na conexão com o banco de dados."}), 500
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
        deleted_id = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if deleted_id:
            return jsonify({"status": "ok", "message": "Usuário deletado com sucesso."})
        else:
            return jsonify({"status": "error", "message": "Usuário não encontrado."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)