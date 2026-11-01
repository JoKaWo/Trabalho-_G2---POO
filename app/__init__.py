import os

from flask import Flask

from config import Config
from .extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    os.makedirs(os.path.join(os.path.dirname(app.root_path), "instance"), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from .auth.routes import bp as auth_bp
    from .main.routes import bp as main_bp
    from .treino.routes import bp as treino_bp
    from .evolucao.routes import bp as evolucao_bp
    from .peso.routes import bp as peso_bp
    from .nutricao.routes import bp as nutricao_bp

    for bp in (auth_bp, main_bp, treino_bp, evolucao_bp, peso_bp, nutricao_bp):
        app.register_blueprint(bp)

    with app.app_context():
        from . import models  # noqa: F401
        from .seed import popular_catalogo

        db.create_all()
        popular_catalogo()

    return app
