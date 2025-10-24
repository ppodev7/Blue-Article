import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def update_database_schema():
    """Atualiza a estrutura do banco de dados"""
    print("Atualizando estrutura do banco de dados...")
    
    try:
        from app import app, db # Importar apenas 'app' e 'db'
        from src.controller.user_controller import UserController
        
        with app.app_context():
            # Dropar e recriar todas as tabelas
            print("Droppando tabelas existentes...")
            db.drop_all()
            
            print("Criando novas tabelas...")
            db.create_all()
            
            # Recriar categorias padrão
            from src.model.models import Category
            
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
            print("Categorias padrão recriadas!")
            
            # Criar usuário administrador padrão se não existir
            admin_email_config = app.config['ADMIN_EMAIL'] # Acessar ADMIN_EMAIL via app.config
            from src.model.models import User
            user_controller = UserController()
            
            admin_user = User.query.filter_by(email=admin_email_config).first()
            if not admin_user:
                print(f"Criando usuário administrador: {admin_email_config} com senha '123456'...")
                user_controller.create_user(
                    name="Administrador", 
                    email=admin_email_config, 
                    password="123456", 
                    admin_email=admin_email_config)
            print("Estrutura do banco atualizada com sucesso!")
            
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_database_schema()
