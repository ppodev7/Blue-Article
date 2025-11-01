from flask import Blueprint, jsonify
from models.work import Work

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/stats', methods=['GET'])
def stats():
    total_works = Work.query.count()
    total_downloads = sum(w.downloads for w in Work.query.all())
    autores = [w.autor for w in Work.query.all()]
    autores_pop = sorted(set(autores), key=lambda x: autores.count(x), reverse=True)[:3]
    return jsonify({
        'total_trabalhos': total_works,
        'total_downloads': total_downloads,
        'autores_populares': autores_pop
    })
