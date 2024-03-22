from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
import os

linkedin_app = Flask(__name__)
linkedin_app.config['SECRET_KEY'] = os.urandom(24)
linkedin_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///linkedin_users.db'
linkedin_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(linkedin_app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    linkedin_id = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    profile_picture = db.Column(db.String(120), nullable=True)  # Optional

    def __repr__(self):
        return f'<User {self.email}>'

# LinkedIn OAuth Settings
CLIENT_ID = '86xqm0tomtgsbm'
CLIENT_SECRET = 'BUiDCQT0mmGd5nnJ'
REDIRECT_URI = 'https://colleaguespoint.com/oops'

@linkedin_app.route('/')
def home():
    return 'Welcome to my Flask app! <a href="/login/linkedin">Login with LinkedIn</a>'

@linkedin_app.route('/login/linkedin')
def login_linkedin():
    auth_url = "https://www.linkedin.com/oauth/v2/authorization?response_type=code" + \
               f"&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}" + \
               "&scope=r_liteprofile%20r_emailaddress"
    return redirect(auth_url)

@linkedin_app.route('/oops')
def linkedin_callback():
    code = request.args.get('code')
    access_token = get_access_token(code)
    user_info = get_user_info(access_token)
    # Save or update user info in the database
    save_user(user_info)
    return 'LinkedIn login successful! User information has been saved.'

def get_access_token(code):
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
    return token_response.get('access_token')

def get_user_info(access_token):
    # Placeholder for LinkedIn API call to fetch user info
    # Return a dictionary with user info (e.g., LinkedIn ID, first name, last name, email, profile picture)
    return {}

def save_user(user_info):
    user = User.query.filter_by(linkedin_id=user_info['linkedin_id']).first()
    if not user:
        user = User(linkedin_id=user_info['linkedin_id'],
                    first_name=user_info['first_name'],
                    last_name=user_info['last_name'],
                    email=user_info['email'],
                    profile_picture=user_info.get('profile_picture'))
        db.session.add(user)
    else:
        # Update existing user info if needed
        pass
    db.session.commit()

if __name__ == '__main__':
    db.create_all()
    linkedin_app.run(debug=True)
