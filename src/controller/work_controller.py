from flask import Blueprint, request, jsonify, send_from_directory
from models.work import Work
from models.history import DownloadHistory
from models import db
import os

work_bp = Blueprint('works', __name__, url_prefix='/works')

UPLOAD_FOLDER = os.path.join(os.getcwd(),'uploads')

@work_bp.route('/add', methods=['POST'])
def add_work():
    titulo = request.form.get('titulo')
    autor = request.form.get('autor')
    curso = request.form.get('curso')
    ano = request.form.get('ano')
    descricao = request.form.get('descricao')

    pdf = request.files.get('pdf')
    capa = request.files.get('capa')

    pdf_path = os.path.join(UPLOAD_FOLDER,'pdfs', pdf.filename)
    capa_path = os.path.join(UPLOAD_FOLDER,'capas', capa.filename)

    pdf.save(pdf_path)
    capa.save(capa_path)

    work = Work(titulo=titulo, autor=autor, curso=curso, ano=ano,
                descricao=descricao, pdf_path=pdf_path, capa_path=capa_path)
    db.session.add(work)
    db.session.commit()
    return jsonify({'message':'Trabalho adicionado!'})

@work_bp.route('/list', methods=['GET'])
def list_works():
    works = Work.query.all()
    return jsonify([{'id':w.id,'titulo':w.titulo,'autor':w.autor,'curso':w.curso,'ano':w.ano,'downloads':w.downloads} for w in works])

@work_bp.route('/download/<int:work_id>', methods=['GET'])
def download(work_id):
    work = Work.query.get(work_id)
    if not work:
        return jsonify({'error':'Trabalho não encontrado'}),404
    work.downloads += 1
    db.session.add(DownloadHistory(user_id=1, work_id=work.id))
    db.session.commit()
    return send_from_directory(os.path.dirname(work.pdf_path), os.path.basename(work.pdf_path), as_attachment=True)
