from models import db
from datetime import datetime

class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200))
    autor = db.Column(db.String(100))
    curso = db.Column(db.String(100))
    ano = db.Column(db.Integer)
    descricao = db.Column(db.Text)
    pdf_path = db.Column(db.String(200))
    capa_path = db.Column(db.String(200))
    downloads = db.Column(db.Integer, default=0)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
