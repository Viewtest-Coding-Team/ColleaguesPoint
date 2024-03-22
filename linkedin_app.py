from flask import Flask, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from requests_oauthlib import OAuth2Session
import os

# Your LinkedIn application credentials and configuration
CLIENT_ID = '86xqm0tomtgsbm'
CLIENT_SECRET = 'BUiDCQT0mmGd5nnJ'
REDIRECT_URI = 'https://colleaguespoint.com/oops'

# Flask application setup
linkedin_app = Flask(__name__)
linkedin_app.secret_key = os.urandom(24)

# Database configuration
linkedin_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///linkedin_users.db'
linkedin_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(linkedin_app)

# Define the User model
class LinkedInUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    linkedin_id = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)

# Ensure the database is created
with linkedin_app.app_context():
    db.create_all()

# Route to home page
@linkedin_app.route('/')
def home():
    return 'Welcome to my Flask app! <a href="/login/linkedin">Login with LinkedIn</a>'

# Route to initiate LinkedIn OAuth flow
@linkedin_app.route('/login/linkedin')
def login_linkedin():
    linkedin = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    authorization_url, state = linkedin.authorization_url(
        'https://www.linkedin.com/oauth/v2/authorization', 
        scope=['r_liteprofile', 'r_emailaddress']
    )
    session['oauth_state'] = state
    return redirect(authorization_url)

# OAuth callback route
@linkedin_app.route('/oauth/linkedin/callback')
def linkedin_callback():
    linkedin = OAuth2Session(CLIENT_ID, state=session['oauth_state'], redirect_uri=REDIRECT_URI)
    token = linkedin.fetch_token(
        'https://www.linkedin.com/oauth/v2/accessToken',
        client_secret=CLIENT_SECRET,
        authorization_response=request.url
    )

    # Fetch user's profile information
    linkedin_data = linkedin.get('https://api.linkedin.com/v2/me').json()
    email_data = linkedin.get('https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))').json()

    linkedin_id = linkedin_data['id']
    first_name = linkedin_data.get('localizedFirstName', '')
    last_name = linkedin_data.get('localizedLastName', '')
    email = email_data['elements'][0]['handle~']['emailAddress'] if email_data['elements'] else ''

    # Check if user exists, if not, add to database
    user = LinkedInUser.query.filter_by(linkedin_id=linkedin_id).first()
    if not user:
        user = LinkedInUser(
            linkedin_id=linkedin_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            profile_picture=''
        )
        db.session.add(user)
        db.session.commit()

    return 'LinkedIn login successful! User information stored.'

if __name__ == '__main__':
    linkedin_app.run(debug=True)
