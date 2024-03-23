from flask import Flask, request, redirect, session, url_for
import requests
import os
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
linkedin_app = Flask(__name__)
linkedin_app.secret_key = os.urandom(24)

# Configure SQLAlchemy to use the Heroku PostgreSQL database
db_uri = os.environ.get('DATABASE_URL')
if db_uri.startswith('postgres://'):
    db_uri = db_uri.replace('postgres://', 'postgresql://', 1)

linkedin_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
linkedin_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(linkedin_app)

# Your LinkedIn application credentials
CLIENT_ID = '86xqm0tomtgsbm'
CLIENT_SECRET = 'BUiDCQT0mmGd5nnJ'
REDIRECT_URI = 'https://colleaguespoint.com/oops'
SCOPE = 'r_liteprofile'  # Scope for accessing basic profile info

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
    return redirect(url_for('login_linkedin'))

@linkedin_app.route('/login/linkedin')
def login_linkedin():
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        "?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE}"
    )
    return redirect(auth_url)

@linkedin_app.route('/oops')
def linkedin_callback():
    code = request.args.get('code')
    if code:
        # Exchange authorization code for access token
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
        access_token = token_response.json().get('access_token')
        # Now you have the access token, you can use it to fetch user data from LinkedIn API
        # For demonstration, let's just return the access token
        return f'Access token: {access_token}'
    else:
        return 'LinkedIn authorization failed'

if __name__ == '__main__':
    # Run the application
    linkedin_app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
