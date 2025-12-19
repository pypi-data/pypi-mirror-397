from flask import Blueprint

api_bp = Blueprint("api", __name__, static_url_path='static/', url_prefix='/api')

# Create API routes here
