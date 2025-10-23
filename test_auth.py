#!/usr/bin/env python3
"""
Script para testar o sistema de registro e login
"""

import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_user_registration_and_login():
    """Testa o registro e login de usuário"""
    print("Testando sistema de registro e login...")
    
    try:
        from app import app, db, User, auth_controller
        
        with app.app_context():
            # Limpar usuários de teste anteriores
            test_user = User.query.filter_by(email='teste@exemplo.com').first()
            if test_user:
                db.session.delete(test_user)
                db.session.commit()
                print("Usuário de teste anterior removido")
            
            # Teste 1: Registrar usuário
            print("\n1. Testando registro de usuário...")
            user = auth_controller.register('Usuario Teste', 'teste@exemplo.com', '123456')
            
            if user:
                print(f"OK - Usuario registrado com sucesso: {user.name} ({user.email})")
                print(f"   ID: {user.id}")
                print(f"   Password hash: {user.password_hash[:20]}...")
            else:
                print("ERRO - Falha no registro do usuario")
                return False
            
            # Teste 2: Verificar se usuário existe no banco
            print("\n2. Verificando se usuário existe no banco...")
            db_user = User.query.filter_by(email='teste@exemplo.com').first()
            if db_user:
                print(f"OK - Usuario encontrado no banco: {db_user.name}")
                print(f"   Password hash: {db_user.password_hash[:20]}...")
            else:
                print("ERRO - Usuario nao encontrado no banco")
                return False
            
            # Teste 3: Testar login
            print("\n3. Testando login...")
            login_user = auth_controller.login('teste@exemplo.com', '123456')
            if login_user:
                print(f"OK - Login realizado com sucesso: {login_user.name}")
            else:
                print("ERRO - Falha no login")
                
                # Debug: verificar senha manualmente
                print("\n4. Debug - Verificando senha manualmente...")
                if db_user.check_password('123456'):
                    print("OK - Senha verificada manualmente - OK")
                else:
                    print("ERRO - Senha verificada manualmente - FALHOU")
                
                return False
            
            # Teste 4: Testar senha incorreta
            print("\n5. Testando senha incorreta...")
            wrong_login = auth_controller.login('teste@exemplo.com', 'senhaerrada')
            if not wrong_login:
                print("OK - Senha incorreta rejeitada corretamente")
            else:
                print("ERRO - Senha incorreta foi aceita (problema!)")
                return False
            
            # Limpar usuário de teste
            db.session.delete(user)
            db.session.commit()
            print("\nOK - Usuario de teste removido")
            
            return True
            
    except Exception as e:
        print(f"ERRO - Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_user_registration_and_login()
    if success:
        print("\nTodos os testes passaram!")
    else:
        print("\nAlguns testes falharam!")
    sys.exit(0 if success else 1)
