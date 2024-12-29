import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    
    # PostgreSQL bağlantısı
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://db_450mt_forum_user:ys3L3IHbALZHlSypA16tKns9nysdk6XK@dpg-ctohogtsvqrc73b8htkg-a.frankfurt-postgres.render.com/db_450mt_forum')
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7) 