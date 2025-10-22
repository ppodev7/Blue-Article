from flask import Blueprint, request, jsonify
from models.user import User
from models import db

from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error':'Email já cadastrado'}), 400
    user = User(nome=data['nome'], email=data['email'])
    user.set_password(data['senha'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message':'Usuário cadastrado com sucesso!'})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['senha']):
        return jsonify({'message':'Login bem-sucedido','role':user.role})
    return jsonify({'error':'Credenciais inválidas'}), 401
