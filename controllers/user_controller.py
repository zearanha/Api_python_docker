from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required
from models.user import User, bcrypt
from services.database import get_db_connection

# Cria um Blueprint para as rotas de usuário
user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/health', methods=['GET'])
def health_check():
    """Verifica a saúde da aplicação e a conexão com o banco de dados."""
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({"status": "ok", "message": "API e banco de dados estão operacionais."}), 200
    else:
        return jsonify({"status": "error", "message": "API operacional, mas falha na conexão com o banco de dados."}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    """Autentica um usuário e retorna um token JWT."""
    data = request.json
    name = data.get('name')
    password = data.get('password')

    if not name or not password:
        return jsonify({"msg": "Nome de usuário e senha são obrigatórios"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"msg": "Falha na conexão com o banco de dados"}), 500

    try:
        user_data = User.get_user_by_name(conn, name)
        if user_data and bcrypt.check_password_hash(user_data['password_hash'], password):
            access_token = create_access_token(identity=name)
            return jsonify(access_token=access_token)
        else:
            return jsonify({"msg": "Nome de usuário ou senha incorretos"}), 401
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    finally:
        if conn:
            conn.close()

@user_bp.route('/users', methods=['POST'])
def create_user():
    """Cria um novo usuário."""
    data = request.json
    name = data.get('name')
    password = data.get('password')
    if not name or not password:
        return jsonify({"status": "error", "message": "Nome e senha são obrigatórios."}), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Falha na conexão com o banco de dados."}), 500
    
    try:
        new_user_id = User.create_user(conn, name, password)
        return jsonify({"status": "ok", "message": "Usuário criado com sucesso.", "id": new_user_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if conn:
            conn.close()

@user_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Retorna todos os usuários."""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Falha na conexão com o banco de dados."}), 500
    try:
        users_list = User.get_all_users(conn)
        return jsonify(users_list)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if conn:
            conn.close()

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_by_id(user_id):
    """Retorna um usuário específico por ID."""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Falha na conexão com o banco de dados."}), 500
    try:
        user = User.get_user_by_id(conn, user_id)
        if user:
            return jsonify(user)
        else:
            return jsonify({"status": "error", "message": "Usuário não encontrado."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if conn:
            conn.close()

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Atualiza um usuário existente."""
    data = request.json
    new_name = data.get('name')
    new_password = data.get('password')
    
    if not new_name and not new_password:
        return jsonify({"status": "error", "message": "Pelo menos um campo ('name' ou 'password') deve ser fornecido."}), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Falha na conexão com o banco de dados."}), 500
    
    try:
        updated = User.update_user(conn, user_id, new_name, new_password)
        if updated:
            return jsonify({"status": "ok", "message": "Usuário atualizado com sucesso."})
        else:
            return jsonify({"status": "error", "message": "Usuário não encontrado."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if conn:
            conn.close()

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Deleta um usuário por ID."""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Falha na conexão com o banco de dados."}), 500
    
    try:
        deleted = User.delete_user(conn, user_id)
        if deleted:
            return jsonify({"status": "ok", "message": "Usuário deletado com sucesso."})
        else:
            return jsonify({"status": "error", "message": "Usuário não encontrado."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if conn:
            conn.close()