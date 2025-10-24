import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("Testando importacoes...")
    
    try:
        from flask import Flask
        print("OK - Flask importado com sucesso")
    except ImportError as e:
        print(f"ERRO - Erro ao importar Flask: {e}")
        return False
    
    try:
        from flask_sqlalchemy import SQLAlchemy
        print("OK - Flask-SQLAlchemy importado com sucesso")
    except ImportError as e:
        print(f"ERRO - Erro ao importar Flask-SQLAlchemy: {e}")
        return False
    
    try:
        from werkzeug.security import generate_password_hash
        print("OK - Werkzeug importado com sucesso")
    except ImportError as e:
        print(f"ERRO - Erro ao importar Werkzeug: {e}")
        return False
    
    return True

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    print("\nTestando conexao com banco de dados...")
    
    try:
        from app import app, db
        with app.app_context():
            # Com SQLite, o teste de conexão é efetivamente a capacidade de interagir com o db.
            db.engine.connect()
        print("OK - Conexão com o banco de dados (SQLite) bem-sucedida.")
        return True
    except Exception as e:
        print(f"ERRO - Erro ao conectar com o banco: {e}")
        print("Dica: Verifique a string de conexão em app.py.")
        return False

def test_app_creation():
    """Testa se a aplicação Flask pode ser criada"""
    print("\nTestando criacao da aplicacao Flask...")
    
    try:
        from app import app, db, create_tables
        print("OK - Aplicacao Flask criada com sucesso")
        
        # Testar criação das tabelas
        with app.app_context():
            try:
                create_tables()
                print("OK - Tabelas criadas/verificadas com sucesso")
                return True
            except Exception as e:
                print(f"ERRO - Erro ao criar tabelas: {e}")
                return False
                
    except Exception as e:
        print(f"ERRO - Erro ao criar aplicacao: {e}")
        return False

def main():
    """Função principal do teste"""
    print("Iniciando testes da aplicacao Blue Article...\n")
    
    tests = [
        ("Importacoes", test_imports),
        ("Conexao com Banco", test_database_connection),
        ("Criacao da Aplicacao", test_app_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Resultado dos Testes: {passed}/{total} passaram")
    
    if passed == total:
        print("Todos os testes passaram! A aplicacao esta pronta para uso.")
        print("\nPara executar a aplicacao:")
        print("   python app.py")
        print("\nAcesse: http://localhost:5000")
    else:
        print("Alguns testes falharam. Verifique os erros acima.")
        print("\nPara instalar dependencias:")
        print("   pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
