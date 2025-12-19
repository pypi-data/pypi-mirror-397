from flask import Flask, jsonify, send_from_directory
from .config import get_config
from .extensions import db, migrate, jwt, cors
from .constants.http_status_codes import HTTP_429_TOO_MANY_REQUESTS, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_503_SERVICE_UNAVAILABLE, HTTP_401_UNAUTHORIZED, HTTP_422_UNPROCESSABLE_ENTITY
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import timedelta

# Swagger UI Setup for Documentation
# Read more at https://swagger.io/docs/specification/v3_0/about/
SWAGGER_URL = '/docs'
API_URL = '/static/swagger.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Placeholder for you app description here."}
)

# Read more on application factory pattern at https://flask.palletsprojects.com/en/stable/tutorial/factory/

def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    # Initialise Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # Initialise CORS with specific settings
    cors.init_app(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["<Live API URL>", "http://127.0.0.1:5000/"],
        "methods": ["GET", "POST", "OPTIONS", "DELETE", "PUT"],
        "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Configure JWT Token Expiration Time
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)    
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(hours=48) 
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 3600    # Recycle connections after 1 hour
    } 

    # Import Blueprints here to avoid circular imports
    from .blueprints.auth.routes import auth_bp
    from .blueprints.api.routes import api_bp

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # Initialise Swagger UI Blueprint
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Serve the Swagger YAML file
    @app.route('/static/swagger.yaml')
    def send_swagger():
        return send_from_directory('static', 'swagger.yaml')
    
    # Exception Handling | Catch Runtime Errors here
    # Read more on error handling at https://flask.palletsprojects.com/en/stable/errorhandling/
    
    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_file_not_found(error):
        return jsonify({'error': f"{HTTP_404_NOT_FOUND} File not found!"}), HTTP_404_NOT_FOUND
    
    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_internalServer_error(error):
        return jsonify({'error': "Something went wrong! Our team is working on it!"}), HTTP_500_INTERNAL_SERVER_ERROR
    
    @app.errorhandler(HTTP_503_SERVICE_UNAVAILABLE)
    def handle_connection_error(error):
        return jsonify({'error': "Service is currently unavailable. Our team is working on it!"}), HTTP_503_SERVICE_UNAVAILABLE
    
    @app.errorhandler(HTTP_429_TOO_MANY_REQUESTS)
    def handle_too_many_requests_error(error):
        return jsonify({'error': "Too many requests. Try again later!"}), HTTP_429_TOO_MANY_REQUESTS
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "Token expired.",
            "msg": "Invalid token."
        }), HTTP_401_UNAUTHORIZED
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "error": "Authorization required.",
            "msg": "Invalid token."
        }), HTTP_401_UNAUTHORIZED
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "error": "invalid_token.",
            "msg": "Invalid token."
        }), HTTP_422_UNPROCESSABLE_ENTITY
    
    # Kill inactive database sessions
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app
