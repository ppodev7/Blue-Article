from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import csv
from io import StringIO

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blue_article.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ADMIN_EMAIL'] = 'admin@bluearticle.com'  # E-mail do administrador

# Importar modelos primeiro
from src.model.models import db, User, Article, Category

# Inicializar SQLAlchemy com a app
db.init_app(app)

# Importar controllers
from src.controller.article_controller import ArticleController
from src.controller.user_controller import UserController
from src.controller.auth_controller import AuthController
# Importar o blueprint de autenticação
from src.routes.auth import auth_bp
# Importar o blueprint de artigos
from src.routes.articles import articles_bp

# Inicializar controllers
article_controller = ArticleController()
user_controller = UserController()
auth_controller = AuthController()

# Registrar os blueprints na aplicação
app.register_blueprint(auth_bp)
app.register_blueprint(articles_bp)

# Rotas principais
@app.route('/')
def index():
    """Página inicial - lista de artigos"""
    articles = article_controller.get_all_articles()
    return render_template('index.html', articles=articles)

@app.route('/search')
def search():
    """Buscar artigos"""
    # Capturar todos os parâmetros da URL
    query = request.args.get('q', '').strip()
    category_id = request.args.get('category_id', type=int)
    has_file = request.args.get('has_file') == '1'
    sort = request.args.get('sort', 'newest')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    # A lógica de busca agora pode usar todos os filtros
    articles = article_controller.search_articles(query) # Nota: search_articles precisará ser atualizado para usar os novos filtros
    
    categories = Category.query.all()
    
    return render_template('search.html', 
                           articles=articles, 
                           query=query, 
                           categories=categories,
                           selected_category=category_id,
                           has_file=has_file, sort=sort,
                           date_from=date_from, date_to=date_to)

@app.route('/dashboard')
def dashboard():
    """Dashboard do usuário"""
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar o dashboard!', 'error')
        return redirect(url_for('auth.login'))
    
    user_articles = article_controller.get_user_articles(session['user_id'])
    return render_template('dashboard.html', articles=user_articles)

@app.route('/api/track-view/<int:article_id>', methods=['POST'])
def track_view(article_id):
    """Endpoint para rastrear visualizações de artigos."""
    # Não é necessário verificar login para visualizações, mas pode ser adicionado se desejar.
    # if 'user_id' not in session:
    #     return jsonify({'message': 'Unauthorized'}), 401

    if article_controller.increment_views(article_id):
        return jsonify({'message': 'View tracked successfully'}), 200
    else:
        # Retorna 404 se o artigo não for encontrado ou 500 se houver erro no incremento
        return jsonify({'message': 'Failed to track view or article not found'}), 404


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/export_csv')
def export_csv():
    """Exportar resultados da busca para CSV"""
    if 'user_id' not in session:
        flash('Você precisa estar logado para exportar dados.', 'error')
        return redirect(url_for('auth.login'))

    # Reutilizar a lógica de busca
    query = request.args.get('q', '').strip()
    # Adicione outros filtros se a busca for mais complexa
    articles = article_controller.search_articles(query)

    # Criar CSV em memória
    output = StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho do CSV
    writer.writerow(['ID', 'Title', 'Author', 'Category', 'Keywords', 'Views', 'Downloads', 'Created At'])
    
    # Linhas do CSV
    for article in articles:
        writer.writerow([
            article.id, article.title, article.author.name, article.category.name,
            article.keywords, article.views_count, article.downloads_count,
            article.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    
    return output.getvalue(), 200, {'Content-Disposition': 'attachment; filename=articles.csv', 'Content-Type': 'text/csv'}

# Criar tabelas do banco de dados
def create_tables():
    """Criar tabelas do banco de dados"""
    with app.app_context():
        db.create_all()
        
        # Criar categorias padrão se não existirem
        if Category.query.count() == 0:
            default_categories = [
                Category(name='Ciências Exatas'),
                Category(name='Ciências Humanas'),
                Category(name='Ciências Biológicas'),
                Category(name='Engenharias'),
                Category(name='Tecnologia da Informação'),
                Category(name='Artes e Design'),
                Category(name='Medicina'),
                Category(name='Direito'),
                Category(name='Administração'),
                Category(name='Outros')
            ]
            
            for category in default_categories:
                db.session.add(category)
            
            db.session.commit()
            print("Categorias padrão criadas com sucesso!")
        
        # Criar usuários de exemplo se não existirem
        if User.query.count() == 0:
            print("Criando usuários de exemplo...")
            admin_email = app.config['ADMIN_EMAIL']
            # Admin
            auth_controller.register('Admin User', admin_email, 'admin123', admin_email=admin_email)
            # Autor
            auth_controller.register('Autor Exemplo', 'autor@exemplo.com', 'autor123', admin_email=admin_email)
            # Leitor
            auth_controller.register('Leitor Exemplo', 'leitor@exemplo.com', 'leitor123', admin_email=admin_email)

# Adicionar o app.config ao ambiente para que os blueprints possam acessá-lo
@app.before_request
def before_request_func():
    if 'app.config' not in request.environ:
        request.environ['app.config'] = app.config

if __name__ == '__main__':
    create_tables()  # Criar tabelas na primeira execução
    app.run(debug=True, host='0.0.0.0', port=5000)
