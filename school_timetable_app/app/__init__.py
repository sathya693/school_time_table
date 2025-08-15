from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    """
    Application factory function.
    Initializes the Flask app, configures it, and registers blueprints.
    """
    app = Flask(__name__)

    # Load configuration from the config object
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions with the app instance
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    # The routes are defined in app.routes, so we import and register the blueprint here.
    # This avoids circular import issues.
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
