from flask import Flask, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from requests_oauthlib import OAuth2Session
import os

# Your LinkedIn application credentials
CLIENT_ID = '86xqm0tomtgsbm'
CLIENT_SECRET = 'BUiDCQT0mmGd5nnJ'
# Ensure this redirect URI matches exactly what's registered in your LinkedIn app
REDIRECT_URI = 'https://colleaguespoint.com/oops'

# Ensure 'OAUTHLIB_INSECURE_TRANSPORT' is ONLY used for testing locally
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///linkedin_users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the User model
class LinkedInUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    linkedin_id = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)

db.create_all()

@app.route('/')
def home():
    return 'Welcome to my Flask app! <a href="/login/linkedin">Login with LinkedIn</a>'

@app.route('/login/linkedin')
def login_linkedin():
    linkedin = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    authorization_url, state = linkedin.authorization_url('https://www.linkedin.com/oauth/v2/authorization', scope=['r_liteprofile', 'r_emailaddress'])
    
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/oauth/linkedin/callback')
def linkedin_callback():
    linkedin = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, state=session['oauth_state'])
    token = linkedin.fetch_token('https://www.linkedin.com/oauth/v2/accessToken',
                                 client_secret=CLIENT_SECRET,
                                 authorization_response=request.url)
    
    # Assuming 'r_liteprofile' and 'r_emailaddress' scopes were requested
    linkedin_data = linkedin.get('https://api.linkedin.com/v2/me').json()
    email_data = linkedin.get('https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))').json()

    # Simplified example, adapt according to the actual data structure
    linkedin_id = linkedin_data['id']
    first_name = linkedin_data['localizedFirstName']
    last_name = linkedin_data['localizedLastName']
    email = email_data['elements'][0]['handle~']['emailAddress']
    profile_picture = None  # Adapt based on actual API response

    # Add user to the database
    user = LinkedInUser(linkedin_id=linkedin_id, first_name=first_name, last_name=last_name, email=email, profile_picture=profile_picture)
    db.session.add(user)
    db.session.commit()
    
    return 'LinkedIn login successful! User information stored.'

if __name__ == '__main__':
    app.run(debug=True)
