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

# Inicializar controllers
article_controller = ArticleController()
user_controller = UserController()
auth_controller = AuthController()

# Rotas principais
@app.route('/')
def index():
    """Página inicial - lista de artigos"""
    articles = article_controller.get_all_articles()
    return render_template('index.html', articles=articles)

@app.route('/article/<int:article_id>')
def view_article(article_id):
    """Visualizar artigo específico"""
    article = article_controller.get_article_by_id(article_id)
    if not article:
        flash('Artigo não encontrado!', 'error')
        return redirect(url_for('index'))
    return render_template('article_detail.html', article=article)

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        
        user = auth_controller.login(email, password)
        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validações básicas
        if not name or not email or not password:
            flash('Todos os campos são obrigatórios!', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres!', 'error')
            return render_template('register.html')
        
        # Tentar criar o usuário
        user = auth_controller.register(name, email, password, admin_email=app.config['ADMIN_EMAIL'])
        if user:
            flash('Conta criada com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Erro ao criar conta. Email já existe ou dados inválidos!', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Dashboard do usuário"""
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar o dashboard!', 'error')
        return redirect(url_for('login'))
    
    user_articles = article_controller.get_user_articles(session['user_id'])
    return render_template('dashboard.html', articles=user_articles)

@app.route('/add_article', methods=['GET', 'POST'])
def add_article():
    """Adicionar novo artigo"""
    if 'user_id' not in session:
        flash('Você precisa fazer login para adicionar artigos!', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        abstract = request.form['abstract']
        content = request.form['content']
        category_id = request.form['category_id']
        keywords = request.form['keywords']
        pdf_file = request.files.get('file')
        cover_file = request.files.get('cover')

        pdf_path = None
        if pdf_file and pdf_file.filename != '':
            filename = secure_filename(pdf_file.filename)
            relative_pdf_path = os.path.join('pdfs', filename)
            pdf_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'pdfs') # Absolute path to save
            os.makedirs(pdf_folder, exist_ok=True)
            pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], relative_pdf_path))
            pdf_path = relative_pdf_path # Store relative path in DB

        cover_path = None
        if cover_file and cover_file.filename != '':
            filename = secure_filename(cover_file.filename)
            cover_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'covers')
            os.makedirs(cover_folder, exist_ok=True)
            # Salva o caminho relativo para ser usado no template
            cover_path = os.path.join('covers', filename)
            cover_file.save(os.path.join(app.config['UPLOAD_FOLDER'], cover_path))
        
        if article_controller.create_article(
            title=title,
            abstract=abstract,
            content=content,
            category_id=category_id,
            keywords=keywords,
            user_id=session['user_id'],
            file_path=pdf_path,
            cover_path=cover_path
        ):
            flash('Artigo adicionado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Erro ao adicionar artigo!', 'error')
    
    categories = Category.query.all()
    return render_template('add_article.html', categories=categories)

@app.route('/edit_article/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    """Editar artigo"""
    if 'user_id' not in session:
        flash('Você precisa fazer login para editar artigos!', 'error')
        return redirect(url_for('login'))
    
    article = article_controller.get_article_by_id(article_id)
    if not article or article.user_id != session['user_id']:
        flash('Artigo não encontrado ou você não tem permissão para editá-lo!', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form['title']
        abstract = request.form['abstract']
        content = request.form['content']
        category_id = request.form['category_id']
        keywords = request.form['keywords']
        
        if article_controller.update_article(
            article_id=article_id,
            title=title,
            abstract=abstract,
            content=content,
            category_id=category_id,
            keywords=keywords
        ):
            flash('Artigo atualizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Erro ao atualizar artigo!', 'error')
    
    categories = Category.query.all()
    return render_template('edit_article.html', article=article, categories=categories)

@app.route('/delete_article/<int:article_id>')
def delete_article(article_id):
    """Deletar artigo"""
    if 'user_id' not in session:
        flash('Você precisa fazer login para deletar artigos!', 'error')
        return redirect(url_for('login'))
    
    article = article_controller.get_article_by_id(article_id)
    if not article or article.user_id != session['user_id']:
        flash('Artigo não encontrado ou você não tem permissão para deletá-lo!', 'error')
        return redirect(url_for('dashboard'))
    
    if article_controller.delete_article(article_id):
        flash('Artigo deletado com sucesso!', 'success')
    else:
        flash('Erro ao deletar artigo!', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/download_article/<int:article_id>')
def download_article(article_id):
    """Fornece o download do PDF de um artigo"""
    if 'user_id' not in session:
        flash('Você precisa estar logado para baixar artigos.', 'warning')
        return redirect(url_for('login'))

    article = article_controller.get_article_by_id(article_id)
    full_file_path = os.path.join(app.config['UPLOAD_FOLDER'], article.file_path) if article and article.file_path else None
    if not full_file_path or not os.path.exists(full_file_path):
        flash('Arquivo não encontrado ou indisponível.', 'error')
        return redirect(url_for('view_article', article_id=article_id))

    article.increment_download()
    # Use UPLOAD_FOLDER as the base directory and file_path as the relative path
    return send_from_directory(app.config['UPLOAD_FOLDER'], article.file_path, as_attachment=True)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/export_csv')
def export_csv():
    """Exportar resultados da busca para CSV"""
    if 'user_id' not in session:
        flash('Você precisa estar logado para exportar dados.', 'error')
        return redirect(url_for('login'))

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

if __name__ == '__main__':
    create_tables()  # Criar tabelas na primeira execução
    app.run(debug=True, host='0.0.0.0', port=5000)
