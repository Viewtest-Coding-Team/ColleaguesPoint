from flask import Flask, request, redirect
import requests
import os

linkedin_app = Flask(__name__)
linkedin_app.secret_key = os.urandom(24)

# Your LinkedIn application credentials
CLIENT_ID = '86xqm0tomtgsbm'
CLIENT_SECRET = 'BUiDCQT0mmGd5nnJ'
# Ensure this redirect URI matches exactly what's registered in your LinkedIn app
REDIRECT_URI = 'https://colleaguespoint.com/oops'

@linkedin_app.route('/')
def home():
    return 'Welcome to my Flask app!'

@linkedin_app.route('/login/linkedin')
def login_linkedin():
    # Initiates the LinkedIn OAuth flow, requesting only openid and profile scopes
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        "?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid%20profile"  # Updated to exclude r_emailaddress scope
    )
    return redirect(auth_url)

@linkedin_app.route('/oops')
def linkedin_callback():
    # LinkedIn redirects back with a code
    code = request.args.get('code')
    
    # Exchange the code for an access token
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

    # Placeholder for further actions, e.g., fetching profile data
    # For now, just return a simple success message
    return 'LinkedIn login successful! Access token obtained.'

if __name__ == '__main__':
    linkedin_app.run(debug=True)
