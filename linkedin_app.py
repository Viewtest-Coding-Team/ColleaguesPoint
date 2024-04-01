from flask import Flask, redirect, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from jose import jwt, jwk
import logging
import os
import requests

# Initialize Flask application with detailed logging
linkedin_app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Configure SQLAlchemy database URI
database_uri = os.environ.get('DATABASE_URL')
if database_uri and database_uri.startswith("postgres://"):
    database_uri = database_uri.replace("postgres://", "postgresql://", 1)
linkedin_app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
linkedin_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(linkedin_app)

# LinkedIn authentication keys - using provided values
CLIENT_ID = '86xqm0tomtgsbm'
CLIENT_SECRET = 'BUiDCQT0mmGd5nnJ'
REDIRECT_URI = 'https://colleaguespoint.com/oops'

# Define User model for SQLAlchemy
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    picture_url = db.Column(db.String(255))  # For profile picture URL
    locale = db.Column(db.String(10))  # For user locale

    def __repr__(self):
        return f'<User {self.name}>'

# Ensure the database tables are created
with linkedin_app.app_context():
    db.create_all()

def get_jwks():
    jwks_uri = "https://www.linkedin.com/oauth/openid/jwks"
    response = requests.get(jwks_uri)
    response.raise_for_status()  # Verify successful response
    return response.json()

def validate_id_token(id_token):
    try:
        jwks = get_jwks()
        header = jwt.get_unverified_header(id_token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == header["kid"]:
                rsa_key = jwk.construct(key)
                break
        if not rsa_key:
            logging.error("Appropriate key not found for JWT validation.")
            return None
        
        payload = jwt.decode(
            id_token,
            rsa_key.to_dict(),
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer="https://www.linkedin.com"
        )
        return payload
    except Exception as e:
        logging.error(f"JWT validation error: {e}")
        return None

# Routes
@linkedin_app.route('/')
def home():
    logging.info("Redirecting to LinkedIn for authentication...")
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        "?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid%20profile%20email"
    )
    return redirect(auth_url)

@linkedin_app.route('/oops')
def linkedin_callback():
    code = request.args.get('code')
    if not code:
        logging.error("No authorization code provided by LinkedIn.")
        return jsonify(error="Authorization code not found"), 400
    
    logging.info("Authorization code received. Exchanging for access token...")
    try:
        access_token_response = requests.post(
            'https://www.linkedin.com/oauth/v2/accessToken',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        access_token_response.raise_for_status()  # Check for HTTP errors
        access_token = access_token_response.json().get('access_token')
        logging.info(f"Access token obtained: {access_token}")

        # Fetch user profile information
        logging.info("Retrieving user information...")
        userinfo_response = requests.get(
            'https://api.linkedin.com/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        userinfo_response.raise_for_status()  # Verify successful response
        userinfo_data = userinfo_response.json()
        logging.info(f"User info retrieved: {userinfo_data}")

        # Process and store user information
        process_and_store_user_info(userinfo_data)

        logging.info("User information processed and stored successfully.")
        return jsonify(success=True, message="User authenticated and information stored successfully."), 200
    except Exception as e:
        logging.error(f"Error during LinkedIn OAuth flow: {e}")
        return jsonify(error=str(e)), 500

def process_and_store_user_info(userinfo_data):
    # Extract necessary information
    name = f"{userinfo_data.get('given_name', '')} {userinfo_data.get('family_name', '')}".strip()
    email = userinfo_data.get('email')  # Adjust based on actual API response
    picture_url = userinfo_data.get('picture')  # Adjust based on actual API response
    locale = userinfo_data.get('locale')  # Adjust based on actual API response
    
    logging.info(f"Attempting to store/update user in the database: {email}")
    # Store or update user information in the database
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email, picture_url=picture_url, locale=locale)
        db.session.add(user)
        logging.info(f"New user created: {user}")
    else:
        user.name = name
        user.picture_url = picture_url
        user.locale = locale
        logging.info(f"Existing user updated: {user}")
    db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    linkedin_app.run(host='0.0.0.0', port=port, debug=True)
