from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationship to scan history
    scans = db.relationship('ScanHistory', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ScanHistory(db.Model):
    __tablename__ = 'scan_history'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    tool = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    suggestion = db.Column(db.Text, nullable=False)
    raw_output = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key linking to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
