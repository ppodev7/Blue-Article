from src.model.models import db, User, Article, Category, Comment
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from PIL import Image, ImageOps
import os

class UserController:
    """Controller para gerenciar usuários"""
    
    def get_user_by_id(self, user_id):
        """Busca usuário por ID"""
        return User.query.get(user_id)
    
    def get_user_by_email(self, email):
        """Busca usuário por email"""
        return User.query.filter_by(email=email).first()
    
    def create_user(self, name, email, password, admin_email=None):
        """Cria um novo usuário"""
        try:
            if not name or not email or not password:
                print("Erro: Campos obrigatórios não preenchidos")
                return False
            
            if len(password) < 6:
                print("Erro: Senha muito curta")
                return False
            
            existing_user = self.get_user_by_email(email)
            if existing_user:
                print(f"Erro: Email {email} já existe")
                return False
            
            user = User(name=name, email=email)
            user.set_password(password)

            if email == admin_email:
                user.role = 'admin'
            
            db.session.add(user)
            db.session.commit()
            print(f"Usuário {name} criado com sucesso")
            return user
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar usuário: {e}")
            return False
    
    def update_user(self, user_id, name=None, email=None, password=None):
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
    
    def set_user_role(self, user_id, role):
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            user.role = role
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao definir papel: {e}")
            return False

    def get_all_users(self):
        return User.query.all()
    
    def get_users_count(self):
        return User.query.count()


class ArticleController:
    """Controller para gerenciar artigos"""

    def _resize_cover_image(self, image_path, output_size=(1200, 675)):
        """Redimensiona e comprime capa para tamanho padrão fixo."""
        try:
            if os.path.exists(image_path):
                image = Image.open(image_path)

                image = image.convert("RGB")  # corrige PNG com transparência

                # Ajusta a imagem ao tamanho exato sem distorcer
                image = ImageOps.fit(image, output_size, Image.LANCZOS)

                # Salva com compressão otimizada
                image.save(image_path, format="JPEG", quality=75, optimize=True)

                return True
            return False
        except Exception as e:
            print(f"Erro ao redimensionar capa: {e}")
            return False

    def get_article_by_id(self, article_id):
        return Article.query.get(article_id)
    
    def get_all_articles(self, limit=None, offset=0):
        query = Article.query.filter_by(status='published').order_by(Article.created_at.desc())
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query.all()
    
    def get_user_articles(self, user_id):
        return Article.query.filter_by(user_id=user_id).order_by(Article.created_at.desc()).all()
    
    def search_articles(self, query_text):
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
    
    def get_articles_by_category(self, category_id, exclude_id=None, limit=None):
        query = Article.query.filter_by(category_id=category_id, status='published')
        if exclude_id:
            query = query.filter(Article.id != exclude_id)
        query = query.order_by(Article.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def create_article(self, title, abstract, content, category_id, keywords, user_id, file_path=None, cover_path=None):
        try:
            if cover_path:
                self._resize_cover_image(cover_path)

            article = Article(
                title=title,
                abstract=abstract,
                content=content,
                keywords=keywords,
                category_id=category_id,
                user_id=user_id,
                file_path=file_path,
                cover_path=cover_path
            )
            
            db.session.add(article)
            db.session.commit()
            return article
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar artigo: {e}")
            return False
    
    def update_article(self, article_id, title=None, abstract=None, content=None, 
                      category_id=None, keywords=None, status=None, file_path=None, cover_path=None):
        try:
            article = self.get_article_by_id(article_id)
            if not article:
                return False
            
            if cover_path:
                self._resize_cover_image(cover_path)
            
            if title: article.title = title
            if abstract: article.abstract = abstract
            if content: article.content = content
            if category_id: article.category_id = category_id
            if keywords: article.keywords = keywords
            if status: article.status = status
            if file_path: article.file_path = file_path
            if cover_path: article.cover_path = cover_path
            
            article.updated_at = datetime.utcnow()
            db.session.commit()
            return article
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar artigo: {e}")
            return False
    
    def delete_article(self, article_id):
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
        return Article.query.count()
    
    def get_published_articles_count(self):
        return Article.query.filter_by(status='published').count()


class AuthController:
    def login(self, email, password):
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None
    
    def register(self, name, email, password, admin_email=None):
        return UserController().create_user(name, email, password, admin_email)
    
    def change_password(self, user_id, old_password, new_password):
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
    def get_category_by_id(self, category_id):
        return Category.query.get(category_id)
    
    def get_all_categories(self):
        return Category.query.all()
    
    def create_category(self, name, description=None):
        try:
            if Category.query.filter_by(name=name).first():
                return False
            category = Category(name=name, description=description)
            db.session.add(category)
            db.session.commit()
            return category
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar categoria: {e}")
            return False
    
    def update_category(self, category_id, name=None, description=None):
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                return False
            if name: category.name = name
            if description: category.description = description
            db.session.commit()
            return category
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar categoria: {e}")
            return False
    
    def delete_category(self, category_id):
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                return False
            if Article.query.filter_by(category_id=category_id).count() > 0:
                return False
            db.session.delete(category)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao deletar categoria: {e}")
            return False


class CommentController:
    def get_comment_by_id(self, comment_id):
        return Comment.query.get(comment_id)
    
    def get_article_comments(self, article_id):
        return Comment.query.filter_by(article_id=article_id).order_by(Comment.created_at.desc()).all()
    
    def create_comment(self, content, user_id, article_id):
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
