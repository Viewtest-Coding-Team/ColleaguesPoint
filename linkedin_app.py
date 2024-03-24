from flask import Flask, redirect, url_for, request, jsonify
import requests
import os
from flask_sqlalchemy import SQLAlchemy
import logging

# Initialize Flask app
linkedin_app = Flask(__name__)
linkedin_app.secret_key = os.urandom(24)

# Check for DATABASE_URL environment variable
db_uri = os.getenv('DATABASE_URL')
if not db_uri:
    raise Exception('DATABASE_URL is not set')
elif db_uri.startswith('postgres://'):
    db_uri = db_uri.replace('postgres://', 'postgresql://', 1)

linkedin_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
linkedin_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(linkedin_app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Your LinkedIn application credentials
CLIENT_ID = '86xqm0tomtgsbm'  # Consider moving to environment variables
CLIENT_SECRET = 'BUiDCQT0mmGd5nnJ'  # Consider moving to environment variables
REDIRECT_URI = 'https://colleaguespoint.com/oops'

# Define the User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return f'<User {self.name}>'

# Routes
@linkedin_app.route('/')
def home():
    logging.info('Redirecting to LinkedIn login')
    return redirect(url_for('login_linkedin'))

@linkedin_app.route('/login/linkedin')
def login_linkedin():
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        "?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid%20profile%20email"
    )
    logging.info(f'Redirecting to LinkedIn OAuth: {auth_url}')
    return redirect(auth_url)

@linkedin_app.route('/oops')
def linkedin_callback():
    code = request.args.get('code')
    if not code:
        error = "Authorization code not found"
        logging.error(error)
        return jsonify(error=error), 400

    logging.info(f'Received authorization code: {code}')

    # Use the authorization code to fetch access token from LinkedIn
    try:
        logging.info('Fetching access token from LinkedIn')
        # Make a request to LinkedIn's token endpoint and handle the response
        # For example:
        # response = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data=data)
        # access_token = response.json().get('access_token')

        # Simplified response for debugging
        return jsonify(code=code), 200
    except Exception as e:
        logging.error(f'Error processing the LinkedIn callback: {e}')
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    # Run the application
    linkedin_app.run(debug=True)
