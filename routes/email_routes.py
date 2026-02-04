"""
Email Routes Blueprint

Email list view, individual email details, and email actions.
"""

from flask import Blueprint, render_template, request, jsonify, session
import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from routes.auth_routes import login_required
from src.auth import get_gmail_service, get_calendar_service
from services.gmail_service import GmailService
from services.agent_service import AgentService

email_bp = Blueprint('emails', __name__)


@email_bp.route('/')
@login_required
def email_list():
    """
    Display list of emails with triage categories.
    """
    try:
        gmail_service = get_gmail_service()
        
        # Get filter from query params
        filter_type = request.args.get('filter', 'all')
        max_results = int(request.args.get('limit', 20))
        
        # Fetch emails based on filter
        if filter_type == 'unread':
            emails = GmailService.search_emails(gmail_service, 'is:unread', max_results)
        elif filter_type == 'starred':
            emails = GmailService.search_emails(gmail_service, 'is:starred', max_results)
        else:
            emails = GmailService.get_recent_emails(gmail_service, max_results)
        
        # Run triage on each email
        for email in emails:
            triage_result = AgentService.triage_email(
                email['sender'],
                email['subject'],
                email['body']
            )
            email['triage_category'] = triage_result['category']
            email['triage_confidence'] = triage_result['confidence']
        
        return render_template(
            'emails.html',
            emails=emails,
            filter_type=filter_type,
            total_count=len(emails)
        )
    
    except Exception as e:
        print(f"Email list error: {e}")
        return render_template(
            'emails.html',
            emails=[],
            error=f"Unable to load emails: {str(e)}"
        )


@email_bp.route('/<email_id>')
@login_required
def email_detail(email_id):
    """
    Display full email details and actions.
    """
    try:
        gmail_service = get_gmail_service()
        
        # Get email
        message = gmail_service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()
        
        from src.tools import extract_email_parts
        sender, subject, body = extract_email_parts(message)
        
        # Run triage
        triage_result = AgentService.triage_email(sender, subject, body)
        
        email_data = {
            'id': email_id,
            'sender': sender,
            'subject': subject,
            'body': body,
            'date': GmailService._get_email_date(message),
            'triage': triage_result
        }
        
        return render_template(
            'email_detail.html',
            email=email_data
        )
    
    except Exception as e:
        print(f"Email detail error: {e}")
        return render_template(
            'email_detail.html',
            error=f"Unable to load email: {str(e)}"
        )


@email_bp.route('/<email_id>/draft', methods=['POST'])
@login_required
def create_draft(email_id):
    """
    Generate draft reply for email (AJAX endpoint).
    """
    try:
        gmail_service = get_gmail_service()
        calendar_service = get_calendar_service()
        
        data = request.get_json()
        feedback = data.get('feedback', None)
        
        # Get email
        message = gmail_service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()
        
        from src.tools import extract_email_parts
        sender, subject, body = extract_email_parts(message)
        
        # Generate draft
        draft_result = AgentService.generate_draft(
            gmail_service,
            calendar_service,
            sender,
            subject,
            body,
            feedback
        )
        
        if draft_result['success']:
            # Store draft in session for approval
            if 'pending_drafts' not in session:
                session['pending_drafts'] = {}
            
            session['pending_drafts'][email_id] = draft_result['draft']
            session.modified = True
            
            return jsonify({
                'success': True,
                'draft': draft_result['draft'],
                'event_time': draft_result.get('event_time'),
                'calendar_status': draft_result.get('calendar_status')
            })
        else:
            return jsonify({
                'success': False,
                'error': draft_result.get('error')
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@email_bp.route('/<email_id>/send', methods=['POST'])
@login_required
def send_draft(email_id):
    """
    Send approved draft (Human-in-the-Loop approval step).
    """
    try:
        gmail_service = get_gmail_service()
        calendar_service = get_calendar_service()
        
        data = request.get_json()
        draft_data = data.get('draft')
        add_to_calendar = data.get('add_to_calendar', False)
        event_time = data.get('event_time')
        
        # Send email
        send_result = GmailService.send_email(
            gmail_service,
            draft_data['To'],
            draft_data['Subject'],
            draft_data['Body']
        )
        
        response = {
            'success': send_result['success'],
            'message': send_result['message']
        }
        
        # Add to calendar if requested
        if add_to_calendar and event_time:
            calendar_result = CalendarService.create_event(
                calendar_service,
                f"Meeting with {draft_data['To']}",
                event_time
            )
            response['calendar_added'] = calendar_result['success']
        
        # Clear from pending drafts
        if 'pending_drafts' in session and email_id in session['pending_drafts']:
            del session['pending_drafts'][email_id]
            session.modified = True
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error sending email: {str(e)}'
        })


@email_bp.route('/search', methods=['GET'])
@login_required
def search():
    """
    Search emails with Gmail query syntax.
    """
    try:
        gmail_service = get_gmail_service()
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'No search query provided'
            })
        
        results = GmailService.search_emails(gmail_service, query, max_results=20)
        
        # Run triage on results
        for email in results:
            triage_result = AgentService.triage_email(
                email['sender'],
                email['subject'],
                email.get('body', '')
            )
            email['triage_category'] = triage_result['category']
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })
