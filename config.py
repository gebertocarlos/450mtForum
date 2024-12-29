import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    
    # PostgreSQL bağlantısı
    base_uri = os.environ.get('DATABASE_URL', 'postgresql://db_450mt_forum_user:ys3L3IHbALZHlSypA16tKns9nysdk6XK@dpg-ctohogtsvqrc73b8htkg-a.frankfurt-postgres.render.com/db_450mt_forum')
    if base_uri.startswith("postgres://"):
        base_uri = base_uri.replace("postgres://", "postgresql://", 1)
    
    # SSL parametrelerini ekle
    SQLALCHEMY_DATABASE_URI = f"{base_uri}?sslmode=require"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7) 