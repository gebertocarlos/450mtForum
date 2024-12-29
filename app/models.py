from datetime import datetime
from flask_login import UserMixin
from extensions import db, login_manager
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    entries = db.relationship('Entry', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Title(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, unique=True, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    entries = db.relationship('Entry', backref='title_obj', lazy=True)

    def __repr__(self):
        return f"Title('{self.title}')"

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title_id = db.Column(db.Integer, db.ForeignKey('title.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('entry.id'), nullable=True)
    likes = db.relationship('Like', backref='entry', lazy=True)
    replies = db.relationship('Entry', backref=db.backref('parent', remote_side=[id]),
                            lazy='dynamic')

    def __repr__(self):
        return f"Entry('{self.title_obj.title}', '{self.date_posted}')"

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'), nullable=False)
    date_liked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 