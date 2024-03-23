from flask import Flask, redirect, url_for, request
import requests
import os
from flask_sqlalchemy import SQLAlchemy
import logging

# Initialize Flask app
linkedin_app = Flask(__name__)
linkedin_app.secret_key = os.urandom(24)

# Configure SQLAlchemy to use the Heroku PostgreSQL database
db_uri = os.environ.get('DATABASE_URL')
if db_uri and db_uri.startswith('postgres://'):
    db_uri = db_uri.replace('postgres://', 'postgresql://', 1)

linkedin_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
linkedin_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(linkedin_app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Your LinkedIn application credentials
CLIENT_ID = '86xqm0tomtgsbm'
CLIENT_SECRET = 'BUiDCQT0mmGd5nnJ'
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
    
    logging.info('Received authorization code')

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
    if token_response.status_code == 200:
        logging.info('Access token retrieved successfully')
        access_token = token_response.json().get('access_token')
        logging.info(f'Access Token: {access_token}')
    else:
        logging.error(f'Failed to retrieve access token. Status code: {token_response.status_code}. Response: {token_response.text}')
        return 'Failed to retrieve access token', 500

    headers = {'Authorization': f'Bearer {access_token}'}
    profile_response = requests.get('https://api.linkedin.com/v2/me', headers=headers)

    if profile_response.status_code == 200:
        logging.info('User data fetched successfully from LinkedIn API')
        profile_data = profile_response.json()
        logging.info(f'User Data: {profile_data}')
    else:
        logging.error(f'Failed to fetch user data. Status code: {profile_response.status_code}. Response: {profile_response.text}')
        return 'Failed to fetch user data from LinkedIn API', 500

    name = profile_data.get('localizedFirstName') + ' ' + profile_data.get('localizedLastName')
    email = profile_data.get('emailAddress')
    
    logging.info(f'Parsed User Name: {name}, Email: {email}')

    # Create a new User object and save it to the database
    new_user = User(name=name, email=email)
    try:
        db.session.add(new_user)
        db.session.commit()
        logging.info('User data saved successfully to the database')
    except Exception as e:
        logging.error(f'Error saving user data to the database: {str(e)}')
        db.session.rollback()

    # Check if the new user is in the database
    all_users = User.query.all()
    logging.info(f'All users in the database: {all_users}')

    # Redirect to a success page or do further processing
    return 'User data saved successfully!'

if __name__ == '__main__':
    # Run the application
    linkedin_app.run(debug=True)
