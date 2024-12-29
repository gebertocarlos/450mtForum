from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import pytz

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Lütfen giriş yapın.'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Timezone ayarı
    app.config['TIMEZONE'] = pytz.timezone('Europe/Istanbul')
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)
    
    from app.main.routes import main
    from app.auth.routes import auth
    from app.errors.handlers import errors
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(errors)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001) 