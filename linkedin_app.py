from flask import Flask, request, redirect
import requests
import os

linkedin_app = Flask(__name__)
linkedin_app.secret_key = os.urandom(24)

CLIENT_ID = '86xqm0tomtgsbm'
CLIENT_SECRET = 'BUiDCQT0mmGd5nnJ'
REDIRECT_URI = 'https://colleaguespoint.com/oops'

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
        "&scope=r_liteprofile%20r_emailaddress"
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
    return f'LinkedIn login successful! Access token obtained: {access_token}'

if __name__ == '__main__':
    linkedin_app.run(debug=True)
