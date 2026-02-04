"""
Dashboard Routes Blueprint

Main dashboard showing email summaries, stats, and quick actions.
"""

from flask import Blueprint, render_template, session
import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from routes.auth_routes import login_required
from src.auth import get_gmail_service, get_calendar_service
from services.gmail_service import GmailService
from services.calendar_service import CalendarService
from services.agent_service import AgentService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def home():
    """
    Main dashboard view.
    Shows summary cards, statistics, and quick action buttons.
    """
    try:
        # Get service instances
        gmail_service = get_gmail_service()
        calendar_service = get_calendar_service()
        
        # Fetch dashboard data
        unread_count = GmailService.get_unread_count(gmail_service)
        recent_emails = GmailService.get_recent_emails(gmail_service, max_results=5)
        upcoming_events = CalendarService.get_upcoming_events(calendar_service, days_ahead=7, max_results=5)
        
        # Count emails requiring response (simplified - could use AI triage)
        # For now, we'll estimate based on unread emails in inbox
        respond_count = min(unread_count, 10)  # Placeholder logic
        
        # Get email categories
        categories = GmailService.get_email_categories(gmail_service)
        
        # Format events for display
        formatted_events = [
            CalendarService.format_event_for_display(event) 
            for event in upcoming_events
        ]
        
        # Get AI summary of recent emails
        email_summary = "No recent emails" if not recent_emails else None
        if recent_emails:
            email_summary = AgentService.get_email_summary(recent_emails)
        
        return render_template(
            'dashboard.html',
            unread_count=unread_count,
            respond_count=respond_count,
            upcoming_events_count=len(upcoming_events),
            recent_emails=recent_emails[:3],  # Show top 3
            upcoming_events=formatted_events[:3],  # Show top 3
            email_summary=email_summary,
            categories=categories
        )
    
    except Exception as e:
        print(f"Dashboard error: {e}")
        return render_template(
            'dashboard.html',
            error="Unable to load dashboard data. Please try again.",
            unread_count=0,
            respond_count=0,
            upcoming_events_count=0,
            recent_emails=[],
            upcoming_events=[],
            categories={}
        )


@dashboard_bp.route('/run-triage')
@login_required
def run_triage():
    """
    Run email triage on recent emails.
    Processes emails and categorizes them.
    """
    try:
        gmail_service = get_gmail_service()
        recent_emails = GmailService.get_recent_emails(gmail_service, max_results=10)
        
        triage_results = []
        for email in recent_emails:
            result = AgentService.triage_email(
                email['sender'],
                email['subject'],
                email['body']
            )
            
            triage_results.append({
                'email': email,
                'triage': result
            })
        
        return render_template(
            'triage_results.html',
            results=triage_results
        )
    
    except Exception as e:
        print(f"Triage error: {e}")
        return render_template(
            'dashboard.html',
            error=f"Triage failed: {str(e)}"
        )
