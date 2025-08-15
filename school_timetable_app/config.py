import os

# Base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration class."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Use a default, insecure key for development convenience
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-insecure'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app-dev.db')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

    @staticmethod
    def init_app(app):
        Config.init_app(app)
        # Log a warning if the secret key is not set in production
        if not os.environ.get('SECRET_KEY'):
            raise ValueError("SECRET_KEY environment variable is not set for production.")

# Dictionary to access config classes by name
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
