from flask import Flask, g, jsonify
from app.config import config_by_name
from app.db.connection import close_db_connection
from app.utils.logging import get_request_id, log_exception


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
    
    # Request Correlation ID Middleware
    @app.before_request
    def assign_request_correlation_id():
        get_request_id()

    # Register Blueprints
    from app.routes.views import views_bp
    from app.routes.auth import auth_bp
    from app.routes.students import students_bp
    from app.routes.allocations import allocations_bp
    from app.routes.finance import finance_bp
    from app.routes.visitors import visitors_bp
    from app.routes.complaints import complaints_bp
    from app.routes.maintenance import maintenance_bp
    from app.routes.reports import reports_bp
    
    app.register_blueprint(views_bp, url_prefix='')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(allocations_bp, url_prefix='/api/allocations')
    app.register_blueprint(finance_bp, url_prefix='/api/finance')
    app.register_blueprint(visitors_bp, url_prefix='/api/visitors')
    app.register_blueprint(complaints_bp, url_prefix='/api/complaints')
    app.register_blueprint(maintenance_bp, url_prefix='/api/maintenance')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')

    # Security Headers & Correlation Header Middleware
    @app.after_request
    def set_security_and_correlation_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if hasattr(g, 'request_id') and g.request_id:
            response.headers['X-Request-ID'] = g.request_id
        return response

    # Global Centralized Error Handlers
    @app.errorhandler(500)
    def handle_internal_server_error(e):
        log_exception("SERVER_INTERNAL_ERROR", exc_info=True)
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500

    @app.errorhandler(404)
    def handle_not_found_error(e):
        return jsonify({'status': 'error', 'message': 'Requested resource or API endpoint not found.'}), 404

    @app.errorhandler(403)
    def handle_forbidden_error(e):
        return jsonify({'status': 'error', 'message': 'Access forbidden: Insufficient permissions.'}), 403

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'service': 'HostelFlow API', 'version': '1.0.0'}, 200

    return app
