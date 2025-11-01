# src/routes/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.controller.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__, template_folder='../../templates')

# Inicializa o controller que este blueprint usará
auth_controller = AuthController()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        
        user = auth_controller.login(email, password)
        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role # Adiciona o papel do usuário à sessão
            flash('Login realizado com sucesso!', 'success')
            # O url_for para rotas fora deste blueprint continua igual
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos!', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not name or not email or not password:
            flash('Todos os campos são obrigatórios!', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres!', 'error')
            return render_template('register.html')
        
        # Acessamos a configuração do app através do request context
        admin_email = request.environ.get('app.config', {}).get('ADMIN_EMAIL')
        user = auth_controller.register(name, email, password, admin_email=admin_email)
        
        if user:
            flash('Conta criada com sucesso! Faça login para continuar.', 'success')
            # O url_for para uma rota DENTRO deste blueprint precisa do prefixo 'auth.'
            return redirect(url_for('auth.login'))
        else:
            flash('Erro ao criar conta. Email já existe ou dados inválidos!', 'error')
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))
