from flask import Flask
from app.config import config_by_name
from app.db.connection import close_db_connection


def create_app(config_name='development'):
    """
    Flask Application Factory Pattern.
    Configures and returns the Flask application instance.
    """
    app = Flask(__name__)
    
    # Load environment configuration
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))
    
    # Register request teardown database cleanup
    app.teardown_appcontext(close_db_connection)
    
    # Register Blueprints
    from app.routes.students import students_bp
    from app.routes.allocations import allocations_bp
    
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(allocations_bp, url_prefix='/api/allocations')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'service': 'HostelFlow API', 'version': '1.0.0'}, 200

    return app
