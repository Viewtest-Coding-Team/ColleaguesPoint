from flask import Flask, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import requests

# Initialize Flask application
linkedin_app = Flask(__name__)
linkedin_app.secret_key = os.urandom(24)

# Database configuration
linkedin_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///linkedin_users.db'
linkedin_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(linkedin_app)

# Define the database model for storing LinkedIn user data
class LinkedInUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    linkedin_id = db.Column(db.String(120), unique=True, nullable=False)
    access_token = db.Column(db.String(255), nullable=False)

# Your LinkedIn application credentials
CLIENT_ID = '86xqm0tomtgsbm'
CLIENT_SECRET = 'BUiDCQT0mmGd5nnJ'
REDIRECT_URI = 'https://colleaguespoint.com/oops'

@linkedin_app.route('/')
def home():
    return 'Welcome to my Flask app! <a href="/login/linkedin">Login with LinkedIn</a>'

@linkedin_app.route('/login/linkedin')
def login_linkedin():
    # LinkedIn OAuth flow initiation
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        "?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=r_liteprofile%20r_emailaddress"
    )
    return redirect(auth_url)

@linkedin_app.route('/oops')
def linkedin_callback():
    # Exchange authorization code for access token
    code = request.args.get('code')
    token_response = requests.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        }
    ).json()
    
    access_token = token_response.get('access_token')
    
    # Placeholder: Extract LinkedIn ID from profile data
    # This is where you'd use the access token to request the user's LinkedIn profile data
    # and extract their LinkedIn ID or another unique identifier.
    linkedin_id = "example-linkedin-id"

    # Save or update user in the database
    user = LinkedInUser.query.filter_by(linkedin_id=linkedin_id).first()
    if user:
        user.access_token = access_token
    else:
        new_user = LinkedInUser(linkedin_id=linkedin_id, access_token=access_token)
        db.session.add(new_user)
    db.session.commit()

    return 'LinkedIn login successful! Access token obtained and user data saved.'

if __name__ == '__main__':
    db.create_all()  # Create database tables
    linkedin_app.run(debug=True)
