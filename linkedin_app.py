from flask import Flask, redirect, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import logging
import os
import requests

# Initialize Flask application
linkedin_app = Flask(__name__)

# Configure SQLAlchemy database URI
database_uri = os.environ.get('DATABASE_URL')
if database_uri.startswith("postgres://"):
    database_uri = database_uri.replace("postgres://", "postgresql://", 1)
linkedin_app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
linkedin_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(linkedin_app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# LinkedIn authentication keys
CLIENT_ID = os.environ.get('CLIENT_ID', '86xqm0tomtgsbm')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET', 'BUiDCQT0mmGd5nnJ')
REDIRECT_URI = os.environ.get('REDIRECT_URI', 'https://colleaguespoint.com/oops')

# Define User model for SQLAlchemy
class User(db.Model):
    __tablename__ = 'users'  # Specify the table name explicitly
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return f'<User {self.name}>'

# Ensure the database tables are created
with linkedin_app.app_context():
    db.create_all()

# Routes
@linkedin_app.route('/')
def home():
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
        return jsonify(error="Authorization code not found"), 400

    try:
        # Exchange code for access token
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
        access_token_response.raise_for_status()
        access_token = access_token_response.json().get('access_token')

        # Fetch user profile
        profile_response = requests.get(
            'https://api.linkedin.com/v2/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        profile_response.raise_for_status()
        profile_data = profile_response.json()

        # Fetch user email
        email_response = requests.get(
            'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        email_response.raise_for_status()
        email_data = email_response.json()
        email = email_data['elements'][0]['handle~']['emailAddress']

        # Save or update user in the database
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=profile_data['localizedFirstName'] + ' ' + profile_data.get('localizedLastName', ''), email=email)
        else:
            user.name = profile_data['localizedFirstName'] + ' ' + profile_data.get('localizedLastName', '')
        db.session.add(user)
        db.session.commit()

        return jsonify(success=True, name=user.name, email=user.email), 200
    except Exception as e:
        logging.error(f'LinkedIn OAuth flow failed: {e}')
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    linkedin_app.run(host='0.0.0.0', port=port, debug=True)  # Enable debug mode
