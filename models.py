from datetime import datetime, timedelta
from flask_login import UserMixin
from extensions import db, login_manager

def get_istanbul_time():
    return datetime.utcnow() + timedelta(hours=3)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False, default=get_istanbul_time)
    entries = db.relationship('Entry', backref='author', lazy=True, foreign_keys='Entry.user_id')
    likes = db.relationship('Like', backref='user', lazy=True)
    liked_entries = db.relationship('Entry', secondary='like', backref=db.backref('liked_by', lazy='dynamic'), overlaps="likes,user")

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=get_istanbul_time)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('entry.id'), nullable=True)
    
    replies = db.relationship('Entry', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    likes = db.relationship('User', secondary='like', backref=db.backref('liked_entries_rel', lazy='dynamic'), overlaps="liked_entries,liked_by")

    def __repr__(self):
        return f"Entry('{self.title}', '{self.date_posted}')"

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'), nullable=False)
    date_liked = db.Column(db.DateTime, nullable=False, default=get_istanbul_time) 