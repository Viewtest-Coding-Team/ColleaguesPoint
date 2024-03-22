from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
import os

# Initialize Flask app
linkedin_app = Flask(__name__)
linkedin_app.secret_key = os.urandom(24)  # Generates a random key for session management

# Database configuration
linkedin_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///linkedin_users.db'
db = SQLAlchemy(linkedin_app)

# LinkedIn application credentials
CLIENT_ID = '86xqm0tomtgsbm'
CLIENT_SECRET = 'BUiDCQT0mmGd5nnJ'
REDIRECT_URI = 'https://colleaguespoint.com/oops'

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    linkedin_id = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

# Create tables
with linkedin_app.app_context():
    db.create_all()

# Routes
@linkedin_app.route('/')
def home():
    return 'Welcome to my Flask app! <a href="/login/linkedin">Login with LinkedIn</a>'

@linkedin_app.route('/login/linkedin')
def login_linkedin():
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
    token_response = requests.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    ).json()
    access_token = token_response.get('access_token')

    # Fetch user profile
    headers = {'Authorization': f'Bearer {access_token}'}
    profile_response = requests.get('https://api.linkedin.com/v2/me', headers=headers)
    email_response = requests.get('https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))', headers=headers)

    profile_data = profile_response.json()
    email_data = email_response.json()
    linkedin_id = profile_data.get('id')
    first_name = profile_data.get('localizedFirstName')
    last_name = profile_data.get('localizedLastName')
    email = email_data.get('elements')[0].get('handle~').get('emailAddress')

    # Save or update user in database
    user = User.query.filter_by(linkedin_id=linkedin_id).first()
    if user:
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
    else:
        user = User(linkedin_id=linkedin_id, first_name=first_name, last_name=last_name, email=email)
        db.session.add(user)
    db.session.commit()

    return f'LinkedIn login successful! Welcome, {first_name} {last_name} - {email}'

if __name__ == '__main__':
    linkedin_app.run(debug=True)
