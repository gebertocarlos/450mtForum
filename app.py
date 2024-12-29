from flask import Flask
from flask_migrate import Migrate
from config import Config
from extensions import db, bcrypt, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    from main import main
    from auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001) 