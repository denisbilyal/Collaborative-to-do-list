from importlib import import_module
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO

db = SQLAlchemy()
DB_NAME = 'database.db'

socketio = SocketIO()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    socketio.init_app(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    auth_module = import_module('website.routes.auth')
    home_module = import_module('website.routes.home')
    tables_module = import_module('website.routes.tables')
    requests_module = import_module('website.routes.requests')
    activity_module = import_module('website.routes.activity')
    settings_module = import_module('website.routes.settings')
    tags_module = import_module('website.routes.tags')
    tasks_module = import_module('website.routes.tasks')
    users_module = import_module('website.routes.users')
    app.register_blueprint(auth_module.auth, url_prefix='/')
    app.register_blueprint(home_module.home_bp, url_prefix='/')
    app.register_blueprint(tables_module.tables_bp, url_prefix='/')
    app.register_blueprint(requests_module.requests_bp, url_prefix='/')
    app.register_blueprint(activity_module.activity_bp, url_prefix='/')
    app.register_blueprint(settings_module.settings_bp, url_prefix='/')
    app.register_blueprint(tags_module.tags_bp, url_prefix='/')
    app.register_blueprint(tasks_module.tasks_bp, url_prefix='/')
    app.register_blueprint(users_module.users_bp, url_prefix='/')


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    models_module = import_module('website.models')

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user_by_id(id):
        return models_module.User.query.get(int(id))

    return app
