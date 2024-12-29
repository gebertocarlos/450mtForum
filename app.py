from flask import Flask
from config import Config
from extensions import db, bcrypt, login_manager
from auth import auth
from main import main
import logging

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Loglama ayarları
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Uzantıları başlat
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Blueprint'leri kaydet
    app.register_blueprint(auth)
    app.register_blueprint(main)

    with app.app_context():
        try:
            logger.info("Veritabanı bağlantısı kuruluyor...")
            logger.info(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            db.create_all()
            logger.info("Veritabanı başarıyla oluşturuldu!")
        except Exception as e:
            logger.error(f"Veritabanı oluşturma hatası: {str(e)}")
            raise

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001) 