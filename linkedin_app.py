from flask import Flask, redirect, url_for, request
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

# Your LinkedIn application credentials should ideally be stored as environment variables
CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID', '86xqm0tomtgsbm')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET', 'BUiDCQT0mmGd5nnJ')
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
        logging.error('Authorization code not found')
        return 'Authorization code not found', 400
    
    logging.info(f'Received authorization code: {code}')

    try:
        token_response = requests.post(
            'https://www.linkedin.com/oauth/v2/accessToken',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
            }
        )
        token_response.raise_for_status()  # This will raise an exception for HTTP errors

        access_token = token_response.json().get('access_token')
        logging.info(f'Access Token: {access_token}')

        headers = {'Authorization': f'Bearer {access_token}'}
        profile_response = requests.get('https://api.linkedin.com/v2/me', headers=headers)
        profile_response.raise_for_status()  # This will raise an exception for HTTP errors

        profile_data = profile_response.json()
        logging.info(f'User Data: {profile_data}')

        name = profile_data.get('localizedFirstName') + ' ' + profile_data.get('localizedLastName')
        email = profile_data.get('emailAddress')  # Ensure your LinkedIn app has permissions and this field exists
        logging.info(f'Parsed User Name: {name}, Email: {email}')

        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        logging.info('User data saved successfully to the database')

    except requests.exceptions.RequestException as e:
        logging.error(f'Network or HTTP error occurred: {e}')
        return 'An error occurred while processing your request.', 500
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        db.session.rollback()
        return 'An internal error occurred.', 500

    return 'User data saved successfully!'

if __name__ == '__main__':
    # Check if LinkedIn credentials are set
    if not CLIENT_ID or not CLIENT_SECRET:
        raise Exception('LinkedIn credentials are not set')

    # Run the application
    linkedin_app.run(debug=True)
