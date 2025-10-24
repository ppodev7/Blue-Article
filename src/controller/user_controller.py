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
    
    def create_user(self, name, email, password, admin_email=None):
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
                email=email,
                role='admin' if email == admin_email else 'user'
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            if user.role == 'admin':
                print(f"Usuário Administrador {name} criado com sucesso")
            else:
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
