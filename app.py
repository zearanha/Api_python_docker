import os
from flask import Flask
from flask_jwt_extended import JWTManager

from controllers.user_controller import user_bp

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY', 'default-super-secreta')
jwt = JWTManager(app)

app.register_blueprint(user_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)