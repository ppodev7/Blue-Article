from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# SQLAlchemy será inicializado no app.py
db = SQLAlchemy()

class User(db.Model):
    """Modelo para usuários do sistema"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com artigos
    articles = db.relationship('Article', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Define a senha do usuário"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Converte o usuário para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'articles_count': len(self.articles)
        }
    
    def __repr__(self):
        return f'<User {self.name}>'

class Category(db.Model):
    """Modelo para categorias de artigos"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com artigos
    articles = db.relationship('Article', backref='category', lazy=True)
    
    def to_dict(self):
        """Converte a categoria para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'articles_count': len(self.articles)
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Article(db.Model):
    """Modelo para artigos acadêmicos"""
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text)  # Palavras-chave separadas por vírgula
    file_path = db.Column(db.String(500))  # Caminho para arquivo PDF (opcional)
    status = db.Column(db.String(20), default='published')  # published, draft, review
    views_count = db.Column(db.Integer, default=0)
    downloads_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Chaves estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    def increment_view(self):
        """Incrementa o contador de visualizações"""
        self.views_count += 1
        db.session.commit()
    
    def increment_download(self):
        """Incrementa o contador de downloads"""
        self.downloads_count += 1
        db.session.commit()
    
    def get_keywords_list(self):
        """Retorna lista de palavras-chave"""
        if self.keywords:
            return [keyword.strip() for keyword in self.keywords.split(',')]
        return []
    
    def set_keywords_from_list(self, keywords_list):
        """Define palavras-chave a partir de uma lista"""
        self.keywords = ', '.join(keywords_list)
    
    def to_dict(self):
        """Converte o artigo para dicionário"""
        return {
            'id': self.id,
            'title': self.title,
            'abstract': self.abstract,
            'content': self.content,
            'keywords': self.get_keywords_list(),
            'file_path': self.file_path,
            'status': self.status,
            'views_count': self.views_count,
            'downloads_count': self.downloads_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'author': self.author.to_dict() if self.author else None,
            'category': self.category.to_dict() if self.category else None
        }
    
    def __repr__(self):
        return f'<Article {self.title}>'

# Modelo adicional para comentários (opcional)
class Comment(db.Model):
    """Modelo para comentários nos artigos"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chaves estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    
    # Relacionamentos
    user = db.relationship('User', backref='comments')
    article = db.relationship('Article', backref='comments')
    
    def to_dict(self):
        """Converte o comentário para dicionário"""
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': self.user.to_dict() if self.user else None
        }
    
    def __repr__(self):
        return f'<Comment {self.id}>'
