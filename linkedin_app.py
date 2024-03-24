from flask import Flask, redirect, url_for, jsonify, request
import logging
import os
import psutil

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Function to log memory usage
def log_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    logging.info(f'Memory usage: {memory_info.rss} bytes')

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

    # Use the authorization code to fetch access token from LinkedIn
    try:
        logging.info('Fetching access token from LinkedIn')
        # Make a request to LinkedIn's token endpoint and handle the response
        # For example:
        # response = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data=data)
        # access_token = response.json().get('access_token')

        # Simplified response for debugging
        return jsonify(code=code), 200
    except Exception as e:
        logging.error(f'Error processing the LinkedIn callback: {e}')
        log_memory_usage()  # Log memory usage
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)
