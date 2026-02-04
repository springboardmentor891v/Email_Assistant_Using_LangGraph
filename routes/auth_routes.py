"""
Authentication Routes Blueprint

Handles Google OAuth 2.0 authentication flow.
"""

from flask import Blueprint, render_template, redirect, url_for, session, request
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.auth import get_gmail_service, get_calendar_service

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login')
def login():
    """
    Display login page with Google OAuth button.
    """
    # Clear any existing session
    session.clear()
    return render_template('login.html')


@auth_bp.route('/authenticate')
def authenticate():
    """
    Initiate Google OAuth 2.0 authentication flow.
    
    This will:
    1. Redirect to Google's OAuth consent screen
    2. User grants permissions
    3. Google redirects back to /auth/callback
    """
    try:
        # Initialize Gmail service (triggers OAuth flow)
        gmail_service = get_gmail_service()
        calendar_service = get_calendar_service()
        
        # Get user profile
        profile = gmail_service.users().getProfile(userId='me').execute()
        user_email = profile.get('emailAddress')
        
        # Store in session
        session['user_email'] = user_email
        session['user_name'] = user_email.split('@')[0].title()
        session['authenticated'] = True
        session.permanent = True
        
        # Store service instances in session (Note: In production, use token storage)
        # For simplicity, we'll re-instantiate services when needed
        session['oauth_completed'] = True
        
        return redirect(url_for('dashboard.home'))
    
    except Exception as e:
        print(f"Authentication error: {e}")
        return render_template('login.html', error="Authentication failed. Please try again.")


@auth_bp.route('/logout')
def logout():
    """
    Log out the user and clear session.
    """
    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/callback')
def callback():
    """
    OAuth callback endpoint (handled by google-auth-oauthlib).
    This route may not be explicitly called but is here for completeness.
    """
    return redirect(url_for('dashboard.home'))


def login_required(f):
    """
    Decorator to require authentication for routes.
    Usage: @login_required above route function
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    
    return decorated_function
