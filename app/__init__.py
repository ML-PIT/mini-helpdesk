import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from config import config
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name=None):
    """Create Flask application with configuration"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize Sentry if configured
    if app.config.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[FlaskIntegration()]
        )
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    CORS(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Import models to ensure they are registered with SQLAlchemy
    from app.models import user, ticket, knowledge, audit
    
    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.tickets import bp as tickets_bp
    app.register_blueprint(tickets_bp, url_prefix='/tickets')
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.customer import bp as customer_bp
    app.register_blueprint(customer_bp, url_prefix='/customer')
    
    from app.knowledge import bp as knowledge_bp
    app.register_blueprint(knowledge_bp, url_prefix='/kb')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/helpdesk.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Helpdesk startup')
    
    # Create upload folder if it doesn't exist
    upload_folder = os.path.join(app.instance_path, app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_folder, exist_ok=True)
    
    # Initialize Claude integration
    try:
        from app.utils.claude import init_claude_integration
        init_claude_integration(app)
    except Exception as e:
        app.logger.warning(f"Failed to initialize Claude integration: {e}")
    
    # Add custom template filters
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to HTML line breaks"""
        if text is None:
            return ''
        import re
        text = str(text).replace('\n', '<br>')
        text = re.sub(r'\r\n?', '<br>', text)
        return text
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))