# 📚 Blue Article - Biblioteca Digital de TCCs e Artigos Acadêmicos

Uma aplicação web Flask para gerenciar e compartilhar trabalhos de conclusão de curso e artigos acadêmicos.

## 🚀 Características

- **Interface moderna** com Bootstrap 5
- **Sistema de autenticação** completo
- **Gerenciamento de artigos** (CRUD)
- **Sistema de categorias** para organização
- **Busca avançada** por título, resumo e palavras-chave
- **Dashboard personalizado** para usuários
- **Contadores de visualizações** e downloads
- **Design responsivo** para todos os dispositivos

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3 + Flask
- **Banco de Dados**: SQLite
- **ORM**: SQLAlchemy
- **Frontend**: HTML5 + CSS3 + JavaScript + Bootstrap 5
- **Ícones**: Font Awesome 6

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Git

## 🔧 Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd blue-article/Blue-Article
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
```

### 3. Ative o ambiente virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instale as dependências
```bash
pip install -r requirements.txt
```

### 5. Configure o banco de dados

1. Inicie o XAMPP e ative o MySQL
2. Acesse o phpMyAdmin (http://localhost/phpmyadmin)
3. Crie um banco de dados chamado `blue_article`
4. A aplicação criará as tabelas automaticamente na primeira execução

### 6. Execute a aplicação
```bash
python app.py
```

A aplicação estará disponível em: http://localhost:5000

## 📁 Estrutura do Projeto

```
Blue-Article/
├── app.py                 # Arquivo principal da aplicação
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── src/
│   ├── model/
│   │   └── models.py     # Modelos SQLAlchemy
│   ├── controller/
│   │   ├── article_controller.py
│   │   ├── user_controller.py
│   │   └── auth_controller.py
│   └── view/             # (não utilizado - templates estão na raiz)
├── templates/            # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_article.html
│   ├── edit_article.html
│   ├── article_detail.html
│   └── search.html
└── static/              # Arquivos estáticos
    ├── css/
    │   └── style.css
    ├── js/
    │   └── main.js
    └── img/
```

## 🎯 Funcionalidades

### Para Visitantes
- Visualizar artigos publicados
- Buscar artigos por palavras-chave
- Filtrar por categorias
- Cadastrar-se no sistema

### Para Usuários Cadastrados
- Fazer login/logout
- Adicionar novos artigos
- Editar artigos próprios
- Deletar artigos próprios
- Visualizar dashboard com estatísticas
- Gerenciar perfil

### Para Administradores
- Gerenciar todas as categorias
- Visualizar estatísticas gerais
- Moderar conteúdo

## 🔐 Configuração de Segurança

A aplicação usa:
- **Senhas criptografadas** com Werkzeug
- **Sessões seguras** com chave secreta
- **Validação de formulários** no frontend e backend
- **Proteção CSRF** (recomendado implementar)

## 📊 Banco de Dados

### Tabelas Principais

- **users**: Usuários do sistema
- **categories**: Categorias de artigos
- **articles**: Artigos acadêmicos
- **comments**: Comentários (opcional)

### Relacionamentos

- Um usuário pode ter vários artigos
- Um artigo pertence a uma categoria
- Um artigo pode ter vários comentários

## 🚀 Deploy

### Desenvolvimento
```bash
python app.py
```

### Produção
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🐛 Solução de Problemas

### Erro de conexão com MySQL
- Verifique se o XAMPP está rodando
- Confirme se o banco `blue_article` existe
- Verifique as credenciais no `app.py`

### Erro de módulos Python
- Ative o ambiente virtual
- Execute `pip install -r requirements.txt`

### Erro de templates
- Verifique se a pasta `templates` existe
- Confirme se os arquivos HTML estão corretos

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para suporte, entre em contato através de:
- Email: [seu-email@exemplo.com]
- Issues do GitHub: [link-para-issues]

## 🎉 Agradecimentos

- Flask Community
- Bootstrap Team
- Font Awesome
- SQLAlchemy Team
