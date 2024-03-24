from flask import Flask, redirect, url_for, jsonify, request
import logging
import os
import psutil
import requests  # Added to make HTTP requests

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# LinkedIn authentication keys
CLIENT_ID = "86xqm0tomtgsbm"
CLIENT_SECRET = "BUiDCQT0mmGd5nnJ"
REDIRECT_URI = "https://colleaguespoint.com/oops"

# Function to log memory usage
def log_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    logging.info(f'Memory usage: {memory_info.rss} bytes')

# Function to exchange authorization code for access token
def get_access_token(code):
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    # Make a POST request to the token endpoint
    response = requests.post(token_url, data=data)

    # Parse the response JSON
    response_json = response.json()

    # Extract and return the access token
    access_token = response_json.get('access_token')
    return access_token

# Routes
@app.route('/')
def home():
    logging.info('Redirecting to LinkedIn login')
    log_memory_usage()  # Log memory usage
    return redirect(url_for('login_linkedin'))

@app.route('/login/linkedin')
def login_linkedin():
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        "?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid%20profile%20email"
    )
    logging.info(f'Redirecting to LinkedIn OAuth: {auth_url}')
    log_memory_usage()  # Log memory usage
    return redirect(auth_url)

@app.route('/oops')
def linkedin_callback():
    code = request.args.get('code')
    if not code:
        error = "Authorization code not found"
        logging.error(error)
        log_memory_usage()  # Log memory usage
        return jsonify(error=error), 400

    logging.info(f'Received authorization code: {code}')
    log_memory_usage()  # Log memory usage

    try:
        logging.info('Fetching access token from LinkedIn')
        access_token = get_access_token(code)
        return jsonify(access_token=access_token), 200
    except Exception as e:
        logging.error(f'Error processing the LinkedIn callback: {e}')
        log_memory_usage()  # Log memory usage
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)
