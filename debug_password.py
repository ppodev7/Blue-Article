#!/usr/bin/env python3
"""
Script para debug detalhado do problema de senha
"""

import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_password_issue():
    """Debug detalhado do problema de senha"""
    print("Debug detalhado do problema de senha...")
    
    try:
        from app import app, db, User, auth_controller
        from werkzeug.security import generate_password_hash, check_password_hash
        
        with app.app_context():
            # Limpar usuários de teste anteriores
            test_user = User.query.filter_by(email='debug@exemplo.com').first()
            if test_user:
                db.session.delete(test_user)
                db.session.commit()
            
            print("\n1. Testando hash de senha diretamente...")
            password = '123456'
            hash1 = generate_password_hash(password)
            hash2 = generate_password_hash(password)
            
            print(f"Senha original: {password}")
            print(f"Hash 1: {hash1}")
            print(f"Hash 2: {hash2}")
            print(f"Hash 1 == Hash 2: {hash1 == hash2}")
            print(f"check_password_hash(hash1, password): {check_password_hash(hash1, password)}")
            print(f"check_password_hash(hash2, password): {check_password_hash(hash2, password)}")
            
            print("\n2. Testando criação de usuário manual...")
            user = User(
                name='Debug User',
                email='debug@exemplo.com'
            )
            user.set_password(password)
            
            print(f"Senha definida: {password}")
            print(f"Hash armazenado: {user.password_hash}")
            print(f"check_password('123456'): {user.check_password('123456')}")
            print(f"check_password('1234567'): {user.check_password('1234567')}")
            
            db.session.add(user)
            db.session.commit()
            
            print("\n3. Recuperando usuário do banco...")
            db_user = User.query.filter_by(email='debug@exemplo.com').first()
            if db_user:
                print(f"Usuário recuperado: {db_user.name}")
                print(f"Hash no banco: {db_user.password_hash}")
                print(f"check_password('123456'): {db_user.check_password('123456')}")
                print(f"check_password('1234567'): {db_user.check_password('1234567')}")
                
                # Teste com hash direto
                print(f"check_password_hash direto: {check_password_hash(db_user.password_hash, '123456')}")
            else:
                print("ERRO - Usuário não encontrado no banco")
            
            # Limpar
            db.session.delete(user)
            db.session.commit()
            
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_password_issue()
