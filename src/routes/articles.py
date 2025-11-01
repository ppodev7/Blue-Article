from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
import os
import io # ADICIONADO VICTOR
import csv # ADICIONADO VICTOR
from flask import Response # ADICIONADO VICTOR
import unicodedata

from src.controller.article_controller import ArticleController
from src.model.models import Category

def remover_acentos(texto):
    """Remove acentos de uma string"""
    if not texto:
        return texto
    nfkd = unicodedata.normalize('NFKD', texto)
    return ''.join([char for char in nfkd if not unicodedata.combining(char)])

# Cria o Blueprint para as rotas de artigos
articles_bp = Blueprint('articles', __name__, template_folder='../../templates')

# Inicializa o controller
article_controller = ArticleController()

@articles_bp.route('/article/<int:article_id>')
def view_article(article_id):
    """Visualizar artigo específico"""
    article = article_controller.get_article_by_id(article_id)
    if not article:
        flash('Artigo não encontrado!', 'error')
        return redirect(url_for('index'))
    
    # Lógica para artigos relacionados (mesma categoria, excluindo o atual)
    related_articles = ArticleController().get_articles_by_category(
        article.category_id, 
        exclude_id=article.id,
        limit=5
    )

    return render_template('article_detail.html', article=article, related_articles=related_articles)

@articles_bp.route('/add_article', methods=['GET', 'POST'])
def add_article():
    """Adicionar novo artigo"""
    if 'user_id' not in session:
        flash('Você precisa fazer login para adicionar artigos!', 'error')
        return redirect(url_for('auth.login'))
    
    app_config = request.environ.get('app.config', {})
    upload_folder = app_config.get('UPLOAD_FOLDER')

    if request.method == 'POST':
        title = request.form['title']
        abstract = request.form['abstract']
        content = request.form['content']
        category_id = request.form['category_id']
        keywords = request.form['keywords']
        pdf_file = request.files.get('file')
        cover_file = request.files.get('cover')

        # Lógica de salvamento do PDF
        pdf_path = None
        if pdf_file and pdf_file.filename != '':
            filename = secure_filename(pdf_file.filename)
            pdf_path = os.path.join('pdfs', filename) # Caminho relativo
            os.makedirs(os.path.join(upload_folder, 'pdfs'), exist_ok=True)
            pdf_file.save(os.path.join(upload_folder, pdf_path))

        # Lógica de salvamento da Imagem de Capa
        cover_path = None
        if cover_file and cover_file.filename != '':
            filename = secure_filename(cover_file.filename)
            cover_path = os.path.join('covers', filename) # Caminho relativo
            os.makedirs(os.path.join(upload_folder, 'covers'), exist_ok=True)
            cover_file.save(os.path.join(upload_folder, cover_path))
        
        if article_controller.create_article(
            title=title, abstract=abstract, content=content, category_id=category_id,
            keywords=keywords, user_id=session['user_id'], file_path=pdf_path, cover_path=cover_path
        ):
            flash('Artigo adicionado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Erro ao adicionar artigo!', 'error')
    
    categories = Category.query.all()
    return render_template('add_article.html', categories=categories)

