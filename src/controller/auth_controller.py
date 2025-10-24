from src.model.models import db, User, Article, Category, Comment
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .user_controller import UserController

class AuthController:
    """Controller para autenticação"""
    
    def login(self, email, password):
        """Realiza login do usuário"""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None
    
    def register(self, name, email, password, admin_email=None):
        """Registra novo usuário"""
        user_controller = UserController()
        return user_controller.create_user(name, email, password, admin_email=admin_email)
    
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
