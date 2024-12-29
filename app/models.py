from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from flask import current_app
import pytz

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    entries = db.relationship('Entry', backref='author', lazy=True)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title_id = db.Column(db.Integer, db.ForeignKey('title.id'), nullable=False)
    likes = db.relationship('User', secondary='entry_likes', backref=db.backref('liked_entries', lazy='dynamic'))

    @property
    def local_date_posted(self):
        """Entry'nin oluşturulma zamanını GMT+3'e çevirir."""
        utc_time = pytz.utc.localize(self.date_posted)
        local_time = utc_time.astimezone(current_app.config['TIMEZONE'])
        return local_time

class Title(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    entries = db.relationship('Entry', backref='title_obj', lazy=True)

# Entry-Like ilişki tablosu
entry_likes = db.Table('entry_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('entry_id', db.Integer, db.ForeignKey('entry.id'), primary_key=True)
) 