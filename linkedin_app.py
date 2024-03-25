from flask import Flask, redirect, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import logging
import os
import psutil
import requests

# Initialize Flask application
linkedin_app = Flask(__name__)

# Configure SQLAlchemy database URI
linkedin_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://u105vsqieobh9l:p881cc34100a964f3efba42cf20b4069bf230f6172a23c0f34310d1cc4c149d3a@cbbirn8v9855bl.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/dck0ia67alebo8'
linkedin_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(linkedin_app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define LinkedIn authentication keys
CLIENT_ID = "86xqm0tomtgsbm"
CLIENT_SECRET = "BUiDCQT0mmGd5nnJ"
REDIRECT_URI = "https://colleaguespoint.com/oops"

# Define User model for SQLAlchemy
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return f'<User {self.name}>'

# Function to log memory usage
def log_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    logging.info(f'Memory usage: {memory_info.rss} bytes')

# Routes
@linkedin_app.route('/')
def home():
    logging.info('Redirecting to LinkedIn login')
    log_memory_usage()  # Log memory usage
    return redirect(url_for('login_linkedin'))

@linkedin_app.route('/login/linkedin')
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

@linkedin_app.route('/oops')
def linkedin_callback():
    code = request.args.get('code')
    if not code:
        error = "Authorization code not found"
        logging.error(error)
        log_memory_usage()  # Log memory usage
        return jsonify(error=error), 400

    logging.info(f'Received authorization code: {code}')
    log_memory_usage()  # Log memory usage

    # Assuming you want to add the user to the database here
    # For example:
    # user = User(name='John Doe', email='john@example.com')
    # db.session.add(user)
    # db.session.commit()

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
    # Get the port from the environment variable PORT (used by Heroku)
    port = int(os.environ.get('PORT', 5001))
    # Run the Flask application
    linkedin_app.run(debug=True, port=port)
