from flask import Flask
from config import Config
from extensions import db, bcrypt, login_manager
from auth import auth
from main import main

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Uzantıları başlat
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Blueprint'leri kaydet
    app.register_blueprint(auth)
    app.register_blueprint(main)

    with app.app_context():
        db.drop_all()  # Mevcut tabloları sil
        db.create_all()  # Tabloları yeniden oluştur

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001) 