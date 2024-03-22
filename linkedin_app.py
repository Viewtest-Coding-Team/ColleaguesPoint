from flask import Flask, redirect, request, session, url_for
from requests_oauthlib import OAuth2Session
import os

# Your LinkedIn application credentials
CLIENT_ID = '86xqm0tomtgsbm'
CLIENT_SECRET = 'BUiDCQT0mmGd5nnJ'
# Ensure this redirect URI matches exactly what's registered in your LinkedIn app
REDIRECT_URI = 'https://colleaguespoint.com/oops'

# Flask application setup
linkedin_app = Flask(__name__)
linkedin_app.secret_key = os.urandom(24)

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

    return 'LinkedIn login successful!'

if __name__ == '__main__':
    linkedin_app.run(debug=True)
