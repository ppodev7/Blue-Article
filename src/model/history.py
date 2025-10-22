from models import db
from datetime import datetime

class DownloadHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    work_id = db.Column(db.Integer)
    data = db.Column(db.DateTime, default=datetime.utcnow)
