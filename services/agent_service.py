"""
Agent Service Layer

This module provides a clean interface to the LangGraph-based email agent.
It wraps the existing agent functionality for use in the web application.
"""

import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.agent import traige_email, create_draft_reply
from src.tools import format_email_for_llm, extract_email_parts
from src.gemini import llm_call
import json


class AgentService:
    """
    Service class for interacting with the email agent.
    Provides methods for triage, drafting, and learning.
    """
    
    @staticmethod
    def triage_email(sender: str, subject: str, body: str) -> dict:
        """
        Classify an email into IGNORE, NOTIFY, or RESPOND.
        
        Args:
            sender: Email sender
            subject: Email subject
            body: Email body
            
        Returns:
            dict with keys: category, confidence, reasoning
        """
        email_text = format_email_for_llm(sender, subject, body)
        
        try:
            # Call existing triage function
            category = traige_email(email_text).strip().replace('"', '').replace("'", "")
            
            return {
                'category': category,
                'confidence': 'high',  # Could be enhanced with confidence scoring
                'reasoning': f'Email classified as {category} based on content analysis'
            }
        except Exception as e:
            return {
                'category': 'ERROR',
                'confidence': 'low',
                'reasoning': f'Error during triage: {str(e)}'
            }
    
    @staticmethod
    def generate_draft(gmail_service, calendar_service, sender: str, 
                      subject: str, body: str, user_feedback: str = None) -> dict:
        """
        Generate a draft email response.
        
        Args:
            gmail_service: Gmail API service instance
            calendar_service: Calendar API service instance
            sender: Original sender
            subject: Original subject
            body: Original email body
            user_feedback: Optional feedback for refinement
            
        Returns:
            dict with draft details and calendar info
        """
        try:
            # Extract event time if present
            event_time = AgentService._extract_event_time(body)
            
            # Check calendar availability if event time exists
            calendar_status = None
            if event_time and event_time != "NONE":
                from src.tools import check_availability
                availability = check_availability(calendar_service, event_time)
                calendar_status = availability.get('status')
            
            # Generate draft using existing function
            # Note: This is simplified - the actual function uses interactive input
            # For web interface, we'll use a modified version
            draft_data = AgentService._generate_draft_noninteractive(
                sender, subject, body, calendar_status, user_feedback
            )
            
            return {
                'success': True,
                'draft': draft_data,
                'event_time': event_time,
                'calendar_status': calendar_status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def _extract_event_time(body: str) -> str:
        """Extract event time from email body using AI"""
        from datetime import datetime
        
        now = datetime.now()
        current_date_str = now.strftime("%A, %B %d, %Y")
        current_year = now.year
        
        time_prompt = f"""
        Context: Today is {current_date_str}.
        
        Task: Extract the event start time from the email below.
        - If a date (like "28 Jan") is mentioned without a year, assume the year is {current_year}.
        - Convert the time to ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
        - If NO specific time is found, return exactly 'NONE'.
        
        Email Body:
        "{body}"
        
        Return ONLY the ISO string or 'NONE'. No markdown, no quotes.
        """
        
        try:
            event_time = llm_call(time_prompt).strip().replace('"', '').replace("'", "")
            return event_time
        except:
            return "NONE"
    
    @staticmethod
    def _generate_draft_noninteractive(sender: str, subject: str, body: str, 
                                       calendar_status: str = None, 
                                       user_feedback: str = None) -> dict:
        """
        Generate email draft without interactive prompts (for web UI).
        """
        calendar_context = "No specific time mentioned in email."
        
        if calendar_status == "BUSY":
            calendar_context = "WARNING: You are BUSY at this time. Consider declining or suggesting alternative time."
        elif calendar_status == "FREE":
            calendar_context = "You are FREE at this time."
        
        feedback_context = ""
        if user_feedback:
            feedback_context = f"\n\nUser requested changes: {user_feedback}"
        
        prompt = f"""
        You are a professional Email Assistant.
        Your goal is to write a professional email reply.

        ### INPUT DATA:
        - Sender: {sender}
        - Original Subject: {subject}
        - Original Body: {body}

        ### CALENDAR CONTEXT:
        {calendar_context}
        
        ### USER FEEDBACK / ADJUSTMENTS:
        {feedback_context if feedback_context else "None (Draft the initial reply)"}

        ### GUIDELINES:
        1. **Tone:** Professional, direct, and polite.
        2. **Structure:** Greeting -> Main Point -> Call to Action -> Sign off.
        3. **Constraint:** Return strictly valid JSON.

        ### OUTPUT FORMAT (JSON ONLY):
        {{
            "To": "{sender}",
            "Subject": "Re: {subject}",
            "Body": "The full email body text here..."
        }}
        """
        
        try:
            response_json = llm_call(prompt)
            reply_data = json.loads(response_json)
            return reply_data
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "To": sender,
                "Subject": f"Re: {subject}",
                "Body": "Thank you for your email. I'll get back to you soon."
            }
    
    @staticmethod
    def get_email_summary(emails: list) -> str:
        """
        Generate a natural language summary of multiple emails.
        
        Args:
            emails: List of email dictionaries
            
        Returns:
            Natural language summary
        """
        if not emails:
            return "No emails found."
        
        email_summaries = []
        for email in emails[:5]:  # Limit to 5 for brevity
            sender = email.get('sender', 'Unknown')
            subject = email.get('subject', 'No subject')
            email_summaries.append(f"- From {sender}: {subject}")
        
        summary_text = "\n".join(email_summaries)
        
        prompt = f"""
        Summarize these recent emails in a friendly, concise paragraph:
        
        {summary_text}
        
        Focus on: who sent them, what they're about, and any action items.
        """
        
        try:
            return llm_call(prompt).strip()
        except:
            return f"You have {len(emails)} recent emails."
    
    @staticmethod
    def chat_with_agent(user_message: str, context: dict = None) -> str:
        """
        Process natural language commands from the chat interface.
        
        Args:
            user_message: User's chat message
            context: Optional context (user email, recent emails, etc.)
            
        Returns:
            Agent's response
        """
        # Build context for the AI
        context_str = ""
        if context:
            if 'user_email' in context:
                context_str += f"User: {context['user_email']}\n"
            if 'recent_emails' in context:
                context_str += f"Recent emails count: {len(context['recent_emails'])}\n"
        
        prompt = f"""
        You are an intelligent email assistant. The user says:
        
        "{user_message}"
        
        Context:
        {context_str if context_str else "No additional context"}
        
        Respond naturally and helpfully. If the user asks you to:
        - Summarize emails: Acknowledge and ask which emails
        - Draft a reply: Ask for the email they want to reply to
        - Check calendar: Acknowledge the request
        - Schedule a meeting: Ask for details
        
        Keep responses concise and actionable.
        """
        
        try:
            return llm_call(prompt).strip()
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again."