@articles_bp.route('/edit_article/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    """Editar artigo"""
    if 'user_id' not in session:
        flash('Você precisa fazer login para editar artigos!', 'error')
        return redirect(url_for('auth.login'))
    
    article = article_controller.get_article_by_id(article_id)
    if not article or (article.user_id != session['user_id'] and session.get('user_role') != 'admin'):
        flash('Artigo não encontrado ou você não tem permissão para editá-lo!', 'error')
        return redirect(url_for('dashboard'))

    # Carrega as categorias para serem usadas no GET e no POST (em caso de erro)
    categories = Category.query.all()
    
    app_config = request.environ.get('app.config', {})
    upload_folder = app_config.get('UPLOAD_FOLDER')

    if request.method == 'POST':
        title = request.form['title']
        abstract = request.form['abstract']
        content = request.form['content']
        category_id = request.form['category_id']
        keywords = request.form['keywords']
        pdf_file = request.files.get('file')
        cover_file = request.files.get('cover')

        new_pdf_path = article.file_path
        if pdf_file and pdf_file.filename != '':
            if article.file_path and os.path.exists(os.path.join(upload_folder, article.file_path)):
                os.remove(os.path.join(upload_folder, article.file_path))
            filename = secure_filename(pdf_file.filename)
            new_pdf_path = os.path.join('pdfs', filename)
            os.makedirs(os.path.join(upload_folder, 'pdfs'), exist_ok=True)
            pdf_file.save(os.path.join(upload_folder, new_pdf_path))
        
        new_cover_path = article.cover_path
        if cover_file and cover_file.filename != '':
            if article.cover_path and os.path.exists(os.path.join(upload_folder, article.cover_path)):
                os.remove(os.path.join(upload_folder, article.cover_path))
            filename = secure_filename(cover_file.filename)
            new_cover_path = os.path.join('covers', filename)
            os.makedirs(os.path.join(upload_folder, 'covers'), exist_ok=True)
            cover_file.save(os.path.join(upload_folder, new_cover_path))

        if article_controller.update_article(
            article_id=article_id, title=title, abstract=abstract, content=content,
            category_id=category_id, keywords=keywords, file_path=new_pdf_path, cover_path=new_cover_path
        ):
            flash('Artigo atualizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Erro ao atualizar artigo!', 'error') # A página será renderizada novamente com os dados do artigo
    
    return render_template('edit_article.html', article=article, categories=categories)

@articles_bp.route('/delete_article/<int:article_id>')
def delete_article(article_id):
    """Deletar artigo"""
    if 'user_id' not in session:
        flash('Você precisa fazer login para deletar artigos!', 'error')
        return redirect(url_for('auth.login'))
    
    article = article_controller.get_article_by_id(article_id)
    if not article or (article.user_id != session['user_id'] and session.get('user_role') != 'admin'):
        flash('Artigo não encontrado ou você não tem permissão para deletá-lo!', 'error')
        return redirect(url_for('dashboard'))
    
    if article_controller.delete_article(article_id):
        flash('Artigo deletado com sucesso!', 'success')
    else:
        flash('Erro ao deletar artigo!', 'error')
    
    return redirect(url_for('dashboard'))

@articles_bp.route('/download_article/<int:article_id>')
def download_article(article_id):
    """Fornece o download do PDF de um artigo"""
    if 'user_id' not in session:
        flash('Você precisa estar logado para baixar artigos.', 'warning')
        return redirect(url_for('auth.login'))

    article = article_controller.get_article_by_id(article_id)
    if not article or not article.file_path:
        flash('Arquivo não encontrado ou indisponível.', 'error')
        return redirect(url_for('articles.view_article', article_id=article_id))

    app_config = request.environ.get('app.config', {})
    upload_folder = app_config.get('UPLOAD_FOLDER')
    directory = os.path.join(upload_folder, os.path.dirname(article.file_path))
    filename = os.path.basename(article.file_path)

    if not os.path.exists(os.path.join(directory, filename)):
        flash('Arquivo físico não encontrado no servidor.', 'error')
        return redirect(url_for('articles.view_article', article_id=article_id))

    article.increment_download()
    return send_from_directory(directory, filename, as_attachment=True)

@articles_bp.route('/export_csv/<int:article_id>') # ADICIONADO VICTOR
def export_article_csv(article_id):
    """Exporta os metadados de um artigo específico para CSV"""
    if 'user_id' not in session:
        flash('Você precisa estar logado para exportar dados.', 'warning')
        return redirect(url_for('auth.login'))

    article = article_controller.get_article_by_id(article_id)
    if not article:
        flash('Artigo não encontrado!', 'error')
        return redirect(url_for('index')) # Ou dashboard

    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Campo', 'Valor'])
    writer.writerow([])
    
    writer.writerow(['INFORMACOES BASICAS', ''])
    writer.writerow(['ID do Artigo', article.id])
    writer.writerow(['Titulo', remover_acentos(article.title)])
    writer.writerow(['Status', article.status.capitalize()])
    writer.writerow([])
    
    writer.writerow(['AUTORIA', ''])
    writer.writerow(['Nome do Autor', remover_acentos(article.author.name) if article.author else 'N/A'])
    writer.writerow(['Email do Autor', article.author.email if article.author else 'N/A'])
    writer.writerow(['ID do Autor', article.user_id])
    writer.writerow([])
    
    writer.writerow(['CATEGORIA', ''])
    writer.writerow(['Nome da Categoria', remover_acentos(article.category.name) if article.category else 'N/A'])
    writer.writerow(['ID da Categoria', article.category_id])
    writer.writerow([])
    
    writer.writerow(['CONTEUDO', ''])
    writer.writerow(['Resumo', remover_acentos(article.abstract)])
    writer.writerow(['Palavras-chave', remover_acentos(article.keywords) if article.keywords else 'N/A'])
    writer.writerow([])
    
    writer.writerow(['ARQUIVOS', ''])
    writer.writerow(['PDF Disponivel', 'Sim' if article.file_path else 'Nao'])
    writer.writerow(['Caminho do PDF', article.file_path if article.file_path else 'N/A'])
    writer.writerow(['Imagem de Capa Disponivel', 'Sim' if article.cover_path else 'Nao'])
    writer.writerow(['Caminho da Capa', article.cover_path if article.cover_path else 'N/A'])
    writer.writerow([])
    
    writer.writerow(['ESTATISTICAS', ''])
    writer.writerow(['Visualizacoes', article.views_count])
    writer.writerow(['Downloads', article.downloads_count])
    writer.writerow([])
    
    writer.writerow(['DATAS', ''])
    writer.writerow(['Data de Criacao', article.created_at.strftime('%d/%m/%Y %H:%M:%S') if article.created_at else 'N/A'])
    writer.writerow(['Data de Atualizacao', article.updated_at.strftime('%d/%m/%Y %H:%M:%S') if article.updated_at else 'N/A'])

    # Prepara a resposta
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=metadados_artigo_{article.id}_{article.title[:20].replace(' ', '_')}.csv"}
    )