"""
Creates and configures the Flask application.

This function initializes the Flask app, sets up the database, configures authentication,
registers blueprints for different routes, and initializes the SocketIO extension. It also
configures the login manager and ensures that the database tables are created.

Steps Performed:
1. Initializes the Flask application with a secret key.
2. Configures the SQLite database URI.
3. Initializes the SQLAlchemy and SocketIO extensions.
4. Dynamically imports and registers route modules (blueprints) using `importlib`.
5. Sets up the Flask-Login manager for user authentication.
6. Imports the models module to ensure the database schema is available.
7. Creates all database tables within the app context.
8. Defines a user loader callback for Flask-Login to load users by their ID.

Returns:
    Flask: The fully configured Flask application instance.
"""
from importlib import import_module
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO

db: SQLAlchemy = SQLAlchemy()
DB_NAME = 'database.db'
socketio = SocketIO()


def create_app() -> Flask:
    """
    Creates and configures the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    socketio.init_app(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # Import and register blueprints dynamically
    auth_module = import_module('src.routes.auth')
    home_module = import_module('src.routes.home')
    tables_module = import_module('src.routes.tables')
    requests_module = import_module('src.routes.requests')
    activity_module = import_module('src.routes.activity')
    settings_module = import_module('src.routes.settings')
    tags_module = import_module('src.routes.tags')
    tasks_module = import_module('src.routes.tasks')
    users_module = import_module('src.routes.users')

    app.register_blueprint(auth_module.auth, url_prefix='/')
    app.register_blueprint(home_module.home_bp, url_prefix='/')
    app.register_blueprint(tables_module.tables_bp, url_prefix='/')
    app.register_blueprint(requests_module.requests_bp, url_prefix='/')
    app.register_blueprint(activity_module.activity_bp, url_prefix='/')
    app.register_blueprint(settings_module.settings_bp, url_prefix='/')
    app.register_blueprint(tags_module.tags_bp, url_prefix='/')
    app.register_blueprint(tasks_module.tasks_bp, url_prefix='/')
    app.register_blueprint(users_module.users_bp, url_prefix='/')

    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Import models and create database tables
    models_module = import_module('src.models')
    with app.app_context():
        db.create_all()

    # Define the user loader for Flask-Login
    @login_manager.user_loader
    def load_user_by_id(user_id):
        """
        Loads a user by their ID for Flask-Login.

        Args:
            user_id (int): The ID of the user to load.

        Returns:
            User: The User object corresponding to the given ID, or None if not found.
        """
        return models_module.User.query.get(int(user_id))

    return app
