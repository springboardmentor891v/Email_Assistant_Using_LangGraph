"""
Chat Routes Blueprint

Chatbot interface for natural language interaction with the email assistant.
"""

from flask import Blueprint, render_template, request, jsonify, session
import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from routes.auth_routes import login_required
from src.auth import get_gmail_service, get_calendar_service
from services.agent_service import AgentService
from services.gmail_service import GmailService
from services.calendar_service import CalendarService

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/')
@login_required
def chat_interface():
    """
    Display chat interface.
    """
    # Initialize chat history in session if not exists
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    return render_template('chat.html', chat_history=session.get('chat_history', []))


@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """
    Process user message and return agent response.
    
    Expected JSON payload:
    {
        "message": "user's message text"
    }
    
    Returns:
    {
        "success": true/false,
        "response": "agent's response",
        "actions": [list of suggested actions],
        "data": {additional data if needed}
    }
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'response': 'Please enter a message.'
            })
        
        # Get services
        gmail_service = get_gmail_service()
        calendar_service = get_calendar_service()
        
        # Build context for the agent
        context = {
            'user_email': session.get('user_email'),
            'recent_emails': GmailService.get_recent_emails(gmail_service, max_results=5)
        }
        
        # Process message based on intent
        response_data = process_chat_command(
            user_message, 
            gmail_service, 
            calendar_service,
            context
        )
        
        # Store in chat history
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        session['chat_history'].append({
            'role': 'user',
            'message': user_message
        })
        
        session['chat_history'].append({
            'role': 'assistant',
            'message': response_data['response'],
            'data': response_data.get('data')
        })
        
        # Keep only last 20 messages
        session['chat_history'] = session['chat_history'][-20:]
        session.modified = True
        
        return jsonify(response_data)
    
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            'success': False,
            'response': f'Sorry, I encountered an error: {str(e)}'
        })


def process_chat_command(message, gmail_service, calendar_service, context):
    """
    Process different types of chat commands.
    
    Returns structured response with actions and data.
    """
    message_lower = message.lower()
    
    # Check for specific command patterns
    if 'unread' in message_lower or 'how many' in message_lower:
        count = GmailService.get_unread_count(gmail_service)
        return {
            'success': True,
            'response': f'You have {count} unread emails.',
            'actions': ['view_emails'],
            'data': {'count': count}
        }
    
    elif 'summarize' in message_lower or 'summary' in message_lower:
        emails = GmailService.get_recent_emails(gmail_service, max_results=10)
        summary = AgentService.get_email_summary(emails)
        
        return {
            'success': True,
            'response': summary,
            'actions': ['view_emails'],
            'data': {'email_count': len(emails)}
        }
    
    elif 'calendar' in message_lower or 'meeting' in message_lower or 'schedule' in message_lower:
        events = CalendarService.get_upcoming_events(calendar_service, days_ahead=7)
        
        if not events:
            response = "You have no upcoming meetings in the next 7 days."
        else:
            event_list = []
            for event in events[:5]:
                formatted = CalendarService.format_event_for_display(event)
                event_list.append(f"- {formatted['title']} on {formatted['date']} at {formatted['time']}")
            
            response = f"You have {len(events)} upcoming meetings:\n\n" + "\n".join(event_list)
        
        return {
            'success': True,
            'response': response,
            'actions': ['view_calendar'],
            'data': {'events': events[:5]}
        }
    
    elif 'draft' in message_lower or 'reply' in message_lower or 'respond' in message_lower:
        recent_emails = GmailService.get_recent_emails(gmail_service, max_results=1)
        
        if not recent_emails:
            return {
                'success': True,
                'response': 'No recent emails found to reply to. Please specify which email you want to reply to.',
                'actions': []
            }
        
        email = recent_emails[0]
        response = f"I'll help you draft a reply to: **{email['subject']}** from {email['sender']}.\n\n"
        response += "Please use the 'Draft Reply' button in the email list to generate a full response."
        
        return {
            'success': True,
            'response': response,
            'actions': ['draft_reply'],
            'data': {'email_id': email['id']}
        }
    
    else:
        # General chat with AI
        ai_response = AgentService.chat_with_agent(message, context)
        
        return {
            'success': True,
            'response': ai_response,
            'actions': [],
            'data': None
        }


@chat_bp.route('/clear', methods=['POST'])
@login_required
def clear_chat():
    """
    Clear chat history.
    """
    session['chat_history'] = []
    session.modified = True
    
    return jsonify({
        'success': True,
        'message': 'Chat history cleared'
    })


@chat_bp.route('/draft-reply', methods=['POST'])
@login_required
def draft_reply():
    """
    Generate a draft reply for a specific email.
    
    Expected JSON:
    {
        "email_id": "...",
        "feedback": "optional user feedback"
    }
    """
    try:
        data = request.get_json()
        email_id = data.get('email_id')
        feedback = data.get('feedback', None)
        
        gmail_service = get_gmail_service()
        calendar_service = get_calendar_service()
        
        # Get the email
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
            return jsonify({
                'success': True,
                'draft': draft_result['draft'],
                'event_time': draft_result.get('event_time'),
                'calendar_status': draft_result.get('calendar_status')
            })
        else:
            return jsonify({
                'success': False,
                'error': draft_result.get('error', 'Unknown error')
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
