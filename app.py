"""
Flask Web Application for Email Assistant Using LangGraph

This is the main application entry point that configures Flask,
registers blueprints, and sets up session management.
"""

import os
from flask import Flask, redirect, url_for, session
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Import and register blueprints
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.chat_routes import chat_bp
from routes.email_routes import email_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(email_bp, url_prefix='/emails')


@app.route('/')
def index():
    """
    Root route - redirects to dashboard if authenticated, 
    otherwise redirects to login
    """
    if 'user_email' in session:
        return redirect(url_for('dashboard.home'))
    return redirect(url_for('auth.login'))


@app.context_processor
def inject_user():
    """
    Make user info available to all templates
    """
    return {
        'user_email': session.get('user_email'),
        'user_name': session.get('user_name', 'User')
    }


@app.errorhandler(404)
def not_found(error):
    """Custom 404 error handler"""
    return redirect(url_for('index'))


@app.errorhandler(500)
def server_error(error):
    """Custom 500 error handler"""
    return "Internal Server Error. Please try again later.", 500


if __name__ == '__main__':
    # Development server only - use gunicorn/waitress in production
    app.run(debug=True, host='0.0.0.0', port=5000)
