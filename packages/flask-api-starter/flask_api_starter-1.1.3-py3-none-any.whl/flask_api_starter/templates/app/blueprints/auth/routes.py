from flask import Blueprint, request, jsonify
from ...extensions import db
from ...models.user import User
from ...utils.token import generate_access_token, generate_refresh_token
from ...constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
import validators
from flask_jwt_extended import jwt_required, get_jwt_identity

# Create a blueprint for this route
auth_bp = Blueprint('auth', __name__, static_url_path='static/', url_prefix='/api/auth')

# Sign up route
@auth_bp.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")

        # Validate user input
        if not email or not password:
            return jsonify({"error": "Email and password required."}), HTTP_400_BAD_REQUEST
        
        # Validate the user email
        if not validators.email(email):
            return jsonify({"error": "Email is not valid."}), HTTP_400_BAD_REQUEST
        
        # Check if the user email is already registered
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({"error": "User already exists."}), HTTP_409_CONFLICT
        
        # Add user to the database
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully."}), HTTP_201_CREATED

# Login route
@auth_bp.route("/login", methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")
        # Get user by email
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Generate JWT access token and refresh token to authenticate user once logged in
            token = generate_access_token(user.id)
            refresh=generate_refresh_token(user.id)
            return jsonify({
                    "token": token,
                    "refresh": refresh
                }), HTTP_200_OK
        
        return jsonify({"error": "Invalid credentials"}), HTTP_401_UNAUTHORIZED

# Get current user profile route
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def current_user_profile():
    user_id = get_jwt_identity()

    user=User.query.filter_by(id=user_id).first()

    if user:
        return jsonify({
            'email': user.email
        }), HTTP_200_OK
    else:
        return jsonify({'error': 'User not found.'}), HTTP_404_NOT_FOUND

