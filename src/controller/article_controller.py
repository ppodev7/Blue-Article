from src.model.models import db, User, Article, Category, Comment
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class UserController:
    """Controller para gerenciar usuários"""
    
    def get_user_by_id(self, user_id):
        """Busca usuário por ID"""
        return User.query.get(user_id)
    
    def get_user_by_email(self, email):
        """Busca usuário por email"""
        return User.query.filter_by(email=email).first()
    
    def create_user(self, name, email, password):
        """Cria um novo usuário"""
        try:
            # Validações básicas
            if not name or not email or not password:
                print("Erro: Campos obrigatórios não preenchidos")
                return False
            
            if len(password) < 6:
                print("Erro: Senha muito curta")
                return False
            
            # Verificar se o email já existe
            existing_user = self.get_user_by_email(email)
            if existing_user:
                print(f"Erro: Email {email} já existe")
                return False
            
            user = User(
                name=name,
                email=email
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            print(f"Usuário {name} criado com sucesso")
            return user
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar usuário: {e}")
            return False
    
    def update_user(self, user_id, name=None, email=None, password=None):
        """Atualiza dados do usuário"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            if name:
                user.name = name
            if email:
                user.email = email
            if password:
                user.set_password(password)
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar usuário: {e}")
            return False
    
    def delete_user(self, user_id):
        """Deleta usuário"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao deletar usuário: {e}")
            return False
    
    def get_all_users(self):
        """Retorna todos os usuários"""
        return User.query.all()
    
    def get_users_count(self):
        """Retorna quantidade de usuários"""
        return User.query.count()

class ArticleController:
    """Controller para gerenciar artigos"""
    
    def get_article_by_id(self, article_id):
        """Busca artigo por ID"""
        return Article.query.get(article_id)
    
    def get_all_articles(self, limit=None, offset=0):
        """Retorna todos os artigos publicados"""
        query = Article.query.filter_by(status='published').order_by(Article.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        return query.all()
    
    def get_user_articles(self, user_id):
        """Retorna artigos de um usuário específico"""
        return Article.query.filter_by(user_id=user_id).order_by(Article.created_at.desc()).all()
    
    def search_articles(self, query_text):
        """Busca artigos por título, resumo ou palavras-chave"""
        if not query_text:
            return []
        
        search_term = f"%{query_text}%"
        return Article.query.filter(
            Article.status == 'published',
            db.or_(
                Article.title.like(search_term),
                Article.abstract.like(search_term),
                Article.keywords.like(search_term)
            )
        ).order_by(Article.created_at.desc()).all()
    
    def get_articles_by_category(self, category_id):
        """Retorna artigos de uma categoria específica"""
        return Article.query.filter_by(
            category_id=category_id,
            status='published'
        ).order_by(Article.created_at.desc()).all()
    
    def create_article(self, title, abstract, content, category_id, keywords, user_id, file_path=None):
        """Cria um novo artigo"""
        try:
            article = Article(
                title=title,
                abstract=abstract,
                content=content,
                keywords=keywords,
                category_id=category_id,
                user_id=user_id,
                file_path=file_path
            )
            
            db.session.add(article)
            db.session.commit()
            return article
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar artigo: {e}")
            return False
    
    def update_article(self, article_id, title=None, abstract=None, content=None, 
                      category_id=None, keywords=None, status=None, file_path=None):
        """Atualiza um artigo"""
        try:
            article = self.get_article_by_id(article_id)
            if not article:
                return False
            
            if title:
                article.title = title
            if abstract:
                article.abstract = abstract
            if content:
                article.content = content
            if category_id:
                article.category_id = category_id
            if keywords:
                article.keywords = keywords
            if status:
                article.status = status
            if file_path:
                article.file_path = file_path
            
            article.updated_at = datetime.utcnow()
            db.session.commit()
            return article
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar artigo: {e}")
            return False
    
    def delete_article(self, article_id):
        """Deleta um artigo"""
        try:
            article = self.get_article_by_id(article_id)
            if not article:
                return False
            
            db.session.delete(article)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao deletar artigo: {e}")
            return False
    
    def increment_views(self, article_id):
        """Incrementa contador de visualizações"""
        try:
            article = self.get_article_by_id(article_id)
            if article:
                article.increment_view()
                return True
            return False
        except Exception as e:
            print(f"Erro ao incrementar visualizações: {e}")
            return False
    
    def increment_downloads(self, article_id):
        """Incrementa contador de downloads"""
        try:
            article = self.get_article_by_id(article_id)
            if article:
                article.increment_download()
                return True
            return False
        except Exception as e:
            print(f"Erro ao incrementar downloads: {e}")
            return False
    
    def get_articles_count(self):
        """Retorna quantidade de artigos"""
        return Article.query.count()
    
    def get_published_articles_count(self):
        """Retorna quantidade de artigos publicados"""
        return Article.query.filter_by(status='published').count()

class AuthController:
    """Controller para autenticação"""
    
    def login(self, email, password):
        """Realiza login do usuário"""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None
    
    def register(self, name, email, password):
        """Registra novo usuário"""
        user_controller = UserController()
        return user_controller.create_user(name, email, password)
    
    def change_password(self, user_id, old_password, new_password):
        """Altera senha do usuário"""
        try:
            user = User.query.get(user_id)
            if not user or not user.check_password(old_password):
                return False
            
            user.set_password(new_password)
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao alterar senha: {e}")
            return False

class CategoryController:
    """Controller para gerenciar categorias"""
    
    def get_category_by_id(self, category_id):
        """Busca categoria por ID"""
        return Category.query.get(category_id)
    
    def get_all_categories(self):
        """Retorna todas as categorias"""
        return Category.query.all()
    
    def create_category(self, name, description=None):
        """Cria nova categoria"""
        try:
            # Verificar se já existe categoria com esse nome
            if Category.query.filter_by(name=name).first():
                return False
            
            category = Category(
                name=name,
                description=description
            )
            
            db.session.add(category)
            db.session.commit()
            return category
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar categoria: {e}")
            return False
    
    def update_category(self, category_id, name=None, description=None):
        """Atualiza categoria"""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                return False
            
            if name:
                category.name = name
            if description:
                category.description = description
            
            db.session.commit()
            return category
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar categoria: {e}")
            return False
    
    def delete_category(self, category_id):
        """Deleta categoria"""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                return False
            
            # Verificar se há artigos nesta categoria
            if Article.query.filter_by(category_id=category_id).count() > 0:
                return False  # Não pode deletar categoria com artigos
            
            db.session.delete(category)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao deletar categoria: {e}")
            return False

class CommentController:
    """Controller para gerenciar comentários"""
    
    def get_comment_by_id(self, comment_id):
        """Busca comentário por ID"""
        return Comment.query.get(comment_id)
    
    def get_article_comments(self, article_id):
        """Retorna comentários de um artigo"""
        return Comment.query.filter_by(article_id=article_id).order_by(Comment.created_at.desc()).all()
    
    def create_comment(self, content, user_id, article_id):
        """Cria novo comentário"""
        try:
            comment = Comment(
                content=content,
                user_id=user_id,
                article_id=article_id
            )
            
            db.session.add(comment)
            db.session.commit()
            return comment
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar comentário: {e}")
            return False
    
    def delete_comment(self, comment_id):
        """Deleta comentário"""
        try:
            comment = self.get_comment_by_id(comment_id)
            if not comment:
                return False
            
            db.session.delete(comment)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao deletar comentário: {e}")
            return False
